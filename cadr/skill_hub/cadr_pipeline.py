from typing import Any, Dict, List

import pandas as pd

from cadr.analysis.divergence import detect_divergences, compute_spread, spread_zscore
from cadr.analysis.regime import classify_regime
from cadr.backtest.engine import run_backtest
from cadr.data.cmc_client import CMCClient
from cadr.data.models import DivergenceSignal, FearGreedEntry, GlobalMetrics, StrategySpec
from cadr.skill_hub.client import SkillHubClient
from cadr.skill_hub.pipeline import run_daily_market_overview_preview
from cadr.strategy.generator import generate_strategy


def _chart_points_to_frames(chart_points: List[Dict[str, Any]], symbols: List[str]) -> Dict[str, pd.DataFrame]:
    rows = []
    for point in chart_points:
        if "date" not in point:
            continue
        row = {"timestamp": pd.to_datetime(point["date"])}
        for symbol in symbols:
            row[symbol] = point.get(symbol)
        rows.append(row)

    df = pd.DataFrame(rows).dropna()
    if df.empty:
        raise ValueError("No usable chart points were returned by Skill Hub for the requested pair.")

    df.set_index("timestamp", inplace=True)
    df.sort_index(inplace=True)

    frames = {}
    for symbol in symbols:
        frames[symbol] = pd.DataFrame({"close": df[symbol].astype(float)})
    return frames


