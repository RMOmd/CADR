import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List

import cadr.config as cfg
from cadr.dashboard.storage import DashboardStorage
from cadr.data.cmc_client import CMCClient


DIRECTION_PATTERN = re.compile(r"long_([A-Za-z0-9]+)_short_([A-Za-z0-9]+)", re.IGNORECASE)
LATEST_SNAPSHOT_PATH = Path("log/cadr_dashboard_snapshot_latest.json")
SNAPSHOT_DIR = Path("log/snapshots")
EVALUATION_DIR = Path("log/evaluations")
STABLE_ASSETS = {"USDT", "USDC", "DAI", "FDUSD", "TUSD", "USDP"}


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def parse_direction(direction: str | None, base_asset: str, quote_asset: str) -> Dict[str, Any]:
    if not direction:
        return {
            "direction_raw": None,
            "long_asset": None,
            "short_asset": None,
            "human": None,
        }

    match = DIRECTION_PATTERN.search(direction)
    if match:
        long_asset = match.group(1).upper()
        short_asset = match.group(2).upper()
    else:
        long_asset = quote_asset
        short_asset = base_asset

    return {
        "direction_raw": direction,
        "long_asset": long_asset,
        "short_asset": short_asset,
        "human": f"long {long_asset} / short {short_asset}",
    }


def parse_iso_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def forecast_like_gate_status(signal: Dict[str, Any], enabled_watchlist_pairs: set[str]) -> Dict[str, Any]:
    reasons: List[str] = []
    pair = str(signal.get("pair") or "")
    base_asset = str(signal.get("base_asset") or "").upper()
    quote_asset = str(signal.get("quote_asset") or "").upper()

    if cfg.CADR_SNAPSHOT_REQUIRE_OK_STATUS and signal.get("status") != "ok":
        reasons.append("signal_not_ok")
    if not cfg.CADR_SNAPSHOT_INCLUDE_NON_WATCHLIST and pair not in enabled_watchlist_pairs:
        reasons.append("pair_not_in_watchlist")
    if not signal.get("direction"):
        reasons.append("missing_direction")

    created_at = parse_iso_timestamp(signal.get("created_at"))
    if created_at is None:
        reasons.append("missing_created_at")
    else:
        age_hours = max(0.0, (datetime.now(UTC) - created_at.astimezone(UTC)).total_seconds() / 3600.0)
        if age_hours > float(cfg.CADR_SNAPSHOT_MAX_SIGNAL_AGE_HOURS):
            reasons.append("stale_signal")

    if cfg.CADR_FORECAST_BLOCK_STABLE_LEGS and (base_asset in STABLE_ASSETS or quote_asset in STABLE_ASSETS):
        reasons.append("stable_leg_blocked")

    spread_zscore = signal.get("spread_zscore")
    if spread_zscore is None:
        reasons.append("missing_spread_zscore")
    else:
        magnitude = abs(float(spread_zscore))
        if magnitude < cfg.Z_SCORE_ENTRY_THRESHOLD:
            reasons.append("zscore_below_entry_threshold")
        if magnitude > cfg.CADR_FORECAST_MAX_ABS_ZSCORE:
            reasons.append("zscore_above_maximum")

    conviction = signal.get("conviction_score")
    if conviction is None or int(conviction) < cfg.CADR_FORECAST_MIN_CONVICTION:
        reasons.append("conviction_below_minimum")

    correlation = signal.get("correlation")
    if correlation is None or float(correlation) < cfg.CADR_FORECAST_MIN_CORRELATION:
        reasons.append("correlation_below_minimum")

    spec = signal.get("spec") or {}
    pair_context = ((spec.get("analysis") or {}).get("skill_hub_pair_context") or {})
    data_quality = pair_context.get("data_quality") or {}
    aligned_days = data_quality.get("aligned_days")
    if aligned_days is None or int(aligned_days) < cfg.CADR_FORECAST_MIN_ALIGNED_DAYS:
        reasons.append("aligned_days_below_minimum")

    asset_summaries = pair_context.get("asset_summaries") or {}
    base_summary = asset_summaries.get(base_asset) or {}
    quote_summary = asset_summaries.get(quote_asset) or {}
    try:
        base_vol = float(base_summary.get("realized_volatility_daily_pct"))
        quote_vol = float(quote_summary.get("realized_volatility_daily_pct"))
        if min(base_vol, quote_vol) > 0:
            vol_ratio = max(base_vol, quote_vol) / min(base_vol, quote_vol)
            if vol_ratio > float(cfg.CADR_FORECAST_MAX_VOL_RATIO):
                reasons.append("volatility_imbalance_too_high")
    except (TypeError, ValueError):
        pass

    macro_context = ((spec.get("analysis") or {}).get("macro_context_summary") or {})
    risk_bias = str(macro_context.get("risk_bias") or "").strip().lower()
    if cfg.CADR_FORECAST_REQUIRE_NON_DEFENSIVE and risk_bias in {
        "defensive_research_only",
        "research_only",
        "no_trade_research_only",
    }:
        reasons.append("risk_bias_blocks_forecast")

    return {
        "eligible": not reasons,
        "reasons": reasons,
        "risk_bias": risk_bias or None,
    }


