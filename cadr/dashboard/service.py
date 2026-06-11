import json
import re
from copy import deepcopy
from datetime import UTC, datetime, timedelta
import math
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Lock, Thread
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import pandas as pd

import cadr.config as cfg
from cadr.analysis.divergence import compute_spread, spread_zscore
from cadr.dashboard.snapshots import evaluate_dashboard_snapshot, export_dashboard_snapshot, get_snapshot_status
from cadr.dashboard.storage import DashboardStorage
from cadr.data.cmc_client import CMCClient
from cadr.skill_hub import SkillHubClient, generate_cadr_strategy_from_skill_hub, run_daily_market_overview_preview
import cadr.strategy.signals as sig


PAIR_PATTERN = re.compile(r"^\s*([A-Za-z0-9]+)\s*[/:\-]\s*([A-Za-z0-9]+)\s*$")
STABLE_ASSETS = {"USDT", "USDC", "DAI", "FDUSD", "TUSD", "USDP"}


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
        self._job_queue: Queue = Queue()
        self._job_stop_event = Event()
        self._job_thread: Thread | None = None
        self.storage.seed_watchlist(
            pairs=monitoring_pairs or cfg.MONITORING_PAIRS,
            enabled=cfg.CADR_MONITOR_ENABLED,
            interval_sec=cfg.CADR_MONITOR_INTERVAL_SEC,
            lookback_days=cfg.CADR_MONITOR_LOOKBACK_DAYS,
            now_iso=utc_now_iso(),
        )
        self.export_forecasts_snapshot()

    def start_background_worker(self) -> None:
        if self._job_thread and self._job_thread.is_alive():
            return
        self._reconcile_incomplete_jobs()
        self._job_stop_event.clear()
        self._job_thread = Thread(target=self._job_worker_loop, name="cadr-dashboard-jobs", daemon=True)
        self._job_thread.start()

    def stop_background_worker(self) -> None:
        self._job_stop_event.set()
        self._job_queue.put(None)
        if self._job_thread and self._job_thread.is_alive():
            self._job_thread.join(timeout=3)

    def submit_job(self, job_type: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        created_at = utc_now_iso()
        job = self.storage.create_job(
            job_type,
            status="queued",
            created_at=created_at,
            params=params or {},
            message=self._job_status_message(job_type, "queued", params or {}),
        )
        self._job_queue.put(job["id"])
        return job

    def get_job(self, job_id: int) -> Dict[str, Any] | None:
        return self.storage.get_job(job_id)

    def list_active_jobs(self, limit: int = 8) -> List[Dict[str, Any]]:
        return self.storage.list_jobs(statuses=["queued", "running"], limit=limit)

    def _job_worker_loop(self) -> None:
        while not self._job_stop_event.is_set():
            try:
                job_id = self._job_queue.get(timeout=0.5)
            except Empty:
                continue

            if job_id is None:
                continue

            job = self.storage.get_job(int(job_id))
            if job is None or job["status"] != "queued":
                continue

            params = job.get("params") or {}
            job_type = str(job["job_type"])
            self.storage.start_job(
                job["id"],
                started_at=utc_now_iso(),
                message=self._job_status_message(job_type, "running", params),
            )
            try:
                result = self._execute_job(job_type, params)
                self.storage.complete_job(
                    job["id"],
                    finished_at=utc_now_iso(),
                    result=result if isinstance(result, dict) else {"value": result},
                    message=self._job_completion_message(job_type, result),
                )
            except Exception as exc:
                self.storage.fail_job(
                    job["id"],
                    finished_at=utc_now_iso(),
                    error=str(exc),
                    message=self._job_status_message(job_type, "error", params, str(exc)),
                )

    def _reconcile_incomplete_jobs(self) -> None:
        incomplete = self.storage.list_jobs(statuses=["queued", "running"], limit=200)
        for job in incomplete:
            if job["status"] == "queued":
                self._job_queue.put(job["id"])
                continue
            self.storage.fail_job(
                job["id"],
                finished_at=utc_now_iso(),
                error="Interrupted by service restart.",
                message=f"{self._job_status_message(job['job_type'], 'error', job.get('params') or {}, 'Interrupted by service restart.')}",
            )

    def _execute_job(self, job_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if job_type == "daily_overview":
            return self.run_daily_overview()
        if job_type == "default_scan":
            return self.run_default_scan(lookback_days=int(params.get("lookback_days", 90)))
        if job_type == "pair_scan":
            return self.run_pair(
                base_asset=str(params.get("base_asset", "")),
                quote_asset=str(params.get("quote_asset", "")),
                lookback_days=int(params.get("lookback_days", 90)),
            )
        if job_type == "monitor_scan":
            return self.run_monitor_cycle(force=bool(params.get("force", True)))
        if job_type == "evaluate_forecasts":
            return self.evaluate_due_forecasts()
        if job_type == "snapshot_export":
            return self.export_dashboard_snapshot()
        if job_type == "snapshot_evaluate":
            return self.evaluate_dashboard_snapshot(params.get("snapshot_path"))
        if job_type == "history_sync":
            return self.sync_asset_history(
                symbols=params.get("symbols"),
                days=int(params.get("days", 90)),
            )
        raise ValueError(f"Unsupported job type: {job_type}")

    @staticmethod
    def _job_status_message(job_type: str, status: str, params: Dict[str, Any], error: str | None = None) -> str:
        labels = {
            "daily_overview": "Daily overview",
            "default_scan": "Default scan",
            "pair_scan": f"Pair scan {params.get('base_asset', '')}/{params.get('quote_asset', '')}".strip(),
            "monitor_scan": "Watchlist monitor",
            "evaluate_forecasts": "Forecast evaluation",
            "snapshot_export": "Snapshot export",
            "snapshot_evaluate": "Snapshot evaluation",
            "history_sync": "Market history sync",
        }
        label = labels.get(job_type, job_type.replace("_", " "))
        if status == "queued":
            return f"{label} queued."
        if status == "running":
            return f"{label} is running."
        if status == "error":
            return f"{label} failed: {error or 'unknown error'}"
        return label

    @staticmethod
    def _job_completion_message(job_type: str, result: Any) -> str:
        if isinstance(result, dict):
            for key in ("message", "summary", "status"):
                value = result.get(key)
                if isinstance(value, str) and value.strip():
                    return value
        return DashboardService._job_status_message(job_type, "completed", {})

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
        all_pair_signals = self.storage.list_latest_pair_signals()
        recent_runs = self.storage.list_recent_runs(limit=12)
        monitor_settings = self.storage.get_monitor_settings()
        watchlist = self.storage.list_watchlist_pairs(enabled_only=False)
        enabled_watchlist_pairs = {pair["pair"] for pair in watchlist if pair["enabled"]}
        pair_signals = [signal for signal in all_pair_signals if signal["pair"] in enabled_watchlist_pairs]
        all_forecasts = self.storage.list_forecasts(limit=500)
        watchlist_forecasts = [forecast for forecast in all_forecasts if forecast["pair"] in enabled_watchlist_pairs]
        forecast_summary = self._summarize_forecasts(watchlist_forecasts)
        recent_forecasts = watchlist_forecasts[:8]
        snapshot_status = get_snapshot_status()
        active_jobs = self.list_active_jobs(limit=8)

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
            "active_jobs": active_jobs,
            "forecasts": {
                "summary": forecast_summary,
                "recent": recent_forecasts,
                "export_path": str(Path(cfg.CADR_FORECAST_EXPORT_PATH).resolve()),
            },
            "snapshots": snapshot_status,
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

    def get_asset_history_payload(
        self,
        symbol: str,
        *,
        quote_limit: int = 100,
        ohlcv_limit: int = 200,
    ) -> Dict[str, Any]:
        normalized = str(symbol).strip().upper()
        return {
            "symbol": normalized,
            "quote_snapshots": self.storage.list_quote_snapshots(normalized, limit=max(1, min(quote_limit, 500))),
            "ohlcv_history": self.storage.list_ohlcv_history(normalized, limit=max(1, min(ohlcv_limit, 1000))),
        }

    def sync_asset_history(
        self,
        *,
        symbols: Sequence[str] | None = None,
        days: int = 90,
    ) -> Dict[str, Any]:
        if symbols:
            requested_symbols = [str(symbol).strip().upper() for symbol in symbols if str(symbol).strip()]
        else:
            requested_symbols = sorted(
                {
                    asset
                    for base_asset, quote_asset in self.get_enabled_watchlist_pairs()
                    for asset in (base_asset, quote_asset)
                }
            )

        normalized_symbols: List[str] = []
        seen = set()
        for symbol in requested_symbols:
            if symbol in seen:
                continue
            seen.add(symbol)
            normalized_symbols.append(symbol)

        if not normalized_symbols:
            return {
                "status": "empty",
                "message": "No symbols selected for history sync.",
                "symbols": [],
                "days": max(7, min(int(days), 365)),
                "quote_symbols_fetched": 0,
                "ohlcv_points_fetched": 0,
                "errors": [],
                "historical_ohlcv_supported": None,
            }

        bounded_days = max(7, min(int(days), 365))
        captured_at = utc_now_iso()
        quotes = self._fetch_quotes_with_storage(
            normalized_symbols,
            captured_at=captured_at,
            source="history_sync_quotes",
        )

        ohlcv_points_fetched = 0
        errors: List[Dict[str, str]] = []
        for symbol in normalized_symbols:
            try:
                history = self._fetch_historical_ohlcv_with_storage(
                    symbol,
                    days=bounded_days,
                    captured_at=captured_at,
                    source="history_sync_ohlcv",
                )
                ohlcv_points_fetched += int(len(history.index))
            except Exception as exc:
                errors.append({"symbol": symbol, "error": str(exc)})

        historical_ohlcv_supported = not any(
            "doesn't support this endpoint" in (item.get("error") or "").lower()
            or "subscription plan" in (item.get("error") or "").lower()
            for item in errors
        )

        if errors and not historical_ohlcv_supported and len(quotes) > 0:
            message = (
                "Quote snapshots were saved locally, but the current CoinMarketCap API plan "
                "does not allow historical OHLCV access for this endpoint."
            )
        elif errors and len(quotes) > 0:
            message = (
                f"Quote snapshots were saved locally, but {len(errors)} symbol(s) failed during "
                "historical sync."
            )
        elif errors:
            message = f"History sync failed for {len(errors)} symbol(s)."
        else:
            message = (
                f"Saved quote snapshots for {len(quotes)} symbol(s) and fetched "
                f"{ohlcv_points_fetched} OHLCV rows."
            )

        return {
            "status": "ok" if not errors else ("partial" if quotes or ohlcv_points_fetched else "error"),
            "message": message,
            "symbols": normalized_symbols,
            "days": bounded_days,
            "quote_symbols_fetched": len(quotes),
            "ohlcv_points_fetched": ohlcv_points_fetched,
            "errors": errors,
            "historical_ohlcv_supported": historical_ohlcv_supported,
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

    def export_dashboard_snapshot(self) -> Dict[str, Any]:
        return export_dashboard_snapshot(
            self.storage,
            self.cmc_client,
            db_path=str(self.storage.db_path),
        )

    def evaluate_dashboard_snapshot(self, snapshot_path: str | None = None) -> Dict[str, Any]:
        return evaluate_dashboard_snapshot(snapshot_path, self.cmc_client)

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
        quotes = self._fetch_quotes_with_storage(symbols, captured_at=now_iso, source="forecast_evaluation_quotes")
        history_days_by_symbol: Dict[str, int] = {}
        for forecast in due_forecasts:
            lookback_days = int(self._resolve_forecast_spread_model(forecast).get("lookback_days") or 30)
            holding_days = DashboardService._holding_days_between(forecast["created_at"], now_iso)
            required_days = max(lookback_days + math.ceil(holding_days) + 5, lookback_days + 5)
            history_days_by_symbol[forecast["base_asset"]] = max(history_days_by_symbol.get(forecast["base_asset"], 0), required_days)
            history_days_by_symbol[forecast["quote_asset"]] = max(history_days_by_symbol.get(forecast["quote_asset"], 0), required_days)

        historical_prices: Dict[str, pd.DataFrame] = {}
        for symbol, days in history_days_by_symbol.items():
            try:
                historical_prices[symbol] = self._fetch_historical_ohlcv_with_storage(
                    symbol,
                    days=days,
                    captured_at=now_iso,
                    source="forecast_path_history",
                )
            except Exception:
                historical_prices[symbol] = pd.DataFrame()
        evaluated = 0
        skipped = 0

        for forecast in due_forecasts:
            base_quote = quotes.get(forecast["base_asset"])
            quote_quote = quotes.get(forecast["quote_asset"])
            if base_quote is None or quote_quote is None:
                skipped += 1
                continue

            pnl_pct, outcome, evaluation, effective_evaluated_at = self._evaluate_forecast_with_path(
                forecast,
                current_base_price=float(base_quote.price),
                current_quote_price=float(quote_quote.price),
                base_history=historical_prices.get(forecast["base_asset"], pd.DataFrame()),
                quote_history=historical_prices.get(forecast["quote_asset"], pd.DataFrame()),
                evaluated_at_iso=now_iso,
            )
            self.storage.update_forecast_evaluation(
                forecast["id"],
                evaluated_at=effective_evaluated_at,
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

    @staticmethod
    def _summarize_forecasts(forecasts: Sequence[Dict[str, Any]]) -> Dict[str, int]:
        summary = {
            "total": len(forecasts),
            "pending": 0,
            "evaluated": 0,
            "wins": 0,
            "losses": 0,
            "flat": 0,
        }
        for forecast in forecasts:
            status = str(forecast.get("status") or "")
            outcome = str(forecast.get("outcome") or "")
            if status == "pending":
                summary["pending"] += 1
            elif status == "evaluated":
                summary["evaluated"] += 1
                if outcome == "win":
                    summary["wins"] += 1
                elif outcome == "loss":
                    summary["losses"] += 1
                elif outcome == "flat":
                    summary["flat"] += 1
        return summary

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

    def _fetch_quotes_with_storage(
        self,
        symbols: Sequence[str],
        *,
        captured_at: str,
        source: str,
    ) -> Dict[str, Any]:
        normalized = sorted({str(symbol).strip().upper() for symbol in symbols if str(symbol).strip()})
        if not normalized:
            return {}
        quotes = self.cmc_client.get_quotes(normalized)
        self.storage.add_quote_snapshots(quotes, captured_at=captured_at, source=source)
        return quotes

    def _fetch_historical_ohlcv_with_storage(
        self,
        symbol: str,
        *,
        days: int,
        captured_at: str,
        source: str,
    ) -> pd.DataFrame:
        history = self.cmc_client.get_historical_ohlcv(symbol, days=days)
        if not history.empty:
            rows = []
            for timestamp, row in history.sort_index().iterrows():
                rows.append(
                    {
                        "timestamp": self._timestamp_to_iso(pd.Timestamp(timestamp)),
                        "open": row.get("open"),
                        "high": row.get("high"),
                        "low": row.get("low"),
                        "close": row.get("close"),
                        "volume": row.get("volume"),
                    }
                )
            self.storage.add_ohlcv_history(symbol, rows, captured_at=captured_at, source=source)
        return history

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
        candidates = [signal for signal in signals if self._forecast_gate_status(signal)["eligible"]]
        if not candidates:
            return []

        unique_symbols = sorted({signal["base_asset"] for signal in candidates} | {signal["quote_asset"] for signal in candidates})
        quotes = self._fetch_quotes_with_storage(unique_symbols, captured_at=created_at, source="forecast_entry_quotes")

        created_forecasts: List[Dict[str, Any]] = []
        for signal in candidates:
            if self.storage.has_pending_forecast(signal["pair"], signal["direction"], created_at):
                continue

            base_quote = quotes.get(signal["base_asset"])
            quote_quote = quotes.get(signal["quote_asset"])
            if base_quote is None or quote_quote is None:
                continue

            entry_spread_ratio = float(base_quote.price) / float(quote_quote.price)
            calibration = self._forecast_calibration_context(signal)
            spread_model = self._estimate_forecast_spread_model(
                signal,
                entry_price_base=float(base_quote.price),
                entry_price_quote=float(quote_quote.price),
            )
            if not spread_model.get("confirmed", True):
                continue

            horizon_hours = self._forecast_horizon_hours(signal, spread_model, calibration)
            due_at = (
                datetime.fromisoformat(created_at.replace("Z", "+00:00")) + timedelta(hours=horizon_hours)
            ).isoformat().replace("+00:00", "Z")
            enriched_signal = deepcopy(signal)
            enriched_signal["forecast_spread_model"] = spread_model
            enriched_signal["forecast_calibration"] = calibration
            enriched_signal["forecast_horizon_hours"] = horizon_hours
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
                "signal": enriched_signal,
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
        *,
        evaluated_at_iso: str,
    ) -> Tuple[float, str, Dict[str, Any]]:
        entry_base = float(forecast["entry_price_base"])
        entry_quote = float(forecast["entry_price_quote"])
        base_return = (float(current_base_price) / entry_base) - 1.0
        quote_return = (float(current_quote_price) / entry_quote) - 1.0

        direction = str(forecast["direction"])
        long_base = direction.startswith(f"long_{forecast['base_asset']}_short_{forecast['quote_asset']}")
        gross_pair_return = (base_return - quote_return) if long_base else (quote_return - base_return)
        holding_days = DashboardService._holding_days_between(forecast["created_at"], evaluated_at_iso)
        cost_model = DashboardService._forecast_cost_model(forecast)
        total_cost_pct = cost_model["round_trip_pair_cost_pct"] + ((cost_model["borrow_bps_daily"] / 10000.0) * holding_days)
        net_pair_return = gross_pair_return - total_cost_pct
        pnl_pct = round(net_pair_return * 100.0, 4)
        flat_band_pct = float(cfg.CADR_FORECAST_FLAT_BAND_PCT)

        if pnl_pct > flat_band_pct:
            outcome = "win"
        elif pnl_pct < -flat_band_pct:
            outcome = "loss"
        else:
            outcome = "flat"

        evaluation = {
            "holding_days": round(holding_days, 4),
            "current_base_price": float(current_base_price),
            "current_quote_price": float(current_quote_price),
            "base_return_pct": round(base_return * 100.0, 4),
            "quote_return_pct": round(quote_return * 100.0, 4),
            "gross_pair_return_pct": round(gross_pair_return * 100.0, 4),
            "cost_drag_pct": round(total_cost_pct * 100.0, 4),
            "net_pair_return_pct": pnl_pct,
            "pair_return_pct": pnl_pct,
            "flat_band_pct": flat_band_pct,
            "fee_bps_per_leg": cost_model["fee_bps_per_leg"],
            "slippage_bps_per_leg": cost_model["slippage_bps_per_leg"],
            "borrow_bps_daily": cost_model["borrow_bps_daily"],
            "entry_spread_ratio": float(forecast["entry_spread_ratio"]),
            "current_spread_ratio": float(current_base_price) / float(current_quote_price),
        }
        return pnl_pct, outcome, evaluation

    def _evaluate_forecast_with_path(
        self,
        forecast: Dict[str, Any],
        *,
        current_base_price: float,
        current_quote_price: float,
        base_history: pd.DataFrame,
        quote_history: pd.DataFrame,
        evaluated_at_iso: str,
    ) -> Tuple[float, str, Dict[str, Any], str]:
        path_frame = self._build_forecast_path_frame(
            forecast,
            base_history=base_history,
            quote_history=quote_history,
            evaluated_at_iso=evaluated_at_iso,
        )
        if path_frame.empty:
            pnl_pct, outcome, evaluation = self._evaluate_forecast_from_quotes(
                forecast,
                current_base_price=current_base_price,
                current_quote_price=current_quote_price,
                evaluated_at_iso=evaluated_at_iso,
            )
            evaluation["path_observations"] = []
            evaluation["path_summary"] = {
                "mode": "point_fallback",
                "observations_count": 0,
                "exit_reason": "horizon_expired",
            }
            return pnl_pct, outcome, evaluation, evaluated_at_iso

        thresholds = self._forecast_thresholds(forecast)
        model = self._resolve_forecast_spread_model(forecast)
        flat_band_pct = float(cfg.CADR_FORECAST_FLAT_BAND_PCT)
        entry_zscore = float(model.get("entry_spread_zscore") or forecast.get("spread_zscore") or 0.0)

        observations: List[Dict[str, Any]] = []
        first_profit_day: float | None = None
        reversion_observed_day: float | None = None
        resolved_exit_reason: str | None = None
        resolved_evaluated_at: str | None = None
        resolved_pnl_pct: float | None = None
        resolved_outcome: str | None = None
        resolved_evaluation: Dict[str, Any] | None = None

        for timestamp, row in path_frame.iterrows():
            point_iso = self._timestamp_to_iso(timestamp)
            pnl_pct, point_outcome, point_evaluation = self._evaluate_forecast_from_quotes(
                forecast,
                current_base_price=float(row["base_price"]),
                current_quote_price=float(row["quote_price"]),
                evaluated_at_iso=point_iso,
            )
            point_zscore = row["spread_zscore"]
            point_evaluation["path_spread_value"] = round(float(row["spread_value"]), 8)
            if pd.notna(point_zscore):
                point_evaluation["path_spread_zscore"] = round(float(point_zscore), 4)

            observation = {
                "timestamp": point_iso,
                "holding_days": point_evaluation["holding_days"],
                "base_price": round(float(row["base_price"]), 8),
                "quote_price": round(float(row["quote_price"]), 8),
                "spread_value": round(float(row["spread_value"]), 8),
                "spread_zscore": None if pd.isna(point_zscore) else round(float(point_zscore), 4),
                "pnl_pct": pnl_pct,
                "outcome": point_outcome,
            }
            observations.append(observation)

            if first_profit_day is None and pnl_pct > flat_band_pct:
                first_profit_day = float(point_evaluation["holding_days"])

            hit_take_profit = pd.notna(point_zscore) and sig.exit_signal(float(point_zscore), entry_zscore, thresholds["exit_zscore"])
            hit_stop = (pnl_pct / 100.0) <= -thresholds["stop_loss_pct"] or (
                pd.notna(point_zscore) and abs(float(point_zscore)) >= thresholds["stop_zscore"]
            )

            if hit_take_profit and reversion_observed_day is None:
                reversion_observed_day = float(point_evaluation["holding_days"])

            if hit_stop or hit_take_profit:
                resolved_exit_reason = "stop_loss" if hit_stop else "mean_reversion"
                resolved_evaluated_at = point_iso
                resolved_pnl_pct = pnl_pct
                resolved_outcome = "loss" if hit_stop else ("win" if pnl_pct > flat_band_pct else "flat")
                resolved_evaluation = point_evaluation
                break

        final_spread_value = self._spread_value_for_model(current_base_price, current_quote_price, model)
        final_spread_zscore = self._current_spread_zscore_from_model(final_spread_value, model)
        if resolved_evaluation is None:
            resolved_pnl_pct, resolved_outcome, resolved_evaluation = self._evaluate_forecast_from_quotes(
                forecast,
                current_base_price=current_base_price,
                current_quote_price=current_quote_price,
                evaluated_at_iso=evaluated_at_iso,
            )
            resolved_exit_reason = "horizon_expired"
            resolved_evaluated_at = evaluated_at_iso
            final_observation = {
                "timestamp": evaluated_at_iso,
                "holding_days": resolved_evaluation["holding_days"],
                "base_price": round(float(current_base_price), 8),
                "quote_price": round(float(current_quote_price), 8),
                "spread_value": round(float(final_spread_value), 8),
                "spread_zscore": None if final_spread_zscore is None else round(float(final_spread_zscore), 4),
                "pnl_pct": resolved_pnl_pct,
                "outcome": resolved_outcome,
            }
            if not observations or observations[-1]["timestamp"] != evaluated_at_iso:
                observations.append(final_observation)

        pnls = [float(item["pnl_pct"]) for item in observations]
        last_observation = observations[-1]
        best_observation = max(observations, key=lambda item: item["pnl_pct"])
        worst_observation = min(observations, key=lambda item: item["pnl_pct"])
        resolved_evaluation["path_observations"] = observations
        resolved_evaluation["path_summary"] = {
            "mode": "path_based",
            "path_model": model.get("type", "ratio"),
            "observations_count": len(observations),
            "entry_spread_zscore": round(entry_zscore, 4),
            "max_pnl_pct": round(max(pnls), 4),
            "min_pnl_pct": round(min(pnls), 4),
            "best_observed_at": best_observation["timestamp"],
            "worst_observed_at": worst_observation["timestamp"],
            "first_profit_day": None if first_profit_day is None else round(first_profit_day, 4),
            "reversion_observed_day": None if reversion_observed_day is None else round(reversion_observed_day, 4),
            "exit_reason": resolved_exit_reason,
            "exit_at": resolved_evaluated_at,
            "final_spread_value": round(float(last_observation["spread_value"]), 8),
            "final_spread_zscore": last_observation["spread_zscore"],
        }
        return resolved_pnl_pct, resolved_outcome, resolved_evaluation, resolved_evaluated_at

    def _build_forecast_path_frame(
        self,
        forecast: Dict[str, Any],
        *,
        base_history: pd.DataFrame,
        quote_history: pd.DataFrame,
        evaluated_at_iso: str,
    ) -> pd.DataFrame:
        if base_history.empty or quote_history.empty:
            return pd.DataFrame()

        frame = pd.DataFrame(
            {
                "base_price": base_history.get("close"),
                "quote_price": quote_history.get("close"),
            }
        ).dropna()
        if frame.empty:
            return frame
        frame.index = pd.to_datetime(frame.index, utc=True)

        model = self._resolve_forecast_spread_model(forecast)
        spread = self._build_spread_series(frame["base_price"], frame["quote_price"], model)
        if spread.empty:
            return pd.DataFrame()

        lookback_days = max(5, int(model.get("lookback_days") or 30))
        zscores = spread_zscore(spread, lookback=min(lookback_days, max(5, len(spread) - 1)))
        frame = frame.loc[spread.index].copy()
        frame["spread_value"] = spread
        frame["spread_zscore"] = zscores

        created_ts = self._to_utc_timestamp(forecast["created_at"]).floor("D")
        evaluated_ts = self._to_utc_timestamp(evaluated_at_iso).ceil("D")
        frame = frame[(frame.index >= created_ts) & (frame.index <= evaluated_ts)]
        return frame

    def _estimate_forecast_spread_model(
        self,
        signal: Dict[str, Any],
        *,
        entry_price_base: float,
        entry_price_quote: float,
    ) -> Dict[str, Any]:
        spec = signal.get("spec") or {}
        pair_context = ((spec.get("analysis") or {}).get("skill_hub_pair_context") or {})
        data_quality = pair_context.get("data_quality") or {}
        aligned_days = int(data_quality.get("aligned_days") or cfg.CADR_MONITOR_LOOKBACK_DAYS)
        lookback_days = max(30, min(180, aligned_days))

        captured_at = utc_now_iso()
        try:
            base_history = self._fetch_historical_ohlcv_with_storage(
                signal["base_asset"],
                days=lookback_days + 5,
                captured_at=captured_at,
                source="forecast_model_history",
            )
            quote_history = self._fetch_historical_ohlcv_with_storage(
                signal["quote_asset"],
                days=lookback_days + 5,
                captured_at=captured_at,
                source="forecast_model_history",
            )
        except Exception:
            base_history = pd.DataFrame()
            quote_history = pd.DataFrame()

        if not base_history.empty and not quote_history.empty:
            history = pd.DataFrame(
                {
                    "base_price": base_history.get("close"),
                    "quote_price": quote_history.get("close"),
                }
            ).dropna()
            history = history.tail(lookback_days)
            if len(history) >= 30:
                log_base = history["base_price"].map(math.log)
                log_quote = history["quote_price"].map(math.log)
                quote_var = float(log_quote.var())
                if quote_var > 0:
                    hedge_ratio = float(log_base.cov(log_quote) / quote_var)
                    intercept = float(log_base.mean() - hedge_ratio * log_quote.mean())
                    residual_series = log_base - ((log_quote * hedge_ratio) + intercept)
                    residual_mean = float(residual_series.mean())
                    residual_std = float(residual_series.std(ddof=1))
                    if residual_std > 0:
                        entry_spread_value = math.log(entry_price_base) - ((math.log(entry_price_quote) * hedge_ratio) + intercept)
                        entry_spread_zscore = (entry_spread_value - residual_mean) / residual_std
                        expected_direction = (
                            f"long_{signal['quote_asset']}_short_{signal['base_asset']}"
                            if entry_spread_zscore > 0
                            else f"long_{signal['base_asset']}_short_{signal['quote_asset']}"
                        )
                        confirmed = (
                            abs(entry_spread_zscore) >= max(1.5, cfg.Z_SCORE_ENTRY_THRESHOLD * 0.75)
                            and signal.get("direction") == expected_direction
                        )
                        return {
                            "type": "hedge_residual_log",
                            "lookback_days": lookback_days,
                            "sample_size": len(history),
                            "hedge_ratio": round(hedge_ratio, 6),
                            "intercept": round(intercept, 6),
                            "spread_mean": round(residual_mean, 8),
                            "spread_std": round(residual_std, 8),
                            "entry_spread_value": round(entry_spread_value, 8),
                            "entry_spread_zscore": round(entry_spread_zscore, 4),
                            "confirmed": confirmed,
                        }

        fallback_entry_spread = float(entry_price_base) / float(entry_price_quote)
        return {
            "type": "ratio",
            "lookback_days": min(lookback_days, 30),
            "entry_spread_value": round(fallback_entry_spread, 8),
            "entry_spread_zscore": signal.get("spread_zscore"),
            "confirmed": True,
        }

    def _forecast_calibration_context(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        bucket = self._forecast_bucket(signal.get("spread_zscore"))
        regime = signal.get("market_regime")
        pair = signal.get("pair")
        historical = self.storage.list_forecasts(limit=500, status="evaluated")

        matched: List[Dict[str, Any]] = []
        pair_matched: List[Dict[str, Any]] = []
        for forecast in historical:
            if self._forecast_bucket(forecast.get("spread_zscore")) != bucket:
                continue
            if regime and forecast.get("market_regime") != regime:
                continue
            matched.append(forecast)
            if pair and forecast.get("pair") == pair:
                pair_matched.append(forecast)

        source = pair_matched if pair_matched else matched
        evaluations = [forecast.get("evaluation") or {} for forecast in source]
        wins = sum(1 for forecast in source if forecast.get("outcome") == "win")
        avg_pnl_pct = self._average([forecast.get("pnl_pct") for forecast in source])
        avg_holding_days = self._average([evaluation.get("holding_days") for evaluation in evaluations])
        avg_reversion_days = self._average(
            [
                (evaluation.get("path_summary") or {}).get("reversion_observed_day")
                for evaluation in evaluations
            ]
        )

        return {
            "bucket": bucket,
            "market_regime": regime,
            "sample_size": len(source),
            "same_pair_sample_size": len(pair_matched),
            "win_rate": round((wins / len(source)) if source else 0.0, 4),
            "avg_pnl_pct": avg_pnl_pct,
            "avg_holding_days": avg_holding_days,
            "avg_reversion_days": avg_reversion_days,
        }

    @staticmethod
    def _forecast_horizon_hours(
        signal: Dict[str, Any],
        spread_model: Dict[str, Any],
        calibration: Dict[str, Any],
    ) -> int:
        base_days = max(cfg.CADR_FORECAST_HORIZON_HOURS, 1) / 24.0
        backtest = signal.get("backtest_results") or ((signal.get("spec") or {}).get("backtest_results") or {})
        backtest_holding_days = DashboardService._coerce_float(backtest.get("avg_holding_period_days"))
        historical_holding_days = DashboardService._coerce_float(calibration.get("avg_holding_days"))
        historical_reversion_days = DashboardService._coerce_float(calibration.get("avg_reversion_days"))

        weighted_days = 0.0
        total_weight = 0.0
        for value, weight in (
            (historical_reversion_days, 0.55),
            (historical_holding_days, 0.25),
            (backtest_holding_days, 0.20),
        ):
            if value is not None and value > 0:
                weighted_days += value * weight
                total_weight += weight

        reference_days = (weighted_days / total_weight) if total_weight else base_days
        conviction = int(signal.get("conviction_score") or cfg.CADR_FORECAST_MIN_CONVICTION)
        correlation = DashboardService._coerce_float(signal.get("correlation")) or cfg.CADR_FORECAST_MIN_CORRELATION
        entry_zscore = abs(
            DashboardService._coerce_float(spread_model.get("entry_spread_zscore"))
            or DashboardService._coerce_float(signal.get("spread_zscore"))
            or cfg.Z_SCORE_ENTRY_THRESHOLD
        )
        win_rate = DashboardService._coerce_float(calibration.get("win_rate")) or 0.5

        strength_components = [
            min(1.0, max(0.0, conviction / 5.0)),
            min(1.0, entry_zscore / max(cfg.Z_SCORE_ENTRY_THRESHOLD + 1.0, 1.0)),
            min(1.0, max(0.0, correlation)),
            min(1.0, max(0.0, win_rate)),
        ]
        strength_score = sum(strength_components) / len(strength_components)
        scale = 1.15 - (0.35 * strength_score)
        if int(calibration.get("sample_size") or 0) >= 3 and win_rate < 0.45:
            scale += 0.10

        horizon_hours = reference_days * 24.0 * scale
        horizon_hours = min(float(cfg.CADR_FORECAST_MAX_HORIZON_HOURS), max(float(cfg.CADR_FORECAST_MIN_HORIZON_HOURS), horizon_hours))
        return max(1, int(round(horizon_hours)))

    @staticmethod
    def _forecast_thresholds(forecast: Dict[str, Any]) -> Dict[str, float]:
        signal = forecast.get("signal") or {}
        spec = signal.get("spec") or {}
        analysis = spec.get("analysis") or {}
        thresholds = analysis.get("thresholds") or {}
        risk = spec.get("risk_management") or {}
        raw_stop_loss_pct = DashboardService._coerce_float(risk.get("stop_loss_pct"))
        stop_loss_pct = cfg.DEFAULT_STOP_LOSS_PCT if raw_stop_loss_pct is None else (
            raw_stop_loss_pct / 100.0 if raw_stop_loss_pct > 1 else raw_stop_loss_pct
        )
        return {
            "entry_zscore": float(thresholds.get("entry_zscore", cfg.Z_SCORE_ENTRY_THRESHOLD)),
            "exit_zscore": float(thresholds.get("exit_zscore", cfg.Z_SCORE_EXIT_THRESHOLD)),
            "stop_zscore": float(thresholds.get("stop_zscore", cfg.Z_SCORE_STOP_THRESHOLD)),
            "stop_loss_pct": float(stop_loss_pct),
        }

    @staticmethod
    def _resolve_forecast_spread_model(forecast: Dict[str, Any]) -> Dict[str, Any]:
        signal = forecast.get("signal") or {}
        model = signal.get("forecast_spread_model") or {}
        if model:
            return model
        return {
            "type": "ratio",
            "lookback_days": 30,
            "entry_spread_value": forecast.get("entry_spread_ratio"),
            "entry_spread_zscore": forecast.get("spread_zscore"),
            "confirmed": True,
        }

    @staticmethod
    def _build_spread_series(base_prices: pd.Series, quote_prices: pd.Series, model: Dict[str, Any]) -> pd.Series:
        if model.get("type") == "hedge_residual_log":
            hedge_ratio = float(model.get("hedge_ratio", 1.0))
            intercept = float(model.get("intercept", 0.0))
            df = pd.concat([base_prices, quote_prices], axis=1).dropna()
            if df.empty:
                return pd.Series(dtype=float)
            log_base = df.iloc[:, 0].map(math.log)
            log_quote = df.iloc[:, 1].map(math.log)
            return log_base - ((log_quote * hedge_ratio) + intercept)
        return compute_spread(base_prices, quote_prices, method="ratio")

    @staticmethod
    def _spread_value_for_model(base_price: float, quote_price: float, model: Dict[str, Any]) -> float:
        if model.get("type") == "hedge_residual_log":
            hedge_ratio = float(model.get("hedge_ratio", 1.0))
            intercept = float(model.get("intercept", 0.0))
            return math.log(float(base_price)) - ((math.log(float(quote_price)) * hedge_ratio) + intercept)
        return float(base_price) / float(quote_price)

    @staticmethod
    def _current_spread_zscore_from_model(spread_value: float, model: Dict[str, Any]) -> float | None:
        spread_mean = DashboardService._coerce_float(model.get("spread_mean"))
        spread_std = DashboardService._coerce_float(model.get("spread_std"))
        if spread_mean is None or spread_std is None or spread_std <= 0:
            return None
        return (spread_value - spread_mean) / spread_std

    @staticmethod
    def _forecast_bucket(spread_zscore: Any) -> str:
        magnitude = abs(DashboardService._coerce_float(spread_zscore) or 0.0)
        if magnitude < 2.5:
            return "entry_2_2.5"
        if magnitude < 3.5:
            return "entry_2.5_3.5"
        return "entry_3.5_plus"

    @staticmethod
    def _average(values: Sequence[Any]) -> float | None:
        normalized = [float(value) for value in values if DashboardService._coerce_float(value) is not None]
        if not normalized:
            return None
        return round(sum(normalized) / len(normalized), 4)

    @staticmethod
    def _coerce_float(value: Any) -> float | None:
        try:
            if value is None:
                return None
            number = float(value)
            if math.isfinite(number):
                return number
        except (TypeError, ValueError):
            return None
        return None

    @staticmethod
    def _to_utc_timestamp(value: str | datetime | pd.Timestamp) -> pd.Timestamp:
        timestamp = pd.Timestamp(value)
        if timestamp.tzinfo is None:
            return timestamp.tz_localize("UTC")
        return timestamp.tz_convert("UTC")

    @staticmethod
    def _timestamp_to_iso(timestamp: pd.Timestamp) -> str:
        utc_timestamp = DashboardService._to_utc_timestamp(timestamp)
        return utc_timestamp.isoformat().replace("+00:00", "Z")

    @staticmethod
    def _holding_days_between(started_at_iso: str, finished_at_iso: str) -> float:
        started_at = datetime.fromisoformat(started_at_iso.replace("Z", "+00:00"))
        finished_at = datetime.fromisoformat(finished_at_iso.replace("Z", "+00:00"))
        return max(0.0, (finished_at - started_at).total_seconds() / 86400.0)

    @staticmethod
    def _forecast_cost_model(forecast: Dict[str, Any]) -> Dict[str, float]:
        signal = forecast.get("signal") or {}
        spec = signal.get("spec") or {}
        risk = spec.get("risk_management") or {}
        fee_bps = float(risk.get("fee_bps_per_leg", cfg.BACKTEST_FEE_BPS_PER_LEG))
        slippage_bps = float(risk.get("slippage_bps_per_leg", cfg.BACKTEST_SLIPPAGE_BPS_PER_LEG))
        borrow_bps_daily = float(risk.get("borrow_bps_daily", cfg.BACKTEST_BORROW_BPS_DAILY))
        one_way_pair_cost_pct = ((fee_bps + slippage_bps) * 2.0) / 10000.0
        return {
            "fee_bps_per_leg": fee_bps,
            "slippage_bps_per_leg": slippage_bps,
            "borrow_bps_daily": borrow_bps_daily,
            "one_way_pair_cost_pct": one_way_pair_cost_pct,
            "round_trip_pair_cost_pct": one_way_pair_cost_pct * 2.0,
        }

    @staticmethod
    def _forecast_gate_status(signal: Dict[str, Any]) -> Dict[str, Any]:
        reasons: List[str] = []
        base_asset = str(signal.get("base_asset") or "").upper()
        quote_asset = str(signal.get("quote_asset") or "").upper()

        if signal.get("status") != "ok":
            reasons.append("signal_not_ok")
        if not signal.get("direction"):
            reasons.append("missing_direction")

        if cfg.CADR_FORECAST_BLOCK_STABLE_LEGS and (base_asset in STABLE_ASSETS or quote_asset in STABLE_ASSETS):
            reasons.append("stable_leg_blocked")

        spread_zscore = signal.get("spread_zscore")
        if spread_zscore is None:
            reasons.append("missing_spread_zscore")
        elif abs(float(spread_zscore)) < cfg.Z_SCORE_ENTRY_THRESHOLD:
            reasons.append("zscore_below_entry_threshold")
        elif abs(float(spread_zscore)) > cfg.CADR_FORECAST_MAX_ABS_ZSCORE:
            reasons.append("zscore_above_maximum")

        conviction = signal.get("conviction_score")
        if conviction is None:
            reasons.append("missing_conviction")
        elif int(conviction) < cfg.CADR_FORECAST_MIN_CONVICTION:
            reasons.append("conviction_below_minimum")

        correlation = signal.get("correlation")
        if correlation is None:
            reasons.append("missing_correlation")
        elif float(correlation) < cfg.CADR_FORECAST_MIN_CORRELATION:
            reasons.append("correlation_below_minimum")

        spec = signal.get("spec") or {}
        pair_context = ((spec.get("analysis") or {}).get("skill_hub_pair_context") or {})
        data_quality = pair_context.get("data_quality") or {}
        asset_summaries = pair_context.get("asset_summaries") or {}
        aligned_days = data_quality.get("aligned_days")
        if aligned_days is None:
            reasons.append("missing_aligned_days")
        elif int(aligned_days) < cfg.CADR_FORECAST_MIN_ALIGNED_DAYS:
            reasons.append("aligned_days_below_minimum")

        base_summary = asset_summaries.get(base_asset) or {}
        quote_summary = asset_summaries.get(quote_asset) or {}
        base_vol = DashboardService._coerce_float(base_summary.get("realized_volatility_daily_pct"))
        quote_vol = DashboardService._coerce_float(quote_summary.get("realized_volatility_daily_pct"))
        if base_vol is not None and quote_vol is not None and min(base_vol, quote_vol) > 0:
            vol_ratio = max(base_vol, quote_vol) / min(base_vol, quote_vol)
            if vol_ratio > float(cfg.CADR_FORECAST_MAX_VOL_RATIO):
                reasons.append("volatility_imbalance_too_high")

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
        }

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
