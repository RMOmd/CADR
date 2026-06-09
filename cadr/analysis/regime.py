from enum import Enum
from cadr.data.models import GlobalMetrics, FearGreedEntry

class MarketRegime(Enum):
    RISK_ON = "risk_on"
    RISK_OFF = "risk_off"
    CRISIS = "crisis"
    NEUTRAL = "neutral"

def classify_regime(global_metrics: GlobalMetrics, fear_greed: FearGreedEntry = None) -> MarketRegime:
    """
    Classify the current market regime based on available metrics.
    A simple heuristic:
    - F&G > 60 -> Risk On
    - F&G < 30 -> Risk Off
    - F&G < 20 -> Crisis
    - Otherwise Neutral
    """
    if fear_greed:
        fg_val = fear_greed.value
        if fg_val < 20:
            return MarketRegime.CRISIS
        elif fg_val < 40:
            return MarketRegime.RISK_OFF
        elif fg_val > 60:
            return MarketRegime.RISK_ON
            
    # Fallback to neutral if no clear signal
    return MarketRegime.NEUTRAL