def _coerce_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        number = float(value)
        if number == number:
            return number
    except (TypeError, ValueError):
        return None
    return None


def build_demo_profile(signal: Dict[str, Any], pair_forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
    reasons: List[str] = []
    spec = signal.get("spec") or {}
    analysis = spec.get("analysis") or {}
    demo = analysis.get("demo_diagnostics") or signal.get("backtest_results") or {}
    base_asset = str(signal.get("base_asset") or "").upper()
    quote_asset = str(signal.get("quote_asset") or "").upper()

    correlation = _coerce_float(signal.get("correlation")) or 0.0
    zscore = abs(_coerce_float(signal.get("spread_zscore")) or 0.0)
    win_rate = _coerce_float(demo.get("win_rate"))
    setup_hit_rate = _coerce_float(demo.get("setup_hit_rate"))
    total_trades = int(demo.get("total_trades") or 0)
    setup_samples = int(demo.get("setup_samples") or 0)
    profit_factor = _coerce_float(demo.get("profit_factor")) or 0.0
    sharpe_ratio = _coerce_float(demo.get("sharpe_ratio")) or 0.0
    avg_profit = _coerce_float(demo.get("avg_profit_per_trade_pct")) or 0.0
    sample_points = int(demo.get("sample_points") or 0)
    quality = str(demo.get("quality") or "unknown")

    evaluated_pair_forecasts = [item for item in pair_forecasts if item.get("status") == "evaluated"]
    if evaluated_pair_forecasts:
        forecast_wins = sum(1 for item in evaluated_pair_forecasts if item.get("outcome") == "win")
        forecast_win_rate = forecast_wins / len(evaluated_pair_forecasts)
    else:
        forecast_win_rate = None

    if base_asset in STABLE_ASSETS or quote_asset in STABLE_ASSETS:
        reasons.append("stable_leg_blocked")
    if correlation < cfg.CADR_DEMO_MIN_CORRELATION:
        reasons.append("correlation_below_demo_minimum")
    if zscore < cfg.CADR_DEMO_MIN_ABS_ZSCORE:
        reasons.append("zscore_below_demo_band")
    if zscore > cfg.CADR_DEMO_MAX_ABS_ZSCORE:
        reasons.append("zscore_above_demo_band")
    if total_trades < cfg.CADR_DEMO_MIN_TRADES and setup_samples < cfg.CADR_DEMO_MIN_TRADES:
        reasons.append("not_enough_demo_trades")
    if win_rate is None and setup_hit_rate is None:
        reasons.append("missing_demo_backtest")

    components: List[float] = []
    if setup_hit_rate is not None:
        components.append(setup_hit_rate)
    if win_rate is not None:
        components.append(win_rate)
    if forecast_win_rate is not None:
        components.append(forecast_win_rate)
    expected_win_rate = round(sum(components) / len(components), 4) if components else None

    score_components = [
        min(1.0, max(0.0, correlation)),
        min(1.0, max(0.0, (profit_factor / 2.0))),
        min(1.0, max(0.0, (sharpe_ratio / 2.5))),
        min(1.0, max(0.0, (avg_profit / 4.0))),
        min(1.0, max(0.0, total_trades / 6.0)),
    ]
    if expected_win_rate is not None:
        score_components.append(min(1.0, max(0.0, expected_win_rate)))
    demo_score = round((sum(score_components) / len(score_components)) * 100.0, 2) if score_components else 0.0

    target_hit = expected_win_rate is not None and expected_win_rate >= float(cfg.CADR_DEMO_TARGET_WIN_RATE)
    stretch_hit = expected_win_rate is not None and expected_win_rate >= float(cfg.CADR_DEMO_STRETCH_WIN_RATE)

    return {
        "eligible": not reasons,
        "reasons": reasons,
        "demo_score": demo_score,
        "expected_win_rate": expected_win_rate,
        "target_hit": target_hit,
        "stretch_hit": stretch_hit,
        "setup_hit_rate": setup_hit_rate,
        "backtest_win_rate": win_rate,
        "forecast_win_rate": None if forecast_win_rate is None else round(forecast_win_rate, 4),
        "total_trades": total_trades,
        "setup_samples": setup_samples,
        "profit_factor": round(profit_factor, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "avg_profit_per_trade_pct": round(avg_profit, 2),
        "sample_points": sample_points,
        "quality": quality,
    }


def build_confirmed_profile(signal: Dict[str, Any], pair_forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
    demo_profile = build_demo_profile(signal, pair_forecasts)
    evidence_samples = max(
        int(demo_profile.get("setup_samples") or 0),
        int(demo_profile.get("total_trades") or 0),
        len([item for item in pair_forecasts if item.get("status") == "evaluated"]),
    )
    expected_win_rate = _coerce_float(demo_profile.get("expected_win_rate"))
    reasons = list(demo_profile.get("reasons") or [])

    if evidence_samples < int(cfg.CADR_CONFIRMED_MIN_EVIDENCE_SAMPLES):
        reasons.append("not_enough_confirmed_samples")
    if expected_win_rate is None:
        reasons.append("missing_confirmed_win_rate")
    elif expected_win_rate < float(cfg.CADR_CONFIRMED_TARGET_WIN_RATE):
        reasons.append("confirmed_win_rate_below_target")

    eligible = not reasons
    stretch_hit = expected_win_rate is not None and expected_win_rate >= float(cfg.CADR_CONFIRMED_STRETCH_WIN_RATE)
    return {
        "eligible": eligible,
        "reasons": reasons,
        "confirmed_score": demo_profile.get("demo_score"),
        "expected_win_rate": expected_win_rate,
        "target_hit": expected_win_rate is not None and expected_win_rate >= float(cfg.CADR_CONFIRMED_TARGET_WIN_RATE),
        "stretch_hit": stretch_hit,
        "evidence_samples": evidence_samples,
        "demo_profile": demo_profile,
    }


def compact_history_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "created_at": entry.get("created_at"),
        "status": entry.get("status"),
        "direction": entry.get("direction"),
        "spread_zscore": entry.get("spread_zscore"),
        "conviction_score": entry.get("conviction_score"),
        "market_regime": entry.get("market_regime"),
        "divergence_state": entry.get("divergence_state"),
        "correlation": entry.get("correlation"),
        "base_vs_peer_average_return_pct": entry.get("base_vs_peer_average_return_pct"),
    }


def build_pair_snapshot(
    signal: Dict[str, Any],
    history: List[Dict[str, Any]],
    pair_forecasts: List[Dict[str, Any]],
    entry_reference: Dict[str, Any] | None,
    gate_status: Dict[str, Any],
    demo_profile: Dict[str, Any],
    confirmed_profile: Dict[str, Any],
) -> Dict[str, Any]:
    spec = signal.get("spec") or {}
    analysis = spec.get("analysis", {})
    strategy = spec.get("strategy", {})
    skill_hub_context = analysis.get("skill_hub_pair_context", {})
    backtest_results = spec.get("backtest_results")

    return {
        "pair": signal["pair"],
        "base_asset": signal["base_asset"],
        "quote_asset": signal["quote_asset"],
        "status": signal["status"],
        "position": parse_direction(
            signal.get("direction"),
            signal["base_asset"],
            signal["quote_asset"],
        ),
        "signal_summary": {
            "spread_zscore": signal.get("spread_zscore"),
            "conviction_score": signal.get("conviction_score"),
            "market_regime": signal.get("market_regime"),
            "divergence_state": signal.get("divergence_state"),
            "correlation": signal.get("correlation"),
            "base_vs_peer_average_return_pct": signal.get("base_vs_peer_average_return_pct"),
            "last_observation_at": signal.get("created_at"),
        },
        "entry_reference": entry_reference,
        "strategy_summary": {
            "name": strategy.get("name"),
            "execution_style": strategy.get("execution_style"),
            "entry_rule": (spec.get("rules") or {}).get("entry"),
            "exit_rule": (spec.get("rules") or {}).get("exit"),
            "stop_loss_rule": (spec.get("rules") or {}).get("stop_loss"),
            "invalidation_rule": (spec.get("rules") or {}).get("invalidation"),
        },
        "risk_management": spec.get("risk_management"),
        "macro_context_summary": analysis.get("macro_context_summary"),
        "skill_hub_context": {
            "summary": skill_hub_context.get("summary"),
            "business_decision": skill_hub_context.get("business_decision"),
            "divergence_state": skill_hub_context.get("divergence_state"),
            "base_vs_peer_average_return_pct": skill_hub_context.get("base_vs_peer_average_return_pct"),
            "correlation_to_base": skill_hub_context.get("correlation_to_base"),
            "asset_summaries": skill_hub_context.get("asset_summaries"),
            "data_quality": skill_hub_context.get("data_quality"),
            "risk_notes": skill_hub_context.get("risk_notes"),
            "decision_basis": skill_hub_context.get("decision_basis"),
        },
        "backtest_results": backtest_results,
        "forecast_records": pair_forecasts,
        "gate_status": gate_status,
        "demo_profile": demo_profile,
        "confirmed_profile": confirmed_profile,
        "history": [compact_history_entry(entry) for entry in reversed(history)],
        "raw_spec": spec,
    }


def export_dashboard_snapshot(
    storage: DashboardStorage,
    cmc_client: CMCClient,
    *,
    db_path: str | None = None,
) -> Dict[str, Any]:
    enabled_watchlist_pairs = {
        entry["pair"]
        for entry in storage.list_watchlist_pairs(enabled_only=True)
    }
    latest_signals = [
        signal
        for signal in storage.list_latest_pair_signals()
        if cfg.CADR_SNAPSHOT_INCLUDE_NON_WATCHLIST or signal["pair"] in enabled_watchlist_pairs
    ]
    forecasts = storage.list_forecasts(limit=1000)
    forecasts_by_pair: Dict[str, List[Dict[str, Any]]] = {}
    for item in forecasts:
        forecasts_by_pair.setdefault(item["pair"], []).append(item)

    symbols = sorted({signal["base_asset"] for signal in latest_signals} | {signal["quote_asset"] for signal in latest_signals})
    quotes = cmc_client.get_quotes(symbols) if symbols else {}
    captured_at = utc_now_iso()
    if quotes:
        storage.add_quote_snapshots(quotes, captured_at=captured_at, source="snapshot_export_quotes")

    pair_snapshots = []
    execution_ready_count = 0
    demo_candidates: List[Dict[str, Any]] = []
    confirmed_candidates: List[Dict[str, Any]] = []
    for signal in latest_signals:
        history = storage.get_pair_history(signal["pair"], limit=250)
        pair_forecasts = forecasts_by_pair.get(signal["pair"], [])
        base_quote = quotes.get(signal["base_asset"])
        quote_quote = quotes.get(signal["quote_asset"])
        gate_status = forecast_like_gate_status(signal, enabled_watchlist_pairs)
        demo_profile = build_demo_profile(signal, pair_forecasts)
        confirmed_profile = build_confirmed_profile(signal, pair_forecasts)
        if gate_status["eligible"]:
            execution_ready_count += 1
        if demo_profile["eligible"]:
            demo_candidates.append(
                {
                    "pair": signal["pair"],
                    "direction": signal.get("direction"),
                    "demo_score": demo_profile["demo_score"],
                    "expected_win_rate": demo_profile["expected_win_rate"],
                    "target_hit": demo_profile["target_hit"],
                    "stretch_hit": demo_profile["stretch_hit"],
                    "setup_hit_rate": demo_profile["setup_hit_rate"],
                    "setup_samples": demo_profile["setup_samples"],
                    "total_trades": demo_profile["total_trades"],
                    "profit_factor": demo_profile["profit_factor"],
                    "sharpe_ratio": demo_profile["sharpe_ratio"],
                    "avg_profit_per_trade_pct": demo_profile["avg_profit_per_trade_pct"],
                    "quality": demo_profile["quality"],
                }
            )
        if confirmed_profile["eligible"]:
            confirmed_candidates.append(
                {
                    "pair": signal["pair"],
                    "direction": signal.get("direction"),
                    "expected_win_rate": confirmed_profile["expected_win_rate"],
                    "confirmed_score": confirmed_profile["confirmed_score"],
                    "target_hit": confirmed_profile["target_hit"],
                    "stretch_hit": confirmed_profile["stretch_hit"],
                    "evidence_samples": confirmed_profile["evidence_samples"],
                }
            )
        entry_reference = None
        if base_quote is not None and quote_quote is not None and quote_quote.price:
            entry_reference = {
                "captured_at": captured_at,
                "base_asset_price": base_quote.price,
                "quote_asset_price": quote_quote.price,
                "spread_ratio": base_quote.price / quote_quote.price,
            }
        pair_snapshots.append(
            build_pair_snapshot(
                signal=signal,
                history=history,
                pair_forecasts=pair_forecasts,
                entry_reference=entry_reference,
                gate_status=gate_status,
                demo_profile=demo_profile,
                confirmed_profile=confirmed_profile,
            )
        )

    demo_candidates.sort(
        key=lambda item: (
            item.get("target_hit", False),
            item.get("stretch_hit", False),
            item.get("expected_win_rate") is not None,
            item.get("expected_win_rate") or 0.0,
            item.get("demo_score") or 0.0,
        ),
        reverse=True,
    )
    demo_shortlist = demo_candidates[: max(1, int(cfg.CADR_DEMO_SHORTLIST_LIMIT))]
    demo_target_hits = sum(1 for item in demo_shortlist if item.get("target_hit"))
    demo_stretch_hits = sum(1 for item in demo_shortlist if item.get("stretch_hit"))
    confirmed_candidates.sort(
        key=lambda item: (
            item.get("target_hit", False),
            item.get("stretch_hit", False),
            item.get("expected_win_rate") is not None,
            item.get("expected_win_rate") or 0.0,
            item.get("confirmed_score") or 0.0,
            item.get("evidence_samples") or 0,
        ),
        reverse=True,
    )
    confirmed_shortlist = confirmed_candidates[: max(1, int(cfg.CADR_CONFIRMED_SHORTLIST_LIMIT))]
    confirmed_target_hits = sum(1 for item in confirmed_shortlist if item.get("target_hit"))
    confirmed_stretch_hits = sum(1 for item in confirmed_shortlist if item.get("stretch_hit"))

    generated_at = utc_now_iso()
    timestamp_slug = generated_at.replace(":", "-").replace(".", "-")
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "snapshot_type": "dashboard_prediction_snapshot",
        "generated_at": generated_at,
        "source_db": str(Path(db_path or storage.db_path).resolve()),
        "monitor": storage.get_monitor_settings(),
        "watchlist": storage.list_watchlist_pairs(enabled_only=False),
        "forecast_summary": storage.get_forecast_summary(),
        "latest_pair_count": len(latest_signals),
        "execution_ready_pair_count": execution_ready_count,
        "research_only_pair_count": max(0, len(latest_signals) - execution_ready_count),
        "demo_shortlist": demo_shortlist,
        "demo_shortlist_count": len(demo_shortlist),
        "demo_target_hits": demo_target_hits,
        "demo_stretch_hits": demo_stretch_hits,
        "demo_target_win_rate": cfg.CADR_DEMO_TARGET_WIN_RATE,
        "demo_stretch_win_rate": cfg.CADR_DEMO_STRETCH_WIN_RATE,
        "confirmed_shortlist": confirmed_shortlist,
        "confirmed_shortlist_count": len(confirmed_shortlist),
        "confirmed_target_hits": confirmed_target_hits,
        "confirmed_stretch_hits": confirmed_stretch_hits,
        "confirmed_target_win_rate": cfg.CADR_CONFIRMED_TARGET_WIN_RATE,
        "confirmed_stretch_win_rate": cfg.CADR_CONFIRMED_STRETCH_WIN_RATE,
        "pairs": pair_snapshots,
    }

    dated_path = SNAPSHOT_DIR / f"cadr_dashboard_snapshot_{timestamp_slug}.json"
    LATEST_SNAPSHOT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    dated_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "generated_at": generated_at,
        "latest_path": str(LATEST_SNAPSHOT_PATH.resolve()),
        "dated_path": str(dated_path.resolve()),
        "pair_count": len(pair_snapshots),
        "execution_ready_pair_count": execution_ready_count,
        "demo_shortlist_count": len(demo_shortlist),
        "forecast_summary": payload["forecast_summary"],
    }


