from datetime import datetime

from cadr.analysis.regime import MarketRegime, classify_regime
from cadr.data.models import FearGreedEntry, GlobalMetrics


def make_global_metrics(btc_dominance: float) -> GlobalMetrics:
    return GlobalMetrics(
        total_market_cap=1_000_000_000.0,
        btc_dominance=btc_dominance,
        eth_dominance=18.0
    )


def make_fear_greed(value: float) -> FearGreedEntry:
    return FearGreedEntry(
        timestamp=datetime(2024, 1, 1),
        value=value,
        classification="test"
    )


def test_classify_regime_risk_on_when_sentiment_strong_and_dominance_contained():
    regime = classify_regime(make_global_metrics(52.0), make_fear_greed(72.0))
    assert regime == MarketRegime.RISK_ON


def test_classify_regime_risk_off_when_dominance_is_high_even_with_good_sentiment():
    regime = classify_regime(make_global_metrics(61.0), make_fear_greed(70.0))
    assert regime == MarketRegime.RISK_OFF


def test_classify_regime_crisis_without_sentiment_when_dominance_is_extreme():
    regime = classify_regime(make_global_metrics(65.0), None)
    assert regime == MarketRegime.CRISIS
