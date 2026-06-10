import pandas as pd

import cadr.backtest.metrics as metrics
import cadr.config as cfg
import cadr.strategy.signals as sig
from cadr.analysis.divergence import compute_spread, spread_zscore
from cadr.data.models import BacktestResult, StrategySpec


def _holding_period_days(entry_idx: pd.Timestamp, exit_idx: pd.Timestamp) -> float:
    delta = exit_idx - entry_idx
    return max(1.0, delta.total_seconds() / 86400.0)


def _extract_cost_model(spec: StrategySpec) -> dict:
    risk = spec.risk_management
    fee_bps = float(risk.get("fee_bps_per_leg", cfg.BACKTEST_FEE_BPS_PER_LEG))
    slippage_bps = float(risk.get("slippage_bps_per_leg", cfg.BACKTEST_SLIPPAGE_BPS_PER_LEG))
    borrow_bps_daily = float(risk.get("borrow_bps_daily", cfg.BACKTEST_BORROW_BPS_DAILY))
    one_way_pair_cost_pct = ((fee_bps + slippage_bps) * 2.0) / 10000.0
    round_trip_pair_cost_pct = one_way_pair_cost_pct * 2.0
    return {
        "fee_bps_per_leg": fee_bps,
        "slippage_bps_per_leg": slippage_bps,
        "borrow_bps_daily": borrow_bps_daily,
        "one_way_pair_cost_pct": one_way_pair_cost_pct,
        "round_trip_pair_cost_pct": round_trip_pair_cost_pct,
    }


