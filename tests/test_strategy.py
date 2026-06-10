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
    assert spec.risk_management["fee_bps_per_leg"] == cfg.BACKTEST_FEE_BPS_PER_LEG
    assert spec.risk_management["slippage_bps_per_leg"] == cfg.BACKTEST_SLIPPAGE_BPS_PER_LEG
    assert spec.risk_management["borrow_bps_daily"] == cfg.BACKTEST_BORROW_BPS_DAILY


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
    assert result.avg_holding_period_days >= 1
    assert result.total_cost_drag_pct > 0


def test_backtest_cost_model_reduces_realized_return():
    idx = pd.date_range("2024-01-01", periods=35, freq="D")
    df_b = pd.DataFrame({"close": [100.0] * 35}, index=idx)
    df_a = pd.DataFrame({"close": [100.0] * 30 + [80.0, 78.0, 79.0, 81.0, 84.0]}, index=idx)

    signal = DivergenceSignal(
        asset_a="AAA",
        asset_b="BBB",
        z_score=-2.5,
        direction="long_AAA_short_BBB",
        conviction_score=3,
        metadata={"correlation_breakdown": True},
    )
    spec = generate_strategy(
        [signal],
        MarketRegime.NEUTRAL,
        {"btc_dominance": 55.0, "fear_greed_index": 50, "regime": "neutral"},
    )

    spec.risk_management["position_size_pct"] = 10.0
    spec.risk_management["stop_loss_pct"] = 50.0
    spec.analysis["thresholds"]["stop_zscore"] = 10.0

    low_cost_spec = spec.model_copy(deep=True)
    low_cost_spec.risk_management["fee_bps_per_leg"] = 0.0
    low_cost_spec.risk_management["slippage_bps_per_leg"] = 0.0
    low_cost_spec.risk_management["borrow_bps_daily"] = 0.0

    high_cost_spec = spec.model_copy(deep=True)
    high_cost_spec.risk_management["fee_bps_per_leg"] = 20.0
    high_cost_spec.risk_management["slippage_bps_per_leg"] = 20.0
    high_cost_spec.risk_management["borrow_bps_daily"] = 10.0

    low_cost = run_backtest(df_a, df_b, low_cost_spec)
    high_cost = run_backtest(df_a, df_b, high_cost_spec)

    assert low_cost.avg_profit_per_trade_pct > high_cost.avg_profit_per_trade_pct
    assert high_cost.total_cost_drag_pct > low_cost.total_cost_drag_pct


def test_backtest_supports_shorter_demo_windows():
    idx = pd.date_range("2024-01-01", periods=18, freq="D")
    df_b = pd.DataFrame({"close": [100.0, 100.0, 100.5, 100.5, 101.0, 101.0, 101.5, 101.5, 101.0, 101.0, 100.5, 100.5, 100.0, 100.0, 99.5, 99.5, 99.0, 99.0]}, index=idx)
    df_a = pd.DataFrame({"close": [100.0, 101.0, 102.0, 104.0, 106.0, 108.0, 110.0, 107.0, 104.0, 101.0, 98.0, 96.0, 94.0, 95.0, 96.0, 98.0, 99.0, 100.0]}, index=idx)

    signal = DivergenceSignal(
        asset_a="AAA",
        asset_b="BBB",
        z_score=2.8,
        direction="long_BBB_short_AAA",
        conviction_score=4,
        metadata={"correlation_breakdown": True},
    )
    spec = generate_strategy(
        [signal],
        MarketRegime.NEUTRAL,
        {"btc_dominance": 55.0, "fear_greed_index": 50, "regime": "neutral"},
    )

    result = run_backtest(df_a, df_b, spec, lookback=10, min_points=12)

    assert result.period == "2024-01-01 to 2024-01-18"
    assert result.total_trades >= 0