def _build_demo_diagnostics(
    pair_frame_a: pd.DataFrame,
    pair_frame_b: pd.DataFrame,
    spec: StrategySpec,
) -> Dict[str, Any] | None:
    overlapping = min(len(pair_frame_a), len(pair_frame_b))
    if overlapping < 12:
        return None

    lookback = min(14, max(6, overlapping - 2))
    try:
        backtest_result = run_backtest(
            pair_frame_a,
            pair_frame_b,
            spec,
            lookback=lookback,
            min_points=12,
        )
    except Exception:
        backtest_result = None

    spread = compute_spread(pair_frame_a["close"], pair_frame_b["close"])
    zscores = spread_zscore(spread, lookback=lookback).dropna()
    thresholds = spec.analysis.get("thresholds", {})
    entry_threshold = float(thresholds.get("entry_zscore", 2.0))
    exit_threshold = float(thresholds.get("exit_zscore", 0.5))
    stop_threshold = float(thresholds.get("stop_zscore", 3.5))
    horizon = min(6, max(2, len(zscores) // 3))
    event_hits = 0
    event_failures = 0
    event_samples = 0
    idx = 0
    z_values = list(zscores.values)
    while idx < len(z_values):
        entry_z = float(z_values[idx])
        if abs(entry_z) < entry_threshold:
            idx += 1
            continue
        event_samples += 1
        resolved = False
        for step in range(1, min(horizon + 1, len(z_values) - idx)):
            future_z = float(z_values[idx + step])
            reverted = abs(future_z) <= exit_threshold or (future_z * entry_z) < 0
            stopped = abs(future_z) >= stop_threshold or abs(future_z) >= abs(entry_z) + 0.75
            if reverted:
                event_hits += 1
                resolved = True
                idx += step
                break
            if stopped:
                event_failures += 1
                resolved = True
                idx += step
                break
        if not resolved:
            event_failures += 1
        idx += 1

    payload = backtest_result.model_dump() if backtest_result is not None else {
        "total_trades": 0,
        "win_rate": 0.0,
        "avg_profit_per_trade_pct": 0.0,
        "sharpe_ratio": 0.0,
        "profit_factor": 0.0,
        "calmar_ratio": 0.0,
        "max_drawdown_pct": 0.0,
        "avg_holding_period_days": 0.0,
        "total_cost_drag_pct": 0.0,
    }
    payload["sample_points"] = overlapping
    payload["lookback_used"] = lookback
    payload["quality"] = "limited_sample" if overlapping < 30 else "full_sample"
    payload["setup_samples"] = event_samples
    payload["setup_hits"] = event_hits
    payload["setup_failures"] = event_failures
    payload["setup_hit_rate"] = round((event_hits / event_samples), 4) if event_samples else None
    return payload


def _build_global_metrics(client: CMCClient) -> GlobalMetrics:
    return client.get_global_metrics()


def _build_fear_greed(client: CMCClient) -> FearGreedEntry | None:
    return client.get_fear_greed()


def _fallback_signal_from_skill_hub_report(base_asset: str, quote_asset: str, report: Dict[str, Any]) -> DivergenceSignal:
    divergence_state = report.get("divergence_state")
    return_spread = float(report.get("base_vs_peer_average_return_pct", 0.0))

    if divergence_state == "base_outperforming":
        direction = f"long_{quote_asset}_short_{base_asset}"
    elif divergence_state in {"base_underperforming", "base_lagging"}:
        direction = f"long_{base_asset}_short_{quote_asset}"
    elif divergence_state == "broadly_tracking":
        direction = f"long_{base_asset}_short_{quote_asset}" if return_spread < 0 else f"long_{quote_asset}_short_{base_asset}"
    else:
        raise ValueError("Skill Hub report did not provide a usable divergence_state for CADR signal generation.")

    z_proxy = max(2.05, abs(return_spread) / 2.0)
    if direction.startswith(f"long_{base_asset}"):
        z_proxy *= -1

    conviction = min(5, max(1, int(abs(z_proxy) / 0.5)))
    return DivergenceSignal(
        asset_a=base_asset,
        asset_b=quote_asset,
        z_score=round(z_proxy, 2),
        direction=direction,
        conviction_score=conviction,
        metadata={
            "signal_method": "skill_hub_divergence_fallback",
            "divergence_state": divergence_state,
            "base_vs_peer_average_return_pct": return_spread,
            "correlation_to_base": report.get("correlation_to_base", {}),
        },
    )


def generate_cadr_strategy_from_skill_hub(
    base_asset: str,
    quote_assets: List[str],
    lookback_days: int = 90,
    skill_hub_client: SkillHubClient | None = None,
    cmc_client: CMCClient | None = None,
) -> StrategySpec:
    if not quote_assets:
        raise ValueError("At least one quote asset is required for CADR generation.")

    skill_hub_client = skill_hub_client or SkillHubClient()
    cmc_client = cmc_client or CMCClient()

    divergence_result = skill_hub_client.execute_skill(
        "analyze_cross_asset_performance_divergence",
        {
            "base_asset": base_asset,
            "quote_assets": [{"symbol": symbol, "asset_type": "crypto"} for symbol in quote_assets],
            "lookback_days": lookback_days,
        },
    )

    report = divergence_result.data.get("report", {})
    chart_points = report.get("chart_points", [])
    symbols = [base_asset, *quote_assets]
    frames = _chart_points_to_frames(chart_points, symbols)

    pairs_data = {}
    for quote_asset in quote_assets:
        pairs_data[(base_asset, quote_asset)] = (frames[base_asset]["close"], frames[quote_asset]["close"])

    signals = detect_divergences(
        pairs_data,
        threshold=2.0,
        lookback=min(30, max(10, len(frames[base_asset]) - 1)),
        require_correlation_breakdown=False,
    )
    if not signals:
        signals = [_fallback_signal_from_skill_hub_report(base_asset, quote_assets[0], report)]

    global_metrics = _build_global_metrics(cmc_client)
    fear_greed = _build_fear_greed(cmc_client)
    regime = classify_regime(global_metrics, fear_greed)

    market_overview = run_daily_market_overview_preview(skill_hub_client)
    market_context = {
        "btc_dominance": global_metrics.btc_dominance,
        "eth_dominance": global_metrics.eth_dominance,
        "fear_greed_index": fear_greed.value if fear_greed else None,
        "regime": regime.value,
        "source": "cmc_api_and_skill_hub",
        "skill_hub_market_status": market_overview.status,
        "skill_hub_market_confidence": market_overview.confidence,
    }

    spec = generate_strategy(signals, regime, market_context)
    best_signal = max(signals, key=lambda signal: abs(signal.z_score))
    pair_report = {
        "skill_id": divergence_result.skill_id,
        "summary": divergence_result.data.get("summary"),
        "business_decision": divergence_result.data.get("business_decision"),
        "divergence_state": report.get("divergence_state"),
        "base_vs_peer_average_return_pct": report.get("base_vs_peer_average_return_pct"),
        "correlation_to_base": report.get("correlation_to_base", {}),
        "asset_summaries": report.get("asset_summaries", {}),
        "data_quality": divergence_result.data.get("data_quality", {}),
        "risk_notes": divergence_result.data.get("risk_notes", []),
        "decision_basis": divergence_result.data.get("decision_basis", []),
    }

    spec.strategy["execution_style"] = "cadr_skill_hub_pair_mean_reversion"
    spec.analysis["signal_method"] = "skill_hub_chart_points_plus_local_mean_reversion"
    spec.analysis["skill_hub_pair_context"] = pair_report
    spec.analysis["macro_context_summary"] = {
        "market_overview_summary": market_overview.summary,
        "market_regime": market_overview.market_read.get("regime"),
        "risk_bias": market_overview.market_read.get("risk_bias"),
    }
    spec.rules["entry"] = (
        f"Pair divergence z-score >= {spec.analysis['thresholds']['entry_zscore']} "
        f"with Skill Hub divergence state {pair_report.get('divergence_state')}"
    )
    spec.rules["invalidation"] = "Macro risk bias worsens, correlation breaks structurally, or divergence extends beyond stop threshold."
    spec.market_context["skill_hub"] = {
        "daily_market_overview": {
            "status": market_overview.status,
            "confidence": market_overview.confidence,
            "risk_bias": market_overview.market_read.get("risk_bias"),
        },
        "pair_divergence": {
            "status": divergence_result.data.get("status"),
            "summary": divergence_result.data.get("summary"),
        },
    }

    pair_frame_a = frames[best_signal.asset_a]
    pair_frame_b = frames[best_signal.asset_b]
    if len(pair_frame_a) >= 30 and len(pair_frame_b) >= 30:
        backtest_result = run_backtest(pair_frame_a, pair_frame_b, spec)
        spec.backtest_results = backtest_result.model_dump()
    demo_diagnostics = _build_demo_diagnostics(pair_frame_a, pair_frame_b, spec)
    if demo_diagnostics is not None:
        spec.analysis["demo_diagnostics"] = demo_diagnostics

    return spec