def evaluate_pair(pair_snapshot: Dict[str, Any], quotes: Dict[str, Any]) -> Dict[str, Any]:
    gate_status = pair_snapshot.get("gate_status") or {"eligible": True, "reasons": []}
    entry_reference = pair_snapshot.get("entry_reference") or {}
    base_price_entry = entry_reference.get("base_asset_price")
    quote_price_entry = entry_reference.get("quote_asset_price")
    if not base_price_entry or not quote_price_entry:
        return {
            "pair": pair_snapshot["pair"],
            "status": "skipped",
            "reason": "missing_entry_reference",
            "execution_ready": bool(gate_status.get("eligible")),
            "gate_reasons": gate_status.get("reasons") or [],
        }

    base_symbol = pair_snapshot["base_asset"]
    quote_symbol = pair_snapshot["quote_asset"]
    base_quote = quotes.get(base_symbol)
    quote_quote = quotes.get(quote_symbol)
    if base_quote is None or quote_quote is None:
        return {
            "pair": pair_snapshot["pair"],
            "status": "skipped",
            "reason": "missing_live_quote",
            "execution_ready": bool(gate_status.get("eligible")),
            "gate_reasons": gate_status.get("reasons") or [],
        }

    direction_raw = (pair_snapshot.get("position") or {}).get("direction_raw") or ""
    match = DIRECTION_PATTERN.search(direction_raw)
    if not match:
        return {
            "pair": pair_snapshot["pair"],
            "status": "skipped",
            "reason": "missing_direction",
            "execution_ready": bool(gate_status.get("eligible")),
            "gate_reasons": gate_status.get("reasons") or [],
        }

    long_asset = match.group(1).upper()
    short_asset = match.group(2).upper()
    base_return = (base_quote.price / base_price_entry) - 1.0
    quote_return = (quote_quote.price / quote_price_entry) - 1.0

    if long_asset == base_symbol and short_asset == quote_symbol:
        pair_return = base_return - quote_return
    elif long_asset == quote_symbol and short_asset == base_symbol:
        pair_return = quote_return - base_return
    else:
        return {
            "pair": pair_snapshot["pair"],
            "status": "skipped",
            "reason": "direction_pair_mismatch",
            "execution_ready": bool(gate_status.get("eligible")),
            "gate_reasons": gate_status.get("reasons") or [],
        }

    pnl_pct = round(pair_return * 100.0, 4)
    if pnl_pct > 0.05:
        outcome = "win"
    elif pnl_pct < -0.05:
        outcome = "loss"
    else:
        outcome = "flat"

    return {
        "pair": pair_snapshot["pair"],
        "status": "evaluated",
        "execution_ready": bool(gate_status.get("eligible")),
        "gate_reasons": gate_status.get("reasons") or [],
        "direction": direction_raw,
        "outcome": outcome,
        "pnl_pct": pnl_pct,
        "entry_captured_at": entry_reference.get("captured_at"),
        "current_evaluated_at": utc_now_iso(),
        "entry_base_price": base_price_entry,
        "entry_quote_price": quote_price_entry,
        "current_base_price": base_quote.price,
        "current_quote_price": quote_quote.price,
        "entry_spread_ratio": entry_reference.get("spread_ratio"),
        "current_spread_ratio": base_quote.price / quote_quote.price,
    }


