from datetime import UTC, datetime
from typing import Any, Dict, Iterable, List, Tuple

import cadr.config as cfg
from cadr.skill_hub import SkillHubClient, generate_cadr_strategy_from_skill_hub, run_daily_market_overview_preview
from cadr.skill_hub.models import DailyMarketOverview
from cadr.dashboard.storage import DashboardStorage


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class DashboardService:
    def __init__(self, storage: DashboardStorage, monitoring_pairs: Iterable[Tuple[str, str]] | None = None):
        self.storage = storage
        self.monitoring_pairs = list(monitoring_pairs or cfg.MONITORING_PAIRS)

    def run_daily_overview(self) -> Dict[str, Any]:
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
        pair = f"{base_asset}/{quote_asset}"
        started_at = utc_now_iso()
        run_id = self.storage.create_run("pair_scan", pair, "running", started_at)
        created_at = utc_now_iso()
        try:
            spec = generate_cadr_strategy_from_skill_hub(base_asset=base_asset, quote_assets=[quote_asset], lookback_days=lookback_days)
            signal = self._spec_to_signal(pair, base_asset, quote_asset, spec)
            self.storage.add_pair_signal(run_id, signal, created_at)
            self.storage.complete_run(
                run_id,
                status="ok",
                finished_at=utc_now_iso(),
                message=f"{pair} -> {signal['direction']}",
                payload=signal,
            )
            return signal
        except Exception as exc:
            failed_signal = {
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
                "error": str(exc),
            }
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
        started_at = utc_now_iso()
        run_id = self.storage.create_run("default_scan", None, "running", started_at)
        results = []
        ok_count = 0
        error_count = 0
        for base_asset, quote_asset in self.monitoring_pairs:
            pair = f"{base_asset}/{quote_asset}"
            try:
                spec = generate_cadr_strategy_from_skill_hub(base_asset=base_asset, quote_assets=[quote_asset], lookback_days=lookback_days)
                signal = self._spec_to_signal(pair, base_asset, quote_asset, spec)
                ok_count += 1
            except Exception as exc:
                signal = {
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
                    "error": str(exc),
                }
                error_count += 1

            self.storage.add_pair_signal(run_id, signal, utc_now_iso())
            results.append(signal)

        payload = {
            "total_pairs": len(results),
            "ok_count": ok_count,
            "error_count": error_count,
            "pairs": results,
        }
        self.storage.complete_run(
            run_id,
            status="ok" if error_count == 0 else "partial",
            finished_at=utc_now_iso(),
            message=f"{ok_count} ok / {error_count} errors",
            payload=payload,
        )
        return payload

    def get_dashboard_snapshot(self) -> Dict[str, Any]:
        latest_overview = self.storage.get_latest_run("daily_overview")
        latest_scan = self.storage.get_latest_run("default_scan")
        pair_signals = self.storage.list_latest_pair_signals()
        recent_runs = self.storage.list_recent_runs(limit=12)

        ok_pairs = sum(1 for signal in pair_signals if signal["status"] == "ok")
        error_pairs = sum(1 for signal in pair_signals if signal["status"] == "error")

        return {
            "latest_overview": latest_overview,
            "latest_scan": latest_scan,
            "pair_signals": pair_signals,
            "recent_runs": recent_runs,
            "stats": {
                "monitored_pairs": len(self.monitoring_pairs),
                "latest_pairs_available": len(pair_signals),
                "ok_pairs": ok_pairs,
                "error_pairs": error_pairs,
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
