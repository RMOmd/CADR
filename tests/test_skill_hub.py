import json
import pandas as pd

from cadr.data.models import FearGreedEntry, GlobalMetrics
from cadr.skill_hub import (
    SkillHubClient,
    discover_skill,
    generate_cadr_strategy_from_skill_hub,
    run_daily_market_overview_preview,
)


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def _event(payload):
    return "event:message\ndata:" + json.dumps(payload)


def test_skill_hub_client_discovers_and_executes_daily_market_overview(monkeypatch):
    calls = []

    def fake_post(url, json=None, timeout=None, **kwargs):
        calls.append((json["method"], json.get("params", {})))

        if json["method"] == "initialize":
            return FakeResponse(_event({
                "jsonrpc": "2.0",
                "id": json["id"],
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {"tools": {"listChanged": True}},
                    "serverInfo": {"name": "crypto-skill-hub", "version": "1.0.0"},
                },
            }))

        if json["method"] == "notifications/initialized":
            return FakeResponse("", status_code=202)

        if json["method"] == "tools/call" and json["params"]["name"] == "find_skill":
            return FakeResponse(_event({
                "jsonrpc": "2.0",
                "id": json["id"],
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json_module.dumps({
                            "candidates": [{
                                "uniqueName": "daily_market_overview",
                                "skillDescription": "Daily market read",
                                "resultType": "evidence_pack",
                                "domain": "research",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {"preview": {"type": "boolean"}},
                                    "required": ["preview"],
                                },
                            }]
                        })
                    }]
                },
            }))

        if json["method"] == "tools/call" and json["params"]["name"] == "execute_skill":
            return FakeResponse(_event({
                "jsonrpc": "2.0",
                "id": json["id"],
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json_module.dumps({
                            "result": {
                                "type": "evidence_pack",
                                "skill_id": "daily_market_overview",
                                "timestamp": "2026-06-09T16:36:16.852462+00:00",
                                "data": {
                                    "status": "partial",
                                    "confidence": "medium",
                                    "summary": "Overview summary",
                                    "market_read": {"regime": "headwind_tightening"},
                                    "macro_deep_read": {"macro_news": {"verdict": "mixed"}},
                                    "risk_flags": ["test"],
                                },
                            }
                        })
                    }]
                },
            }))

        raise AssertionError(f"Unexpected request: {json}")

    json_module = json
    client = SkillHubClient(api_key="test-key")
    monkeypatch.setattr(client.session, "post", fake_post)

    candidate = discover_skill(client, "daily market overview", unique_name="daily_market_overview", top_k=10)
    overview = run_daily_market_overview_preview(client)

    assert candidate.unique_name == "daily_market_overview"
    assert candidate.input_schema["required"] == ["preview"]
    assert overview.skill_id == "daily_market_overview"
    assert overview.status == "partial"
    assert overview.market_read["regime"] == "headwind_tightening"
    assert overview.macro_deep_read["macro_news"]["verdict"] == "mixed"
    assert calls[0][0] == "initialize"


def test_skill_hub_client_normalizes_nested_output_payload(monkeypatch):
    def fake_post(url, json=None, timeout=None, **kwargs):
        if json["method"] == "initialize":
            return FakeResponse(_event({
                "jsonrpc": "2.0",
                "id": json["id"],
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {"tools": {"listChanged": True}},
                    "serverInfo": {"name": "crypto-skill-hub", "version": "1.0.0"},
                },
            }))
        if json["method"] == "notifications/initialized":
            return FakeResponse("", status_code=202)
        if json["method"] == "tools/call":
            return FakeResponse(_event({
                "jsonrpc": "2.0",
                "id": json["id"],
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json_module.dumps({
                            "result": {
                                "error": "",
                                "exitCode": 0,
                                "success": True,
                                "output": json_module.dumps({
                                    "skill": "analyze_cross_asset_performance_divergence",
                                    "result": {
                                        "type": "evidence_pack",
                                        "skill_id": "analyze_cross_asset_performance_divergence",
                                        "timestamp": "2026-06-09T00:00:00Z",
                                        "data": {"status": "ok", "summary": "Nested payload works"},
                                    },
                                }),
                            }
                        })
                    }]
                },
            }))
        raise AssertionError(f"Unexpected request: {json}")

    json_module = json
    client = SkillHubClient(api_key="test-key")
    monkeypatch.setattr(client.session, "post", fake_post)

    result = client.execute_skill("analyze_cross_asset_performance_divergence", {"base_asset": "BTC", "quote_assets": []})

    assert result.skill_id == "analyze_cross_asset_performance_divergence"
    assert result.data["summary"] == "Nested payload works"
    assert result.execution_meta["success"] is True


