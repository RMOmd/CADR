import json
from pathlib import Path
import time
from types import SimpleNamespace

import pandas as pd
from fastapi.testclient import TestClient

from cadr.dashboard.app import create_app
from cadr.dashboard.snapshots import evaluate_dashboard_snapshot, export_dashboard_snapshot
from cadr.dashboard.service import DashboardService
from cadr.dashboard.storage import DashboardStorage


def test_dashboard_storage_roundtrip(tmp_path: Path):
    storage = DashboardStorage(str(tmp_path / "dashboard.db"))
    storage.seed_watchlist(
        pairs=[("BTC", "ETH"), ("ETH", "SOL")],
        enabled=True,
        interval_sec=300,
        lookback_days=90,
        now_iso="2026-06-09T00:00:00Z",
    )

    run_id = storage.create_run("default_scan", None, "running", "2026-06-09T00:00:00Z")
    storage.add_pair_signal(
        run_id,
        {
            "pair": "BTC/ETH",
            "base_asset": "BTC",
            "quote_asset": "ETH",
            "status": "ok",
            "direction": "long_ETH_short_BTC",
            "conviction_score": 5,
            "spread_zscore": 3.74,
            "market_regime": "crisis",
            "divergence_state": "base_outperforming",
            "correlation": 0.90,
            "base_vs_peer_average_return_pct": 7.48,
            "backtest_results": None,
            "spec": {"strategy": {"direction": "long_ETH_short_BTC"}},
        },
        "2026-06-09T00:01:00Z",
    )
    storage.complete_run(run_id, "ok", "2026-06-09T00:02:00Z", message="done", payload={"ok": True})

    forecast_id = storage.create_forecast(
        {
            "pair": "BTC/ETH",
            "base_asset": "BTC",
            "quote_asset": "ETH",
            "direction": "long_ETH_short_BTC",
            "spread_zscore": 3.74,
            "conviction_score": 5,
            "market_regime": "crisis",
            "divergence_state": "base_outperforming",
            "correlation": 0.90,
            "entry_price_base": 100000.0,
            "entry_price_quote": 2500.0,
            "entry_spread_ratio": 40.0,
            "created_at": "2026-06-09T00:01:00Z",
            "due_at": "2026-06-10T00:01:00Z",
            "status": "pending",
            "signal": {"pair": "BTC/ETH"},
            "evaluation": None,
        }
    )
    storage.update_forecast_evaluation(
        forecast_id,
        evaluated_at="2026-06-10T00:01:00Z",
        status="evaluated",
        outcome="win",
        pnl_pct=2.15,
        evaluation={"pair_return_pct": 2.15},
    )

    latest_run = storage.get_latest_run("default_scan")
    latest_pair = storage.get_pair_latest("BTC/ETH")
    latest_forecast = storage.list_forecasts(limit=1)[0]

    assert latest_run["status"] == "ok"
    assert latest_run["payload"]["ok"] is True
    assert latest_pair["direction"] == "long_ETH_short_BTC"
    assert latest_pair["spec"]["strategy"]["direction"] == "long_ETH_short_BTC"
    assert latest_forecast["outcome"] == "win"
    assert storage.get_forecast_summary()["wins"] == 1


