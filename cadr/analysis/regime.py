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
    Heuristic combines sentiment and BTC dominance:
    - Very weak sentiment or extreme dominance -> Crisis
    - Weak sentiment or elevated dominance -> Risk Off
    - Strong sentiment with contained dominance -> Risk On
    - Otherwise Neutral
    """
    btc_dominance = global_metrics.btc_dominance

    if fear_greed:
        fg_val = fear_greed.value
        if fg_val < 20 or (fg_val < 30 and btc_dominance >= 64):
            return MarketRegime.CRISIS
        elif fg_val < 40 or btc_dominance >= 60:
            return MarketRegime.RISK_OFF
        elif fg_val > 60 and btc_dominance <= 55:
            return MarketRegime.RISK_ON

    if btc_dominance >= 64:
        return MarketRegime.CRISIS
    if btc_dominance >= 60:
        return MarketRegime.RISK_OFF
    if btc_dominance <= 53:
        return MarketRegime.RISK_ON

    return MarketRegime.NEUTRAL
