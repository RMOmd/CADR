import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import cadr.config as cfg
from cadr.dashboard.storage import DashboardStorage
from cadr.data.cmc_client import CMCClient
from cadr.skill_hub import SkillHubClient, generate_cadr_strategy_from_skill_hub, run_daily_market_overview_preview


PAIR_PATTERN = re.compile(r"^\s*([A-Za-z0-9]+)\s*[/:\-]\s*([A-Za-z0-9]+)\s*$")


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_now_iso() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


class DashboardService:
    def __init__(
        self,
        storage: DashboardStorage,
        monitoring_pairs: Iterable[Tuple[str, str]] | None = None,
        cmc_client: CMCClient | None = None,
    ):
        self.storage = storage
        self.cmc_client = cmc_client or CMCClient()
        self._run_lock = Lock()
        self.storage.seed_watchlist(
            pairs=monitoring_pairs or cfg.MONITORING_PAIRS,
            enabled=cfg.CADR_MONITOR_ENABLED,
            interval_sec=cfg.CADR_MONITOR_INTERVAL_SEC,
            lookback_days=cfg.CADR_MONITOR_LOOKBACK_DAYS,
            now_iso=utc_now_iso(),
        )
        self.export_forecasts_snapshot()

    def run_daily_overview(self) -> Dict[str, Any]:
        with self._run_lock:
            started_at = utc_now_iso()
            run_id = self.storage.create_run("daily_overview", None, "running", started_at)
            try:
                overview = run_daily_market_overview_preview(SkillHubClient())
                payload = overview.model_dump()
                self.storage.complete_run(
                    run_id,
                    status="ok",
                    finished_at=utc_now_iso(),
                    message=overview.summary,
                    payload=payload,
                )
                return payload
            except Exception as exc:
                self.storage.complete_run(
                    run_id,
                    status="error",
                    finished_at=utc_now_iso(),
                    error=str(exc),
                )
                raise

    def run_pair(self, base_asset: str, quote_asset: str, lookback_days: int = 90) -> Dict[str, Any]:
        base_asset = base_asset.strip().upper()
        quote_asset = quote_asset.strip().upper()
        pair = f"{base_asset}/{quote_asset}"
        with self._run_lock:
            started_at = utc_now_iso()
            run_id = self.storage.create_run("pair_scan", pair, "running", started_at)
            created_at = utc_now_iso()
            try:
                spec = generate_cadr_strategy_from_skill_hub(
                    base_asset=base_asset,
                    quote_assets=[quote_asset],
                    lookback_days=lookback_days,
                )
                signal = self._spec_to_signal(pair, base_asset, quote_asset, spec)
                created_forecasts = self._record_forecasts([signal], created_at)
                signal["forecast_recorded"] = bool(created_forecasts)
                self.storage.add_pair_signal(run_id, signal, created_at)
                self.storage.complete_run(
                    run_id,
                    status="ok",
                    finished_at=utc_now_iso(),
                    message=f"{pair} -> {signal['direction']}",
                    payload=signal,
                )
                self.evaluate_due_forecasts()
                return signal
            except Exception as exc:
                failed_signal = self._build_failed_signal(pair, base_asset, quote_asset, str(exc))
                self.storage.add_pair_signal(run_id, failed_signal, created_at)
                self.storage.complete_run(
                    run_id,
                    status="error",
                    finished_at=utc_now_iso(),
                    error=str(exc),
                    payload=failed_signal,
                )
                return failed_signal

    def run_default_scan(self, lookback_days: int = 90) -> Dict[str, Any]:
        with self._run_lock:
            payload = self._run_scan_locked(
                run_type="default_scan",
                pairs=self.get_enabled_watchlist_pairs(),
                lookback_days=lookback_days,
            )
        self.evaluate_due_forecasts()
        return payload

    def run_monitor_cycle(self, force: bool = False) -> Dict[str, Any]:
        settings = self.storage.get_monitor_settings()
        if not force and not settings["enabled"]:
            return {
                "status": "disabled",
                "message": "Background monitor is disabled.",
                "settings": settings,
            }

        lock_acquired = self._run_lock.acquire(blocking=False)
        if not lock_acquired:
            return {
                "status": "busy",
                "message": "Another scan is already running.",
                "settings": settings,
            }

        started_at = utc_now_iso()
        self.storage.update_monitor_settings(
            last_started_at=started_at,
            last_status="running",
            last_message="Background watchlist scan is running.",
            now_iso=started_at,
        )

        try:
            payload = self._run_scan_locked(
                run_type="monitor_scan",
                pairs=self.get_enabled_watchlist_pairs(),
                lookback_days=settings["lookback_days"],
            )
            evaluation = self.evaluate_due_forecasts()
            finished_at = utc_now_iso()
            next_run_at = self._compute_next_run_iso(settings["interval_sec"])
            monitor_state = self.storage.update_monitor_settings(
                next_run_at=next_run_at,
                last_finished_at=finished_at,
                last_status=payload["status"],
                last_message=(
                    f"{payload['ok_count']} ok / {payload['error_count']} errors, "
                    f"{evaluation['evaluated']} forecasts evaluated."
                ),
                now_iso=finished_at,
            )
            return {
                "status": payload["status"],
                "message": monitor_state["last_message"],
                "scan": payload,
                "evaluation": evaluation,
                "settings": monitor_state,
            }
        except Exception as exc:
            finished_at = utc_now_iso()
            self.storage.update_monitor_settings(
                last_finished_at=finished_at,
                last_status="error",
                last_message=str(exc),
                next_run_at=self._compute_next_run_iso(settings["interval_sec"]),
                now_iso=finished_at,
            )
            raise
        finally:
            self._run_lock.release()

    def get_dashboard_snapshot(self) -> Dict[str, Any]:
        latest_overview = self.storage.get_latest_run("daily_overview")
        latest_scan = self.storage.get_latest_run("default_scan")
        latest_monitor = self.storage.get_latest_run("monitor_scan")
        pair_signals = self.storage.list_latest_pair_signals()
        recent_runs = self.storage.list_recent_runs(limit=12)
        monitor_settings = self.storage.get_monitor_settings()
        watchlist = self.storage.list_watchlist_pairs(enabled_only=False)
        forecast_summary = self.storage.get_forecast_summary()
        recent_forecasts = self.storage.list_forecasts(limit=8)

        ok_pairs = sum(1 for signal in pair_signals if signal["status"] == "ok")
        error_pairs = sum(1 for signal in pair_signals if signal["status"] == "error")

        return {
            "latest_overview": latest_overview,
            "latest_scan": latest_scan,
            "latest_monitor": latest_monitor,
            "pair_signals": pair_signals,
            "recent_runs": recent_runs,
            "watchlist": watchlist,
            "monitor": monitor_settings,
            "forecasts": {
                "summary": forecast_summary,
                "recent": recent_forecasts,
                "export_path": str(Path(cfg.CADR_FORECAST_EXPORT_PATH).resolve()),
            },
            "stats": {
                "monitored_pairs": len([pair for pair in watchlist if pair["enabled"]]),
                "latest_pairs_available": len(pair_signals),
                "ok_pairs": ok_pairs,
                "error_pairs": error_pairs,
                "pending_forecasts": forecast_summary["pending"],
                "evaluated_forecasts": forecast_summary["evaluated"],
            },
        }

    def get_pair_detail(self, pair: str) -> Dict[str, Any]:
        latest = self.storage.get_pair_latest(pair)
        history = self.storage.get_pair_history(pair, limit=10)
        if latest is None:
            raise KeyError(pair)
        return {
            "latest": latest,
            "history": history,
        }

    def get_watchlist_payload(self) -> Dict[str, Any]:
        return {
            "pairs": self.storage.list_watchlist_pairs(enabled_only=False),
            "monitor": self.storage.get_monitor_settings(),
        }

    def update_watchlist(
        self,
        *,
        pair_strings: Sequence[str],
        enabled: bool,
        interval_minutes: int,
        lookback_days: int,
    ) -> Dict[str, Any]:
        pairs = self.parse_pair_strings(pair_strings)
        if not pairs:
            raise ValueError("Watchlist must contain at least one valid pair.")

        now_iso = utc_now_iso()
        saved_pairs = self.storage.replace_watchlist(pairs, now_iso=now_iso)
        next_run_at = self._compute_next_run_iso(interval_minutes * 60) if enabled else None
        monitor_settings = self.storage.update_monitor_settings(
            enabled=enabled,
            interval_sec=interval_minutes * 60,
            lookback_days=lookback_days,
            next_run_at=next_run_at,
            last_message="Watchlist updated by operator.",
            now_iso=now_iso,
        )
        return {
            "pairs": saved_pairs,
            "monitor": monitor_settings,
        }

    def list_forecasts(self, limit: int = 20) -> Dict[str, Any]:
        self.export_forecasts_snapshot()
        return {
            "summary": self.storage.get_forecast_summary(),
            "items": self.storage.list_forecasts(limit=limit),
            "export_path": str(Path(cfg.CADR_FORECAST_EXPORT_PATH).resolve()),
        }

    def evaluate_due_forecasts(self) -> Dict[str, Any]:
        now_iso = utc_now_iso()
        due_forecasts = self.storage.list_due_forecasts(now_iso)
        if not due_forecasts:
            summary = self.storage.get_forecast_summary()
            self.export_forecasts_snapshot()
            return {
                "evaluated": 0,
                "skipped": 0,
                "summary": summary,
            }

        symbols = sorted({forecast["base_asset"] for forecast in due_forecasts} | {forecast["quote_asset"] for forecast in due_forecasts})
        quotes = self.cmc_client.get_quotes(symbols)
        evaluated = 0
        skipped = 0

        for forecast in due_forecasts:
            base_quote = quotes.get(forecast["base_asset"])
            quote_quote = quotes.get(forecast["quote_asset"])
            if base_quote is None or quote_quote is None:
                skipped += 1
                continue

            pnl_pct, outcome, evaluation = self._evaluate_forecast_from_quotes(forecast, base_quote.price, quote_quote.price)
            self.storage.update_forecast_evaluation(
                forecast["id"],
                evaluated_at=now_iso,
                status="evaluated",
                outcome=outcome,
                pnl_pct=pnl_pct,
                evaluation=evaluation,
            )
            evaluated += 1

        summary = self.storage.get_forecast_summary()
        self.export_forecasts_snapshot()
        return {
            "evaluated": evaluated,
            "skipped": skipped,
            "summary": summary,
        }

    def export_forecasts_snapshot(self) -> None:
        payload = {
            "generated_at": utc_now_iso(),
            "summary": self.storage.get_forecast_summary(),
            "monitor": self.storage.get_monitor_settings(),
            "watchlist": self.storage.list_watchlist_pairs(enabled_only=False),
            "forecasts": self.storage.list_forecasts(limit=500),
        }
        export_path = Path(cfg.CADR_FORECAST_EXPORT_PATH)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_enabled_watchlist_pairs(self) -> List[Tuple[str, str]]:
        pairs = self.storage.list_watchlist_pairs(enabled_only=True)
        return [(entry["base_asset"], entry["quote_asset"]) for entry in pairs]

    @staticmethod
    def parse_pair_strings(pair_strings: Sequence[str]) -> List[Tuple[str, str]]:
        normalized: List[Tuple[str, str]] = []
        seen = set()
        for value in pair_strings:
            match = PAIR_PATTERN.match(str(value))
            if not match:
                continue
            base_asset = match.group(1).upper()
            quote_asset = match.group(2).upper()
            if base_asset == quote_asset:
                continue
            pair = (base_asset, quote_asset)
            if pair in seen:
                continue
            seen.add(pair)
            normalized.append(pair)
        return normalized

    def _run_scan_locked(self, *, run_type: str, pairs: Sequence[Tuple[str, str]], lookback_days: int) -> Dict[str, Any]:
        started_at = utc_now_iso()
        run_id = self.storage.create_run(run_type, None, "running", started_at)
        results: List[Dict[str, Any]] = []
        ok_count = 0
        error_count = 0
        created_at = utc_now_iso()

        for base_asset, quote_asset in pairs:
            pair = f"{base_asset}/{quote_asset}"
            try:
                spec = generate_cadr_strategy_from_skill_hub(
                    base_asset=base_asset,
                    quote_assets=[quote_asset],
                    lookback_days=lookback_days,
                )
                signal = self._spec_to_signal(pair, base_asset, quote_asset, spec)
                ok_count += 1
            except Exception as exc:
                signal = self._build_failed_signal(pair, base_asset, quote_asset, str(exc))
                error_count += 1

            self.storage.add_pair_signal(run_id, signal, created_at)
            results.append(signal)

        forecasts_created = self._record_forecasts(results, created_at)
        payload = {
            "total_pairs": len(results),
            "ok_count": ok_count,
            "error_count": error_count,
            "forecast_count": len(forecasts_created),
            "pairs": results,
            "status": "ok" if error_count == 0 else "partial",
        }
        self.storage.complete_run(
            run_id,
            status=payload["status"],
            finished_at=utc_now_iso(),
            message=f"{ok_count} ok / {error_count} errors / {len(forecasts_created)} forecasts",
            payload=payload,
        )
        self.export_forecasts_snapshot()
        return payload

    def _record_forecasts(self, signals: Sequence[Dict[str, Any]], created_at: str) -> List[Dict[str, Any]]:
        candidates = [
            signal for signal in signals
            if signal.get("status") == "ok"
            and signal.get("direction")
            and signal.get("spread_zscore") is not None
            and abs(float(signal["spread_zscore"])) >= cfg.Z_SCORE_ENTRY_THRESHOLD
        ]
        if not candidates:
            return []

        unique_symbols = sorted({signal["base_asset"] for signal in candidates} | {signal["quote_asset"] for signal in candidates})
        quotes = self.cmc_client.get_quotes(unique_symbols)
        due_at = (
            datetime.fromisoformat(created_at.replace("Z", "+00:00")) + timedelta(hours=cfg.CADR_FORECAST_HORIZON_HOURS)
        ).isoformat().replace("+00:00", "Z")

        created_forecasts: List[Dict[str, Any]] = []
        for signal in candidates:
            if self.storage.has_pending_forecast(signal["pair"], signal["direction"], created_at):
                continue

            base_quote = quotes.get(signal["base_asset"])
            quote_quote = quotes.get(signal["quote_asset"])
            if base_quote is None or quote_quote is None:
                continue

            entry_spread_ratio = float(base_quote.price) / float(quote_quote.price)
            forecast = {
                "pair": signal["pair"],
                "base_asset": signal["base_asset"],
                "quote_asset": signal["quote_asset"],
                "direction": signal["direction"],
                "spread_zscore": signal.get("spread_zscore"),
                "conviction_score": signal.get("conviction_score"),
                "market_regime": signal.get("market_regime"),
                "divergence_state": signal.get("divergence_state"),
                "correlation": signal.get("correlation"),
                "entry_price_base": float(base_quote.price),
                "entry_price_quote": float(quote_quote.price),
                "entry_spread_ratio": entry_spread_ratio,
                "created_at": created_at,
                "due_at": due_at,
                "status": "pending",
                "signal": signal,
                "evaluation": None,
            }
            forecast_id = self.storage.create_forecast(forecast)
            forecast["id"] = forecast_id
            created_forecasts.append(forecast)

        return created_forecasts

    @staticmethod
    def _evaluate_forecast_from_quotes(
        forecast: Dict[str, Any],
        current_base_price: float,
        current_quote_price: float,
    ) -> Tuple[float, str, Dict[str, Any]]:
        entry_base = float(forecast["entry_price_base"])
        entry_quote = float(forecast["entry_price_quote"])
        base_return = (float(current_base_price) / entry_base) - 1.0
        quote_return = (float(current_quote_price) / entry_quote) - 1.0

        direction = str(forecast["direction"])
        long_base = direction.startswith(f"long_{forecast['base_asset']}_short_{forecast['quote_asset']}")
        pair_return = (base_return - quote_return) if long_base else (quote_return - base_return)
        pnl_pct = round(pair_return * 100.0, 4)

        if pnl_pct > 0.05:
            outcome = "win"
        elif pnl_pct < -0.05:
            outcome = "loss"
        else:
            outcome = "flat"

        evaluation = {
            "current_base_price": float(current_base_price),
            "current_quote_price": float(current_quote_price),
            "base_return_pct": round(base_return * 100.0, 4),
            "quote_return_pct": round(quote_return * 100.0, 4),
            "pair_return_pct": pnl_pct,
            "entry_spread_ratio": float(forecast["entry_spread_ratio"]),
            "current_spread_ratio": float(current_base_price) / float(current_quote_price),
        }
        return pnl_pct, outcome, evaluation

    @staticmethod
    def _compute_next_run_iso(interval_sec: int) -> str:
        return (utc_now() + timedelta(seconds=interval_sec)).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _build_failed_signal(pair: str, base_asset: str, quote_asset: str, error: str) -> Dict[str, Any]:
        return {
            "pair": pair,
            "base_asset": base_asset,
            "quote_asset": quote_asset,
            "status": "error",
            "direction": None,
            "conviction_score": None,
            "spread_zscore": None,
            "market_regime": None,
            "divergence_state": None,
            "correlation": None,
            "base_vs_peer_average_return_pct": None,
            "backtest_results": None,
            "spec": None,
            "error": error,
        }

    @staticmethod
    def _spec_to_signal(pair: str, base_asset: str, quote_asset: str, spec: Dict[str, Any] | Any) -> Dict[str, Any]:
        if hasattr(spec, "model_dump"):
            spec_dict = spec.model_dump()
        else:
            spec_dict = spec

        pair_context = spec_dict.get("analysis", {}).get("skill_hub_pair_context", {})
        correlation_map = pair_context.get("correlation_to_base", {}) or {}
        return {
            "pair": pair,
            "base_asset": base_asset,
            "quote_asset": quote_asset,
            "status": "ok",
            "direction": spec_dict["strategy"].get("direction"),
            "conviction_score": spec_dict["strategy"].get("conviction_score"),
            "spread_zscore": spec_dict["analysis"].get("spread_zscore"),
            "market_regime": spec_dict["strategy"].get("market_regime"),
            "divergence_state": pair_context.get("divergence_state"),
            "correlation": correlation_map.get(quote_asset),
            "base_vs_peer_average_return_pct": pair_context.get("base_vs_peer_average_return_pct"),
            "backtest_results": spec_dict.get("backtest_results"),
            "spec": spec_dict,
        }
