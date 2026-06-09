from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import cadr.config as cfg
from cadr.dashboard.service import DashboardService
from cadr.dashboard.storage import DashboardStorage


class PairRunRequest(BaseModel):
    base_asset: str
    quote_asset: str
    lookback_days: int = Field(default=90, ge=30, le=365)


class ScanRunRequest(BaseModel):
    lookback_days: int = Field(default=90, ge=30, le=365)


def create_app() -> FastAPI:
    base_dir = Path(__file__).resolve().parent
    static_dir = base_dir / "static"
    index_path = static_dir / "index.html"

    storage = DashboardStorage(cfg.CADR_DASHBOARD_DB_PATH)
    service = DashboardService(storage=storage)

    app = FastAPI(title="CADR Dashboard", version="0.1.0")
    app.state.dashboard_service = service
    app.state.dashboard_storage = storage

    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def index():
        return FileResponse(index_path)

    @app.get("/api/dashboard")
    def get_dashboard(request: Request):
        return request.app.state.dashboard_service.get_dashboard_snapshot()

    @app.get("/api/pairs")
    def get_pairs(request: Request):
        return {"pairs": request.app.state.dashboard_storage.list_latest_pair_signals()}

    @app.get("/api/pairs/{pair:path}")
    def get_pair(pair: str, request: Request):
        try:
            return request.app.state.dashboard_service.get_pair_detail(pair)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Pair '{pair}' is not in the dashboard history.")

    @app.get("/api/runs")
    def get_runs(request: Request):
        return {"runs": request.app.state.dashboard_storage.list_recent_runs(limit=25)}

    @app.post("/api/runs/daily-overview")
    def run_daily(request: Request):
        return request.app.state.dashboard_service.run_daily_overview()

    @app.post("/api/runs/default-scan")
    def run_scan(payload: ScanRunRequest, request: Request):
        return request.app.state.dashboard_service.run_default_scan(lookback_days=payload.lookback_days)

    @app.post("/api/runs/pair")
    def run_pair(payload: PairRunRequest, request: Request):
        return request.app.state.dashboard_service.run_pair(
            base_asset=payload.base_asset,
            quote_asset=payload.quote_asset,
            lookback_days=payload.lookback_days,
        )

    return app
