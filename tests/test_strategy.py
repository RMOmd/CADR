import pandas as pd

import cadr.config as cfg
from cadr.analysis.regime import MarketRegime
from cadr.backtest.engine import run_backtest
from cadr.data.models import DivergenceSignal
from cadr.strategy.generator import generate_strategy


def test_generate_strategy_embeds_thresholds_for_downstream_consumers():
    signal = DivergenceSignal(
        asset_a="AAA",
        asset_b="BBB",
        z_score=-2.8,
        direction="long_AAA_short_BBB",
        conviction_score=4,
        metadata={"correlation_breakdown": True}
    )

    spec = generate_strategy(
        [signal],
        MarketRegime.NEUTRAL,
        {"btc_dominance": 55.0, "fear_greed_index": 50, "regime": "neutral"}
    )

    assert spec.analysis["thresholds"]["entry_zscore"] == cfg.Z_SCORE_ENTRY_THRESHOLD
    assert spec.analysis["thresholds"]["exit_zscore"] == cfg.Z_SCORE_EXIT_THRESHOLD
    assert spec.analysis["thresholds"]["stop_zscore"] == cfg.Z_SCORE_STOP_THRESHOLD


def test_backtest_marks_to_market_and_closes_open_trade_at_period_end():
    idx = pd.date_range("2024-01-01", periods=35, freq="D")
    df_b = pd.DataFrame({"close": [100.0] * 35}, index=idx)
    df_a = pd.DataFrame({"close": [100.0] * 30 + [80.0, 78.0, 79.0, 81.0, 84.0]}, index=idx)

    signal = DivergenceSignal(
        asset_a="AAA",
        asset_b="BBB",
        z_score=-2.5,
        direction="long_AAA_short_BBB",
        conviction_score=3,
        metadata={"correlation_breakdown": True}
    )
    spec = generate_strategy(
        [signal],
        MarketRegime.NEUTRAL,
        {"btc_dominance": 55.0, "fear_greed_index": 50, "regime": "neutral"}
    )

    spec.risk_management["position_size_pct"] = 10.0
    spec.risk_management["stop_loss_pct"] = 50.0
    spec.analysis["thresholds"]["stop_zscore"] = 10.0

    result = run_backtest(df_a, df_b, spec)

    assert result.total_trades == 1
    assert result.avg_profit_per_trade_pct > 0
    assert result.max_drawdown_pct > 0
