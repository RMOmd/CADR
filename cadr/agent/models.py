from typing import List, Optional

from pydantic import BaseModel, Field


class AssetContext(BaseModel):
    id: int
    symbol: str
    name: Optional[str] = None
    price: float
    market_cap: float = 0.0
    volume_24h: float = 0.0
    percent_change_1h: float = 0.0
    percent_change_24h: float = 0.0
    percent_change_7d: float = 0.0
    percent_change_30d: float = 0.0
    rsi: Optional[float] = None
    macd_signal: Optional[str] = None
    thesis_tags: List[str] = Field(default_factory=list)
    latest_news: List[str] = Field(default_factory=list)
    source: str = "cmc_agent_hub"


class MarketContextSnapshot(BaseModel):
    btc_dominance: float
    eth_dominance: float
    total_market_cap: float = 0.0
    total_volume_24h: Optional[float] = None
    altcoin_season_index: Optional[float] = None
    fear_greed_index: Optional[float] = None
    marketcap_rsi: Optional[float] = None
    marketcap_macd_signal: Optional[str] = None
    open_interest_change_24h: Optional[float] = None
    funding_bias: Optional[str] = None
    trending_narratives: List[str] = Field(default_factory=list)
    macro_events: List[str] = Field(default_factory=list)
    source: str = "cmc_agent_hub"