def evaluate_dashboard_snapshot(
    snapshot_path: str | Path | None,
    cmc_client: CMCClient,
) -> Dict[str, Any]:
    resolved_snapshot_path = Path(snapshot_path or LATEST_SNAPSHOT_PATH)
    payload = json.loads(resolved_snapshot_path.read_text(encoding="utf-8"))

    symbols = sorted({pair["base_asset"] for pair in payload["pairs"]} | {pair["quote_asset"] for pair in payload["pairs"]})
    quotes = cmc_client.get_quotes(symbols) if symbols else {}

    results = [evaluate_pair(pair_snapshot, quotes) for pair_snapshot in payload["pairs"]]
    summary = {
        "total": len(results),
        "evaluated": sum(1 for item in results if item["status"] == "evaluated"),
        "wins": sum(1 for item in results if item.get("outcome") == "win"),
        "losses": sum(1 for item in results if item.get("outcome") == "loss"),
        "flat": sum(1 for item in results if item.get("outcome") == "flat"),
        "skipped": sum(1 for item in results if item["status"] == "skipped"),
    }
    execution_results = [item for item in results if item.get("execution_ready")]
    execution_ready_summary = {
        "total": len(execution_results),
        "evaluated": sum(1 for item in execution_results if item["status"] == "evaluated"),
        "wins": sum(1 for item in execution_results if item.get("outcome") == "win"),
        "losses": sum(1 for item in execution_results if item.get("outcome") == "loss"),
        "flat": sum(1 for item in execution_results if item.get("outcome") == "flat"),
        "skipped": sum(1 for item in execution_results if item["status"] == "skipped"),
    }
    excluded_reasons: Dict[str, int] = {}
    for pair_snapshot in payload["pairs"]:
        gate_status = pair_snapshot.get("gate_status") or {}
        if gate_status.get("eligible"):
            continue
        reasons = gate_status.get("reasons") or ["excluded"]
        for reason in reasons:
            excluded_reasons[reason] = excluded_reasons.get(reason, 0) + 1

    output = {
        "snapshot_path": str(resolved_snapshot_path.resolve()),
        "evaluated_at": utc_now_iso(),
        "summary": summary,
        "execution_ready_summary": execution_ready_summary,
        "excluded_reason_counts": excluded_reasons,
        "results": results,
    }

    EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
    slug = output["evaluated_at"].replace(":", "-").replace(".", "-")
    out_path = EVALUATION_DIR / f"cadr_snapshot_evaluation_{slug}.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    output["output_path"] = str(out_path.resolve())
    return output


def _read_json_if_exists(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    return DashboardStorage._sanitize_json_numbers(json.loads(path.read_text(encoding="utf-8")))


def get_snapshot_status() -> Dict[str, Any]:
    latest_snapshot = _read_json_if_exists(LATEST_SNAPSHOT_PATH)
    latest_evaluation = None
    if EVALUATION_DIR.exists():
        evaluation_files = sorted(EVALUATION_DIR.glob("cadr_snapshot_evaluation_*.json"))
        if evaluation_files:
            latest_evaluation = _read_json_if_exists(evaluation_files[-1])

    return {
        "latest_snapshot_path": str(LATEST_SNAPSHOT_PATH.resolve()) if LATEST_SNAPSHOT_PATH.exists() else None,
        "latest_snapshot": latest_snapshot,
        "latest_evaluation": latest_evaluation,
    }
