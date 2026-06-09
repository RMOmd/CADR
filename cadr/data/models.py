from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class OHLCVBar(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class AssetQuote(BaseModel):
    id: int
    symbol: str
    price: float
    market_cap: float
    volume_24h: float
    percent_change_1h: float
    percent_change_24h: float
    percent_change_7d: float
    percent_change_30d: float

class GlobalMetrics(BaseModel):
    total_market_cap: float
    btc_dominance: float
    eth_dominance: float
    altcoin_season_index: Optional[float] = None
    fear_greed_index: Optional[float] = None

class FearGreedEntry(BaseModel):
    timestamp: datetime
    value: float
    classification: str

class DivergenceSignal(BaseModel):
    asset_a: str
    asset_b: str
    z_score: float
    direction: str # "long_a_short_b" or "long_b_short_a"
    conviction_score: int # 1 to 5
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StrategySpec(BaseModel):
    skill: str = "cadr"
    version: str = "1.0.0"
    generated_at: str
    strategy: Dict[str, Any]
    analysis: Dict[str, Any]
    rules: Dict[str, str]
    risk_management: Dict[str, Any]
    backtest_results: Optional[Dict[str, Any]] = None
    market_context: Dict[str, Any]

class BacktestResult(BaseModel):
    period: str
    total_trades: int
    win_rate: float
    avg_profit_per_trade_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    profit_factor: float
    calmar_ratio: float