def run_backtest(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    spec: StrategySpec,
    *,
    lookback: int | None = None,
    min_points: int = 30,
) -> BacktestResult:
    """Run an iterative mean-reversion backtest with simple trading-cost assumptions."""

    if df_a.empty or df_b.empty:
        raise ValueError("DataFrames cannot be empty for backtesting.")

    df = pd.DataFrame({
        "price_a": df_a["close"],
        "price_b": df_b["close"],
    }).dropna()

    min_points = max(10, int(min_points))
    if len(df) < min_points:
        raise ValueError("Not enough overlapping data for backtesting.")

    df["spread"] = compute_spread(df["price_a"], df["price_b"])
    resolved_lookback = lookback if lookback is not None else 30
    resolved_lookback = max(5, min(int(resolved_lookback), max(5, len(df) - 1)))
    df["zscore"] = spread_zscore(df["spread"], lookback=resolved_lookback)

    direction = spec.strategy["direction"]
    asset_a = spec.strategy["pair"]["asset_a"]
    pos_size_pct = spec.risk_management["position_size_pct"] / 100.0
    stop_loss_pct = spec.risk_management["stop_loss_pct"] / 100.0
    thresholds = spec.analysis.get("thresholds", {})
    entry_threshold = thresholds.get("entry_zscore", cfg.Z_SCORE_ENTRY_THRESHOLD)
    exit_threshold = thresholds.get("exit_zscore", cfg.Z_SCORE_EXIT_THRESHOLD)
    stop_threshold = thresholds.get("stop_zscore", cfg.Z_SCORE_STOP_THRESHOLD)
    cost_model = _extract_cost_model(spec)

    in_position = False
    entry_zscore = 0.0
    entry_price_a = 0.0
    entry_price_b = 0.0
    entry_date = None
    realized_equity = 1.0
    equity_curve = pd.Series(index=df.index, dtype=float)
    trades = []

    for i, (idx, row) in enumerate(df.iterrows()):
        z = row["zscore"]

        if pd.isna(z):
            equity_curve.iloc[i] = realized_equity
            continue

        if not in_position:
            entered = False
            if direction.startswith("long_" + asset_a):
                if z <= -entry_threshold:
                    entered = True
            else:
                if z >= entry_threshold:
                    entered = True

            if entered:
                in_position = True
                entry_zscore = z
                entry_price_a = row["price_a"]
                entry_price_b = row["price_b"]
                entry_date = idx

            equity_curve.iloc[i] = realized_equity
            continue

        gross_ret_a = (row["price_a"] / entry_price_a) - 1
        gross_ret_b = (row["price_b"] / entry_price_b) - 1
        if direction.startswith("long_" + asset_a):
            gross_trade_pnl_pct = gross_ret_a - gross_ret_b
        else:
            gross_trade_pnl_pct = gross_ret_b - gross_ret_a

        holding_days = _holding_period_days(entry_date, idx)
        accrued_cost_pct = cost_model["one_way_pair_cost_pct"] + ((cost_model["borrow_bps_daily"] / 10000.0) * holding_days)
        mtm_equity = realized_equity * (1 + (gross_trade_pnl_pct - accrued_cost_pct) * pos_size_pct)

        hit_stop = (gross_trade_pnl_pct - accrued_cost_pct) <= -stop_loss_pct or abs(z) >= stop_threshold
        hit_tp = sig.exit_signal(z, entry_zscore, exit_threshold)

        if hit_stop or hit_tp:
            in_position = False
            total_cost_pct = cost_model["round_trip_pair_cost_pct"] + ((cost_model["borrow_bps_daily"] / 10000.0) * holding_days)
            net_trade_pnl_pct = gross_trade_pnl_pct - total_cost_pct
            realized_equity = realized_equity * (1 + net_trade_pnl_pct * pos_size_pct)
            trades.append(
                {
                    "entry_date": entry_date,
                    "exit_date": idx,
                    "holding_days": round(holding_days, 2),
                    "gross_pair_pnl_pct": round(gross_trade_pnl_pct * 100.0, 4),
                    "cost_drag_pct": round(total_cost_pct * 100.0, 4),
                    "pnl_pct": net_trade_pnl_pct * pos_size_pct,
                    "reason": "stop_loss" if hit_stop else "take_profit",
                }
            )
            equity_curve.iloc[i] = realized_equity
        else:
            equity_curve.iloc[i] = mtm_equity

    if in_position:
        last_idx = df.index[-1]
        last_row = df.iloc[-1]
        gross_ret_a = (last_row["price_a"] / entry_price_a) - 1
        gross_ret_b = (last_row["price_b"] / entry_price_b) - 1
        if direction.startswith("long_" + asset_a):
            gross_trade_pnl_pct = gross_ret_a - gross_ret_b
        else:
            gross_trade_pnl_pct = gross_ret_b - gross_ret_a

        holding_days = _holding_period_days(entry_date, last_idx)
        total_cost_pct = cost_model["round_trip_pair_cost_pct"] + ((cost_model["borrow_bps_daily"] / 10000.0) * holding_days)
        net_trade_pnl_pct = gross_trade_pnl_pct - total_cost_pct
        realized_equity = realized_equity * (1 + net_trade_pnl_pct * pos_size_pct)
        equity_curve.iloc[-1] = realized_equity
        trades.append(
            {
                "entry_date": entry_date,
                "exit_date": last_idx,
                "holding_days": round(holding_days, 2),
                "gross_pair_pnl_pct": round(gross_trade_pnl_pct * 100.0, 4),
                "cost_drag_pct": round(total_cost_pct * 100.0, 4),
                "pnl_pct": net_trade_pnl_pct * pos_size_pct,
                "reason": "end_of_period",
            }
        )

    results = metrics.calculate_metrics(equity_curve, trades)
    start_date = df.index[0].strftime("%Y-%m-%d")
    end_date = df.index[-1].strftime("%Y-%m-%d")
    avg_holding_days = round(sum(trade["holding_days"] for trade in trades) / len(trades), 2) if trades else 0.0
    total_cost_drag_pct = round(sum(trade["cost_drag_pct"] for trade in trades), 4) if trades else 0.0

    return BacktestResult(
        period=f"{start_date} to {end_date}",
        total_trades=results["total_trades"],
        win_rate=results["win_rate"],
        avg_profit_per_trade_pct=results["avg_profit_per_trade_pct"],
        sharpe_ratio=results["sharpe_ratio"],
        max_drawdown_pct=results["max_drawdown_pct"],
        profit_factor=results["profit_factor"],
        calmar_ratio=results["calmar_ratio"],
        avg_holding_period_days=avg_holding_days,
        total_cost_drag_pct=total_cost_drag_pct,
    )
