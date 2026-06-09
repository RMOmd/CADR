from pathlib import Path

from fastapi.testclient import TestClient

from cadr.dashboard.app import create_app
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