def test_skill_hub_client_accepts_result_nested_one_level_deeper(monkeypatch):
    json_module = json

    def fake_post(url, json=None, timeout=None, **kwargs):
        if json["method"] == "initialize":
            return FakeResponse(_event({
                "jsonrpc": "2.0",
                "id": json["id"],
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {"tools": {"listChanged": True}},
                    "serverInfo": {"name": "crypto-skill-hub", "version": "1.0.0"},
                },
            }))
        if json["method"] == "notifications/initialized":
            return FakeResponse("", status_code=202)
        if json["method"] == "tools/call":
            return FakeResponse(_event({
                "jsonrpc": "2.0",
                "id": json["id"],
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json_module.dumps({
                            "result": {
                                "result": {
                                    "type": "evidence_pack",
                                    "skill_id": "weird_nested_skill",
                                    "timestamp": "2026-06-09T00:00:00Z",
                                    "data": {"status": "ok"},
                                }
                            }
                        })
                    }]
                },
            }))
        raise AssertionError(f"Unexpected request: {json}")

    client = SkillHubClient(api_key="test-key")
    monkeypatch.setattr(client.session, "post", fake_post)

    result = client.execute_skill("weird_nested_skill", {})

    assert result.skill_id == "weird_nested_skill"
    assert result.type == "evidence_pack"


def test_generate_cadr_strategy_from_skill_hub_builds_backtestable_spec():
    class FakeSkillHubClient:
        def execute_skill(self, unique_name, parameters):
            if unique_name == "analyze_cross_asset_performance_divergence":
                chart_points = []
                for i, dt in enumerate(pd.date_range("2026-05-01", periods=45, freq="D")):
                    chart_points.append({
                        "date": dt.strftime("%Y-%m-%d"),
                        "BTC": 100.0 + (i * 0.4),
                        "ETH": 100.0 + (i * 0.1) + (5 if i > 34 else 0),
                    })
                return type("SkillResult", (), {
                    "skill_id": unique_name,
                    "data": {
                        "status": "ok",
                        "summary": "BTC is diverging from ETH",
                        "business_decision": "Use as context",
                        "data_quality": {"aligned_days": 45},
                        "decision_basis": ["Sample basis"],
                        "risk_notes": ["Sample risk"],
                        "report": {
                            "chart_points": chart_points,
                            "divergence_state": "base_outperforming",
                            "base_vs_peer_average_return_pct": 4.2,
                            "correlation_to_base": {"ETH": 0.82},
                            "asset_summaries": {"BTC": {}, "ETH": {}},
                        },
                    },
                })()
            if unique_name == "daily_market_overview":
                return type("SkillResult", (), {
                    "skill_id": unique_name,
                    "timestamp": "2026-06-09T00:00:00Z",
                    "data": {
                        "status": "partial",
                        "confidence": "medium",
                        "summary": "Macro context available",
                        "market_read": {
                            "regime": "headwind_tightening",
                            "risk_bias": "defensive_research_only",
                        },
                    },
                })()
            raise AssertionError(unique_name)

        def find_skill(self, query, top_k=10):
            return [type("Candidate", (), {"unique_name": "daily_market_overview"})()]

    class FakeCMCClient:
        def get_global_metrics(self):
            return GlobalMetrics(
                total_market_cap=2_500_000_000_000.0,
                btc_dominance=58.0,
                eth_dominance=10.0,
            )

        def get_fear_greed(self):
            return FearGreedEntry(
                timestamp="2026-06-09T00:00:00Z",  # pydantic coercion is fine for this fixture
                value=42.0,
                classification="Neutral",
            )

    spec = generate_cadr_strategy_from_skill_hub(
        base_asset="BTC",
        quote_assets=["ETH"],
        lookback_days=90,
        skill_hub_client=FakeSkillHubClient(),
        cmc_client=FakeCMCClient(),
    )

    assert spec.strategy["execution_style"] == "cadr_skill_hub_pair_mean_reversion"
    assert spec.analysis["signal_method"] == "skill_hub_chart_points_plus_local_mean_reversion"
    assert spec.analysis["skill_hub_pair_context"]["divergence_state"] == "base_outperforming"
    assert spec.market_context["skill_hub"]["daily_market_overview"]["status"] == "partial"


def test_fallback_signal_supports_base_lagging_and_broadly_tracking():
    from cadr.skill_hub.cadr_pipeline import _fallback_signal_from_skill_hub_report

    lagging = _fallback_signal_from_skill_hub_report("ETH", "BNB", {
        "divergence_state": "base_lagging",
        "base_vs_peer_average_return_pct": -9.9651,
        "correlation_to_base": {"BNB": 0.69},
    })
    tracking = _fallback_signal_from_skill_hub_report("BTC", "BNB", {
        "divergence_state": "broadly_tracking",
        "base_vs_peer_average_return_pct": -2.4817,
        "correlation_to_base": {"BNB": 0.73},
    })

    assert lagging.direction == "long_ETH_short_BNB"
    assert tracking.direction == "long_BTC_short_BNB"