def test_dashboard_service_watchlist_update_and_forecast_export(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "dashboard.db"
    export_path = tmp_path / "forecasts.json"
    monkeypatch.setattr("cadr.config.CADR_FORECAST_EXPORT_PATH", str(export_path))

    storage = DashboardStorage(str(db_path))
    service = DashboardService(storage=storage, monitoring_pairs=[("BTC", "ETH"), ("ETH", "SOL")])

    payload = service.update_watchlist(
        pair_strings=["btc/eth", "sol/avax", "eth/ada"],
        enabled=True,
        interval_minutes=5,
        lookback_days=120,
    )

    assert [entry["pair"] for entry in payload["pairs"]] == ["BTC/ETH", "SOL/AVAX", "ETH/ADA"]
    assert payload["monitor"]["interval_sec"] == 300
    assert payload["monitor"]["lookback_days"] == 120
    assert export_path.exists()


def test_forecast_evaluation_is_cost_aware():
    forecast = {
        "pair": "BTC/ETH",
        "base_asset": "BTC",
        "quote_asset": "ETH",
        "direction": "long_BTC_short_ETH",
        "entry_price_base": 100.0,
        "entry_price_quote": 100.0,
        "entry_spread_ratio": 1.0,
        "created_at": "2026-06-09T00:00:00Z",
        "signal": {
            "spec": {
                "risk_management": {
                    "fee_bps_per_leg": 6.0,
                    "slippage_bps_per_leg": 4.0,
                    "borrow_bps_daily": 1.5,
                }
            }
        },
    }

    pnl_pct, outcome, evaluation = DashboardService._evaluate_forecast_from_quotes(
        forecast,
        current_base_price=100.2,
        current_quote_price=100.0,
        evaluated_at_iso="2026-06-10T00:00:00Z",
    )

    assert outcome == "loss"
    assert pnl_pct < 0
    assert evaluation["gross_pair_return_pct"] == 0.2
    assert evaluation["cost_drag_pct"] > evaluation["gross_pair_return_pct"]
    assert evaluation["net_pair_return_pct"] == pnl_pct


def test_record_forecasts_respects_quality_gate(tmp_path: Path, monkeypatch):
    export_path = tmp_path / "forecasts.json"
    monkeypatch.setattr("cadr.config.CADR_FORECAST_EXPORT_PATH", str(export_path))
    monkeypatch.setattr("cadr.config.CADR_FORECAST_REQUIRE_NON_DEFENSIVE", True)

    class FakeCMCClient:
        def get_quotes(self, symbols):
            return {symbol: SimpleNamespace(price=100.0 + index) for index, symbol in enumerate(symbols)}

    storage = DashboardStorage(str(tmp_path / "dashboard.db"))
    service = DashboardService(
        storage=storage,
        monitoring_pairs=[("BTC", "ETH")],
        cmc_client=FakeCMCClient(),
    )

    defensive_signal = {
        "pair": "BTC/ETH",
        "base_asset": "BTC",
        "quote_asset": "ETH",
        "status": "ok",
        "direction": "long_ETH_short_BTC",
        "conviction_score": 5,
        "spread_zscore": 3.74,
        "market_regime": "crisis",
        "divergence_state": "base_outperforming",
        "correlation": 0.91,
        "spec": {
            "analysis": {
                "skill_hub_pair_context": {"data_quality": {"aligned_days": 90}},
                "macro_context_summary": {"risk_bias": "defensive_research_only"},
            }
        },
    }
    allowed_signal = {
        **defensive_signal,
        "pair": "BTC/SOL",
        "quote_asset": "SOL",
        "spec": {
            "analysis": {
                "skill_hub_pair_context": {"data_quality": {"aligned_days": 90}},
                "macro_context_summary": {"risk_bias": "balanced_risk"},
            }
        },
    }

    skipped = service._record_forecasts([defensive_signal], "2026-06-09T00:00:00Z")
    created = service._record_forecasts([allowed_signal], "2026-06-09T00:00:00Z")

    assert skipped == []
    assert len(created) == 1
    assert created[0]["pair"] == "BTC/SOL"


def test_forecast_gate_blocks_stable_and_imbalanced_pairs(monkeypatch):
    monkeypatch.setattr("cadr.config.CADR_FORECAST_BLOCK_STABLE_LEGS", True)
    monkeypatch.setattr("cadr.config.CADR_FORECAST_MAX_ABS_ZSCORE", 8.0)
    monkeypatch.setattr("cadr.config.CADR_FORECAST_MAX_VOL_RATIO", 8.0)

    signal = {
        "pair": "TON/USDT",
        "base_asset": "TON",
        "quote_asset": "USDT",
        "status": "ok",
        "direction": "long_USDT_short_TON",
        "conviction_score": 5,
        "spread_zscore": 15.17,
        "market_regime": "crisis",
        "divergence_state": "base_outperforming",
        "correlation": 0.92,
        "spec": {
            "analysis": {
                "skill_hub_pair_context": {
                    "data_quality": {"aligned_days": 90},
                    "asset_summaries": {
                        "TON": {"realized_volatility_daily_pct": 5.87},
                        "USDT": {"realized_volatility_daily_pct": 0.02},
                    },
                },
                "macro_context_summary": {"risk_bias": "balanced_risk"},
            }
        },
    }

    gate = DashboardService._forecast_gate_status(signal)

    assert gate["eligible"] is False
    assert "stable_leg_blocked" in gate["reasons"]
    assert "zscore_above_maximum" in gate["reasons"]
    assert "volatility_imbalance_too_high" in gate["reasons"]


def test_record_forecasts_enriches_model_horizon_and_calibration(tmp_path: Path, monkeypatch):
    export_path = tmp_path / "forecasts.json"
    monkeypatch.setattr("cadr.config.CADR_FORECAST_EXPORT_PATH", str(export_path))
    monkeypatch.setattr("cadr.config.CADR_FORECAST_MIN_HORIZON_HOURS", 12)
    monkeypatch.setattr("cadr.config.CADR_FORECAST_MAX_HORIZON_HOURS", 72)

    class FakeCMCClient:
        def get_quotes(self, symbols):
            prices = {
                "BTC": 130.0,
                "SOL": 55.0,
            }
            return {symbol: SimpleNamespace(price=prices[symbol]) for symbol in symbols}

        def get_historical_ohlcv(self, symbol, days=90):
            index = pd.date_range("2026-03-01", periods=95, freq="D", tz="UTC")
            quote = pd.Series([50.0 + (i * 0.08) for i in range(len(index))], index=index)
            if symbol == "SOL":
                closes = quote
            else:
                closes = quote * 2.0 * pd.Series([1.0 + ((i % 5) - 2) * 0.002 for i in range(len(index))], index=index)
            return pd.DataFrame({"close": closes}, index=index)

    storage = DashboardStorage(str(tmp_path / "dashboard.db"))
    storage.create_forecast(
        {
            "pair": "BTC/SOL",
            "base_asset": "BTC",
            "quote_asset": "SOL",
            "direction": "long_SOL_short_BTC",
                "spread_zscore": 3.6,
            "conviction_score": 5,
            "market_regime": "crisis",
            "divergence_state": "base_outperforming",
            "correlation": 0.92,
            "entry_price_base": 120.0,
            "entry_price_quote": 52.0,
            "entry_spread_ratio": 120.0 / 52.0,
            "created_at": "2026-06-01T00:00:00Z",
            "due_at": "2026-06-02T06:00:00Z",
            "evaluated_at": "2026-06-02T00:00:00Z",
            "status": "evaluated",
            "outcome": "win",
            "pnl_pct": 1.4,
            "signal": {"pair": "BTC/SOL"},
            "evaluation": {
                "holding_days": 1.0,
                "path_summary": {"reversion_observed_day": 0.75},
            },
        }
    )
    service = DashboardService(
        storage=storage,
        monitoring_pairs=[("BTC", "SOL")],
        cmc_client=FakeCMCClient(),
    )

    signal = {
        "pair": "BTC/SOL",
        "base_asset": "BTC",
        "quote_asset": "SOL",
        "status": "ok",
        "direction": "long_SOL_short_BTC",
        "conviction_score": 5,
        "spread_zscore": 3.74,
        "market_regime": "crisis",
        "divergence_state": "base_outperforming",
        "correlation": 0.91,
        "backtest_results": {"avg_holding_period_days": 2.0},
        "spec": {
            "analysis": {
                "skill_hub_pair_context": {"data_quality": {"aligned_days": 90}},
                "macro_context_summary": {"risk_bias": "balanced_risk"},
            }
        },
    }

    created = service._record_forecasts([signal], "2026-06-09T00:00:00Z")

    assert len(created) == 1
    assert created[0]["signal"]["forecast_spread_model"]["type"] == "hedge_residual_log"
    assert created[0]["signal"]["forecast_calibration"]["sample_size"] == 1
    assert created[0]["signal"]["forecast_horizon_hours"] != 24
    assert 12 <= created[0]["signal"]["forecast_horizon_hours"] <= 72


def test_evaluate_due_forecasts_uses_path_based_monitoring(tmp_path: Path, monkeypatch):
    export_path = tmp_path / "forecasts.json"
    monkeypatch.setattr("cadr.config.CADR_FORECAST_EXPORT_PATH", str(export_path))
    monkeypatch.setattr("cadr.dashboard.service.utc_now_iso", lambda: "2026-06-11T00:00:00Z")

    class FakeCMCClient:
        def get_quotes(self, symbols):
            prices = {
                "BTC": 100.0,
                "SOL": 50.0,
            }
            return {symbol: SimpleNamespace(price=prices[symbol]) for symbol in symbols}

        def get_historical_ohlcv(self, symbol, days=90):
            index = pd.date_range("2026-06-06", periods=6, freq="D", tz="UTC")
            if symbol == "SOL":
                closes = pd.Series([50.0, 50.0, 50.0, 50.0, 50.0, 50.0], index=index)
            else:
                closes = pd.Series([100.0, 100.5, 99.5, 130.0, 102.0, 100.0], index=index)
            return pd.DataFrame({"close": closes}, index=index)

    storage = DashboardStorage(str(tmp_path / "dashboard.db"))
    service = DashboardService(
        storage=storage,
        monitoring_pairs=[("BTC", "SOL")],
        cmc_client=FakeCMCClient(),
    )
    forecast_id = storage.create_forecast(
        {
            "pair": "BTC/SOL",
            "base_asset": "BTC",
            "quote_asset": "SOL",
            "direction": "long_SOL_short_BTC",
            "spread_zscore": 3.2,
            "conviction_score": 5,
            "market_regime": "crisis",
            "divergence_state": "base_outperforming",
            "correlation": 0.91,
            "entry_price_base": 130.0,
            "entry_price_quote": 50.0,
            "entry_spread_ratio": 2.6,
            "created_at": "2026-06-09T00:00:00Z",
            "due_at": "2026-06-10T00:00:00Z",
            "status": "pending",
            "signal": {
                "pair": "BTC/SOL",
                "direction": "long_SOL_short_BTC",
                "spread_zscore": 3.2,
                "forecast_spread_model": {
                    "type": "ratio",
                    "lookback_days": 3,
                    "entry_spread_value": 2.6,
                    "entry_spread_zscore": 3.2,
                    "confirmed": True,
                },
                "spec": {
                    "analysis": {"thresholds": {"entry_zscore": 2.0, "exit_zscore": 0.5, "stop_zscore": 3.5}},
                    "risk_management": {"stop_loss_pct": 5.0},
                },
            },
            "evaluation": None,
        }
    )

    result = service.evaluate_due_forecasts()
    evaluated_forecast = storage.list_forecasts(limit=1)[0]

    assert result["evaluated"] == 1
    assert evaluated_forecast["id"] == forecast_id
    assert evaluated_forecast["status"] == "evaluated"
    assert evaluated_forecast["evaluation"]["path_summary"]["mode"] == "path_based"
    assert evaluated_forecast["evaluation"]["path_summary"]["exit_reason"] == "mean_reversion"
    assert evaluated_forecast["evaluated_at"].startswith("2026-06-10")
    assert len(evaluated_forecast["evaluation"]["path_observations"]) >= 2


def test_background_job_worker_completes_job(tmp_path: Path):
    storage = DashboardStorage(str(tmp_path / "dashboard.db"))
    service = DashboardService(storage=storage, monitoring_pairs=[("BTC", "ETH")])
    service.run_daily_overview = lambda: {"status": "ok", "message": "job done"}
    service.start_background_worker()
    try:
        job = service.submit_job("daily_overview")
        deadline = time.time() + 3
        latest = job
        while time.time() < deadline:
            latest = service.get_job(job["id"])
            if latest and latest["status"] in {"completed", "error"}:
                break
            time.sleep(0.05)
        assert latest is not None
        assert latest["status"] == "completed"
        assert latest["result"]["message"] == "job done"
    finally:
        service.stop_background_worker()


def test_snapshot_export_and_evaluation_split_execution_ready_cohort(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("cadr.config.CADR_SNAPSHOT_MAX_SIGNAL_AGE_HOURS", 48)
    monkeypatch.setattr("cadr.config.CADR_SNAPSHOT_INCLUDE_NON_WATCHLIST", False)
    monkeypatch.setattr("cadr.config.CADR_SNAPSHOT_REQUIRE_OK_STATUS", True)
    monkeypatch.setattr("cadr.config.CADR_FORECAST_REQUIRE_NON_DEFENSIVE", True)
    monkeypatch.setattr("cadr.config.CADR_CONFIRMED_MIN_EVIDENCE_SAMPLES", 1)
    monkeypatch.setattr("cadr.dashboard.snapshots.LATEST_SNAPSHOT_PATH", tmp_path / "latest_snapshot.json")
    monkeypatch.setattr("cadr.dashboard.snapshots.SNAPSHOT_DIR", tmp_path / "snapshots")
    monkeypatch.setattr("cadr.dashboard.snapshots.EVALUATION_DIR", tmp_path / "evaluations")

    storage = DashboardStorage(str(tmp_path / "dashboard.db"))
    storage.seed_watchlist(
        pairs=[("BTC", "ETH")],
        enabled=True,
        interval_sec=300,
        lookback_days=90,
        now_iso="2026-06-09T00:00:00Z",
    )
    run_id = storage.create_run("default_scan", None, "running", "2026-06-10T00:00:00Z")
    storage.add_pair_signal(
        run_id,
        {
            "pair": "BTC/ETH",
            "base_asset": "BTC",
            "quote_asset": "ETH",
            "status": "ok",
            "direction": "long_ETH_short_BTC",
            "conviction_score": 5,
            "spread_zscore": 3.1,
            "market_regime": "risk_off",
            "divergence_state": "base_outperforming",
            "correlation": 0.91,
            "base_vs_peer_average_return_pct": 7.48,
            "backtest_results": None,
            "spec": {
                    "analysis": {
                        "macro_context_summary": {"risk_bias": "balanced_risk"},
                        "demo_diagnostics": {
                            "win_rate": 0.8,
                            "total_trades": 4,
                            "profit_factor": 1.7,
                            "sharpe_ratio": 1.4,
                            "avg_profit_per_trade_pct": 1.2,
                            "sample_points": 19,
                            "quality": "limited_sample",
                        },
                        "skill_hub_pair_context": {
                            "data_quality": {"aligned_days": 90},
                            "asset_summaries": {
                            "BTC": {"realized_volatility_daily_pct": 2.0},
                            "ETH": {"realized_volatility_daily_pct": 2.5},
                        },
                    },
                }
            },
        },
        "2026-06-10T00:01:00Z",
    )
    storage.add_pair_signal(
        run_id,
        {
            "pair": "TON/USDT",
            "base_asset": "TON",
            "quote_asset": "USDT",
            "status": "ok",
            "direction": "long_USDT_short_TON",
            "conviction_score": 5,
            "spread_zscore": 14.0,
            "market_regime": "risk_off",
            "divergence_state": "base_outperforming",
            "correlation": 0.03,
            "base_vs_peer_average_return_pct": 31.0,
            "backtest_results": None,
            "spec": {
                "analysis": {
                    "macro_context_summary": {"risk_bias": "defensive_research_only"},
                    "skill_hub_pair_context": {
                        "data_quality": {"aligned_days": 90},
                        "asset_summaries": {
                            "TON": {"realized_volatility_daily_pct": 5.8},
                            "USDT": {"realized_volatility_daily_pct": 0.02},
                        },
                    },
                }
            },
        },
        "2026-06-10T00:01:00Z",
    )
    storage.complete_run(run_id, "ok", "2026-06-10T00:02:00Z", message="done", payload={"ok": True})

    class ExportCMCClient:
        def get_quotes(self, symbols):
            prices = {
                "BTC": SimpleNamespace(price=100.0),
                "ETH": SimpleNamespace(price=100.0),
                "TON": SimpleNamespace(price=1.6),
                "USDT": SimpleNamespace(price=1.0),
            }
            return {symbol: prices[symbol] for symbol in symbols}

    class EvaluationCMCClient:
        def get_quotes(self, symbols):
            prices = {
                "BTC": SimpleNamespace(price=95.0),
                "ETH": SimpleNamespace(price=105.0),
                "TON": SimpleNamespace(price=1.5),
                "USDT": SimpleNamespace(price=1.0),
            }
            return {symbol: prices[symbol] for symbol in symbols}

    export = export_dashboard_snapshot(storage, ExportCMCClient(), db_path=str(tmp_path / "dashboard.db"))
    evaluation = evaluate_dashboard_snapshot(export["latest_path"], EvaluationCMCClient())

    assert export["pair_count"] == 2
    assert export["execution_ready_pair_count"] == 1
    assert export["demo_shortlist_count"] == 1
    latest_snapshot = json.loads(Path(export["latest_path"]).read_text(encoding="utf-8"))
    assert latest_snapshot["confirmed_shortlist_count"] == 1
    assert evaluation["summary"]["total"] == 2
    assert evaluation["execution_ready_summary"]["total"] == 1
    assert evaluation["execution_ready_summary"]["wins"] == 1
    assert evaluation["excluded_reason_counts"]["pair_not_in_watchlist"] >= 1


def test_dashboard_api_uses_runtime_service_override():
    app = create_app()

    class FakeMonitorStorage:
        def get_monitor_settings(self):
            return {
                "enabled": False,
                "interval_sec": 300,
                "lookback_days": 90,
                "next_run_at": None,
                "last_started_at": None,
                "last_finished_at": None,
                "last_status": None,
                "last_message": None,
                "updated_at": "2026-06-09T00:00:00Z",
            }

    class FakeStorage:
        def list_latest_pair_signals(self):
            return [{"pair": "BTC/ETH", "status": "ok"}]

        def list_recent_runs(self, limit=25):
            return [{"run_type": "default_scan", "status": "ok"}]

    class FakeService:
        def __init__(self):
            self.storage = FakeMonitorStorage()

        def start_background_worker(self):
            return None

        def stop_background_worker(self):
            return None

        def get_dashboard_snapshot(self):
            return {
                "stats": {"monitored_pairs": 1},
                "pair_signals": [],
                "recent_runs": [],
                "snapshots": {
                    "latest_snapshot": {
                        "generated_at": "2026-06-09T00:05:00Z",
                        "latest_pair_count": 1,
                    },
                    "latest_snapshot_path": "log/cadr_dashboard_snapshot_latest.json",
                    "latest_evaluation": {
                        "evaluated_at": "2026-06-10T00:05:00Z",
                        "output_path": "log/evaluations/cadr_snapshot_evaluation.json",
                        "summary": {"wins": 1, "losses": 0, "flat": 0, "skipped": 0},
                    },
                },
            }

        def get_pair_detail(self, pair):
            return {"latest": {"pair": pair}, "history": []}

        def run_daily_overview(self):
            return {"status": "ok"}

        def run_default_scan(self, lookback_days=90):
            return {"status": "ok", "lookback_days": lookback_days}

        def run_pair(self, base_asset, quote_asset, lookback_days=90):
            return {"pair": f"{base_asset}/{quote_asset}", "status": "ok", "lookback_days": lookback_days}

        def get_watchlist_payload(self):
            return {"pairs": [{"pair": "BTC/ETH"}], "monitor": {"enabled": True}}

        def update_watchlist(self, **kwargs):
            return {"pairs": [{"pair": "BTC/ETH"}], "monitor": {"enabled": True, "interval_sec": 300}}

        def run_monitor_cycle(self, force=False):
            return {"status": "ok", "force": force}

        def list_forecasts(self, limit=20):
            return {"summary": {"pending": 1}, "items": [{"pair": "BTC/ETH"}]}

        def evaluate_due_forecasts(self):
            return {"evaluated": 1, "summary": {"wins": 1}}

        def export_dashboard_snapshot(self):
            return {"generated_at": "2026-06-09T00:05:00Z", "pair_count": 1}

        def evaluate_dashboard_snapshot(self, snapshot_path=None):
            return {"summary": {"evaluated": 1, "wins": 1, "losses": 0, "flat": 0, "skipped": 0}}

    app.state.dashboard_storage = FakeStorage()
    app.state.dashboard_service = FakeService()

    with TestClient(app) as client:
        assert client.get("/api/dashboard").json()["stats"]["monitored_pairs"] == 1
        assert client.get("/api/pairs").json()["pairs"][0]["pair"] == "BTC/ETH"
        assert client.get("/api/pairs/BTC%2FETH").json()["latest"]["pair"] == "BTC/ETH"
        assert client.post("/api/runs/daily-overview").json()["status"] == "ok"
        assert client.post("/api/runs/default-scan", json={"lookback_days": 120}).json()["lookback_days"] == 120
        assert client.post(
            "/api/runs/pair",
            json={"base_asset": "BTC", "quote_asset": "SOL", "lookback_days": 60},
        ).json()["pair"] == "BTC/SOL"
        assert client.get("/api/watchlist").json()["pairs"][0]["pair"] == "BTC/ETH"
        assert client.put(
            "/api/watchlist",
            json={
                "pairs": ["BTC/ETH", "ETH/SOL"],
                "enabled": True,
                "interval_minutes": 5,
                "lookback_days": 90,
            },
        ).json()["monitor"]["enabled"] is True
        assert client.post("/api/monitor/run").json()["force"] is True
        assert client.get("/api/forecasts").json()["items"][0]["pair"] == "BTC/ETH"
        assert client.post("/api/forecasts/evaluate", json={"force": False}).json()["evaluated"] == 1
        assert client.post("/api/snapshots/export").json()["pair_count"] == 1
        assert client.post("/api/snapshots/evaluate", json={"snapshot_path": None}).json()["summary"]["evaluated"] == 1
