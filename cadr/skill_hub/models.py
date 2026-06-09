from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SkillHubCandidate(BaseModel):
    unique_name: str
    skill_description: str
    result_type: Optional[str] = None
    domain: Optional[str] = None
    input_schema: Dict[str, Any] = Field(default_factory=dict)


class SkillHubExecutionResult(BaseModel):
    type: str
    skill_id: str
    timestamp: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    execution_meta: Dict[str, Any] = Field(default_factory=dict)


class DailyMarketOverview(BaseModel):
    skill_id: str
    timestamp: Optional[str] = None
    status: Optional[str] = None
    confidence: Optional[str] = None
    summary: Optional[str] = None
    market_read: Dict[str, Any] = Field(default_factory=dict)
    macro_deep_read: Dict[str, Any] = Field(default_factory=dict)
    trader_assessment: Any = Field(default_factory=dict)
    decision_report: Any = Field(default_factory=dict)
    trader_readouts: Any = Field(default_factory=list)
    watchlist: Any = Field(default_factory=list)
    signal_board: Any = Field(default_factory=list)
    data_insights: Any = Field(default_factory=list)
    coverage_diagnostics: Any = Field(default_factory=list)
    coverage_gap_index: Any = None
    enhancement_gaps: Any = Field(default_factory=list)
    next_research_actions: Any = Field(default_factory=list)
    risk_flags: Any = Field(default_factory=list)
    missing_or_stale_inputs: Any = Field(default_factory=list)
    action_guidance: Any = Field(default_factory=dict)
    freshness_note: Optional[str] = None
    output_budget: Any = Field(default_factory=dict)
