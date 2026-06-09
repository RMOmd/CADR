from pathlib import Path

from fastapi.testclient import TestClient

from cadr.dashboard.app import create_app
from cadr.dashboard.storage import DashboardStorage


def test_dashboard_storage_roundtrip(tmp_path: Path):
    storage = DashboardStorage(str(tmp_path / "dashboard.db"))
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

    latest_run = storage.get_latest_run("default_scan")
    latest_pair = storage.get_pair_latest("BTC/ETH")

    assert latest_run["status"] == "ok"
    assert latest_run["payload"]["ok"] is True
    assert latest_pair["direction"] == "long_ETH_short_BTC"
    assert latest_pair["spec"]["strategy"]["direction"] == "long_ETH_short_BTC"


def test_dashboard_api_uses_runtime_service_override():
    app = create_app()

    class FakeStorage:
        def list_latest_pair_signals(self):
            return [{"pair": "BTC/ETH", "status": "ok"}]

        def list_recent_runs(self, limit=25):
            return [{"run_type": "default_scan", "status": "ok"}]

    class FakeService:
        def get_dashboard_snapshot(self):
            return {"stats": {"monitored_pairs": 1}, "pair_signals": [], "recent_runs": []}

        def get_pair_detail(self, pair):
            return {"latest": {"pair": pair}, "history": []}

        def run_daily_overview(self):
            return {"status": "ok"}

        def run_default_scan(self, lookback_days=90):
            return {"status": "ok", "lookback_days": lookback_days}

        def run_pair(self, base_asset, quote_asset, lookback_days=90):
            return {"pair": f"{base_asset}/{quote_asset}", "status": "ok", "lookback_days": lookback_days}

    app.state.dashboard_storage = FakeStorage()
    app.state.dashboard_service = FakeService()

    client = TestClient(app)

    assert client.get("/api/dashboard").json()["stats"]["monitored_pairs"] == 1
    assert client.get("/api/pairs").json()["pairs"][0]["pair"] == "BTC/ETH"
    assert client.get("/api/pairs/BTC%2FETH").json()["latest"]["pair"] == "BTC/ETH"
    assert client.post("/api/runs/daily-overview").json()["status"] == "ok"
    assert client.post("/api/runs/default-scan", json={"lookback_days": 120}).json()["lookback_days"] == 120
    assert client.post(
        "/api/runs/pair",
        json={"base_asset": "BTC", "quote_asset": "SOL", "lookback_days": 60},
    ).json()["pair"] == "BTC/SOL"
