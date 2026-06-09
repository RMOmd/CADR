import json
from typing import Any, Dict, List, Optional

import requests

import cadr.config as cfg
from cadr.skill_hub.models import SkillHubCandidate, SkillHubExecutionResult


class SkillHubError(RuntimeError):
    """Raised when the CoinMarketCap Skill Hub returns a transport or MCP error."""


def _extract_event_payload(raw_text: str) -> Dict[str, Any]:
    stripped = raw_text.strip()
    if not stripped:
        raise SkillHubError("CMC Skill Hub returned an empty response.")

    if stripped.startswith("{"):
        return json.loads(stripped)

    data_lines = []
    for line in stripped.splitlines():
        if line.startswith("data:"):
            data_lines.append(line[len("data:"):].strip())

    if not data_lines:
        raise SkillHubError("CMC Skill Hub response did not contain any data payload.")

    return json.loads("\n".join(data_lines))


def _parse_embedded_json(content: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not content:
        return {}

    first = content[0]
    if first.get("type") != "text":
        raise SkillHubError(f"Unsupported Skill Hub content type: {first.get('type')}")

    text = first.get("text", "")
    if not text:
        return {}
    return json.loads(text)


def _normalize_execution_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    result_block = payload.get("result", payload)

    if isinstance(result_block, dict) and "output" in result_block and isinstance(result_block["output"], str):
        try:
            nested = json.loads(result_block["output"])
        except json.JSONDecodeError as exc:
            raise SkillHubError(f"Could not decode nested Skill Hub output JSON: {exc}") from exc

        normalized = nested.get("result", nested)
        if isinstance(normalized, dict):
            normalized["_execution_meta"] = {
                "success": result_block.get("success"),
                "exit_code": result_block.get("exitCode"),
                "error": result_block.get("error"),
                "skill": nested.get("skill"),
            }
        return normalized

    return result_block


def _coerce_execution_result_shape(execution_result: Dict[str, Any]) -> Dict[str, Any]:
    if "type" in execution_result and "skill_id" in execution_result:
        return execution_result

    nested = execution_result.get("result")
    if isinstance(nested, dict) and "type" in nested and "skill_id" in nested:
        merged = dict(nested)
        if "_execution_meta" in execution_result:
            merged["_execution_meta"] = execution_result["_execution_meta"]
        return merged

    output = execution_result.get("output")
    if isinstance(output, dict) and "type" in output and "skill_id" in output:
        merged = dict(output)
        if "_execution_meta" in execution_result:
            merged["_execution_meta"] = execution_result["_execution_meta"]
        return merged

    raise SkillHubError(
        "CMC Skill Hub returned an execution payload without the expected type/skill_id fields. "
        f"Available keys: {sorted(execution_result.keys())}"
    )


class SkillHubClient:
    """Minimal JSON-RPC client for CoinMarketCap Skill Hub over streamable HTTP."""

    def __init__(
        self,
        api_key: Optional[str] = cfg.CMC_SKILL_HUB_API_KEY,
        base_url: str = cfg.CMC_SKILL_HUB_URL,
        tool_timeout_sec: int = cfg.CMC_SKILL_HUB_TOOL_TIMEOUT_SEC,
    ):
        if not api_key:
            raise ValueError("CMC_SKILL_HUB_API_KEY is required to use the Skill Hub client.")

        self.api_key = api_key
        self.base_url = base_url
        self.tool_timeout_sec = tool_timeout_sec
        self.session = requests.Session()
        self.session.headers.update({
            "X-CMC-MCP-API-KEY": self.api_key,
            "Accept": "application/json, text/event-stream",
        })
        self._initialized = False
        self._next_id = 1
        self.server_info: Dict[str, Any] = {}

    def _post(self, method: str, params: Dict[str, Any], timeout: Optional[int] = None) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id,
            "method": method,
            "params": params,
        }
        self._next_id += 1

        response = self.session.post(
            self.base_url,
            json=payload,
            timeout=timeout or self.tool_timeout_sec,
        )
        response.raise_for_status()
        message = _extract_event_payload(response.text)

        if "error" in message:
            error = message["error"]
            raise SkillHubError(f"CMC Skill Hub error {error.get('code')}: {error.get('message')}")

        return message.get("result", {})

    def initialize(self) -> Dict[str, Any]:
        if self._initialized:
            return self.server_info

        result = self._post(
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "cadr-skill-hub-client", "version": "1.0.0"},
            },
            timeout=30,
        )
        self.server_info = result.get("serverInfo", {})
        self._initialized = True

        # Best-effort initialization notification; server currently accepts stateless calls.
        try:
            self.session.post(
                self.base_url,
                json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
                timeout=15,
            )
        except requests.RequestException:
            pass

        return self.server_info

    def list_tools(self) -> List[str]:
        self.initialize()
        result = self._post("tools/list", {}, timeout=30)
        return [tool.get("name") for tool in result.get("tools", [])]

    def find_skill(self, query: str, top_k: int = 5) -> List[SkillHubCandidate]:
        self.initialize()
        result = self._post(
            "tools/call",
            {
                "name": "find_skill",
                "arguments": {"query": query, "top_k": top_k},
            },
        )
        payload = _parse_embedded_json(result.get("content", []))
        candidates = []
        for item in payload.get("candidates", []):
            candidates.append(SkillHubCandidate(
                unique_name=item["uniqueName"],
                skill_description=item.get("skillDescription", ""),
                result_type=item.get("resultType"),
                domain=item.get("domain"),
                input_schema=item.get("inputSchema", {}),
            ))
        return candidates

    def execute_skill(self, unique_name: str, parameters: Dict[str, Any]) -> SkillHubExecutionResult:
        self.initialize()
        result = self._post(
            "tools/call",
            {
                "name": "execute_skill",
                "arguments": {
                    "unique_name": unique_name,
                    "parameters": parameters,
                },
            },
        )
        payload = _parse_embedded_json(result.get("content", []))
        execution_result = _coerce_execution_result_shape(_normalize_execution_payload(payload))
        execution_meta = execution_result.pop("_execution_meta", {}) if isinstance(execution_result, dict) else {}
        return SkillHubExecutionResult(
            type=execution_result["type"],
            skill_id=execution_result["skill_id"],
            timestamp=execution_result.get("timestamp"),
            data=execution_result.get("data", {}),
            execution_meta=execution_meta,
        )
