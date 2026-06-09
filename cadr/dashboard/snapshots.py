import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List

from cadr.dashboard.storage import DashboardStorage
from cadr.data.cmc_client import CMCClient


DIRECTION_PATTERN = re.compile(r"long_([A-Za-z0-9]+)_short_([A-Za-z0-9]+)", re.IGNORECASE)
LATEST_SNAPSHOT_PATH = Path("log/cadr_dashboard_snapshot_latest.json")
SNAPSHOT_DIR = Path("log/snapshots")
EVALUATION_DIR = Path("log/evaluations")


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
        "history": [compact_history_entry(entry) for entry in reversed(history)],
        "raw_spec": spec,
    }


def export_dashboard_snapshot(
    storage: DashboardStorage,
    cmc_client: CMCClient,
    *,
    db_path: str | None = None,
) -> Dict[str, Any]:
    latest_signals = storage.list_latest_pair_signals()
    forecasts = storage.list_forecasts(limit=1000)
    forecasts_by_pair: Dict[str, List[Dict[str, Any]]] = {}
    for item in forecasts:
        forecasts_by_pair.setdefault(item["pair"], []).append(item)

    symbols = sorted({signal["base_asset"] for signal in latest_signals} | {signal["quote_asset"] for signal in latest_signals})
    quotes = cmc_client.get_quotes(symbols) if symbols else {}

    pair_snapshots = []
    captured_at = utc_now_iso()
    for signal in latest_signals:
        history = storage.get_pair_history(signal["pair"], limit=250)
        base_quote = quotes.get(signal["base_asset"])
        quote_quote = quotes.get(signal["quote_asset"])
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
                pair_forecasts=forecasts_by_pair.get(signal["pair"], []),
                entry_reference=entry_reference,
            )
        )

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
        "forecast_summary": payload["forecast_summary"],
    }


def evaluate_pair(pair_snapshot: Dict[str, Any], quotes: Dict[str, Any]) -> Dict[str, Any]:
    entry_reference = pair_snapshot.get("entry_reference") or {}
    base_price_entry = entry_reference.get("base_asset_price")
    quote_price_entry = entry_reference.get("quote_asset_price")
    if not base_price_entry or not quote_price_entry:
        return {
            "pair": pair_snapshot["pair"],
            "status": "skipped",
            "reason": "missing_entry_reference",
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
        }

    direction_raw = (pair_snapshot.get("position") or {}).get("direction_raw") or ""
    match = DIRECTION_PATTERN.search(direction_raw)
    if not match:
        return {
            "pair": pair_snapshot["pair"],
            "status": "skipped",
            "reason": "missing_direction",
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

    output = {
        "snapshot_path": str(resolved_snapshot_path.resolve()),
        "evaluated_at": utc_now_iso(),
        "summary": summary,
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
    return json.loads(path.read_text(encoding="utf-8"))


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
