from typing import Optional

from cadr.skill_hub.client import SkillHubClient
from cadr.skill_hub.models import DailyMarketOverview, SkillHubCandidate


def discover_skill(client: SkillHubClient, query: str, unique_name: Optional[str] = None, top_k: int = 10) -> SkillHubCandidate:
    candidates = client.find_skill(query=query, top_k=top_k)
    if unique_name:
        for candidate in candidates:
            if candidate.unique_name == unique_name:
                return candidate
        raise ValueError(f"Skill '{unique_name}' was not found for query '{query}'.")

    if not candidates:
        raise ValueError(f"No Skill Hub candidates were returned for query '{query}'.")
    return candidates[0]


def run_daily_market_overview_preview(client: SkillHubClient) -> DailyMarketOverview:
    discover_skill(client, query="daily market overview", unique_name="daily_market_overview", top_k=10)
    result = client.execute_skill("daily_market_overview", {"preview": True})
    return DailyMarketOverview(
        skill_id=result.skill_id,
        timestamp=result.timestamp,
        status=result.data.get("status"),
        confidence=result.data.get("confidence"),
        summary=result.data.get("summary"),
        market_read=result.data.get("market_read", {}),
        macro_deep_read=result.data.get("macro_deep_read", {}),
        trader_assessment=result.data.get("trader_assessment", {}),
        decision_report=result.data.get("decision_report", {}),
        trader_readouts=result.data.get("trader_readouts", {}),
        watchlist=result.data.get("watchlist", []),
        signal_board=result.data.get("signal_board", {}),
        data_insights=result.data.get("data_insights", {}),
        coverage_diagnostics=result.data.get("coverage_diagnostics", {}),
        coverage_gap_index=result.data.get("coverage_gap_index"),
        enhancement_gaps=result.data.get("enhancement_gaps", []),
        next_research_actions=result.data.get("next_research_actions", []),
        risk_flags=result.data.get("risk_flags", []),
        missing_or_stale_inputs=result.data.get("missing_or_stale_inputs", []),
        action_guidance=result.data.get("action_guidance", {}),
        freshness_note=result.data.get("freshness_note"),
        output_budget=result.data.get("output_budget", {}),
    )
