from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import cadr.config as cfg
from cadr.dashboard.monitor import DashboardMonitor
from cadr.dashboard.service import DashboardService
from cadr.dashboard.storage import DashboardStorage


class PairRunRequest(BaseModel):
    base_asset: str
    quote_asset: str
    lookback_days: int = Field(default=90, ge=30, le=365)


class ScanRunRequest(BaseModel):
    lookback_days: int = Field(default=90, ge=30, le=365)


class WatchlistUpdateRequest(BaseModel):
    pairs: List[str] = Field(min_length=1)
    enabled: bool = True
    interval_minutes: int = Field(default=5, ge=3, le=60)
    lookback_days: int = Field(default=90, ge=30, le=365)


class ForecastEvaluateRequest(BaseModel):
    force: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    monitor = DashboardMonitor(app.state.dashboard_service)
    app.state.dashboard_monitor = monitor
    monitor.start()
    try:
        yield
    finally:
        monitor.stop()


def create_app() -> FastAPI:
    base_dir = Path(__file__).resolve().parent
    static_dir = base_dir / "static"
    index_path = static_dir / "index.html"

    storage = DashboardStorage(cfg.CADR_DASHBOARD_DB_PATH)
    service = DashboardService(storage=storage)

    app = FastAPI(title="CADR Dashboard", version="0.2.0", lifespan=lifespan)
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

    @app.get("/api/watchlist")
    def get_watchlist(request: Request):
        return request.app.state.dashboard_service.get_watchlist_payload()

    @app.put("/api/watchlist")
    def update_watchlist(payload: WatchlistUpdateRequest, request: Request):
        try:
            return request.app.state.dashboard_service.update_watchlist(
                pair_strings=payload.pairs,
                enabled=payload.enabled,
                interval_minutes=payload.interval_minutes,
                lookback_days=payload.lookback_days,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.post("/api/monitor/run")
    def run_monitor(request: Request):
        return request.app.state.dashboard_service.run_monitor_cycle(force=True)

    @app.get("/api/forecasts")
    def get_forecasts(request: Request, limit: int = 20):
        return request.app.state.dashboard_service.list_forecasts(limit=max(1, min(limit, 200)))

    @app.post("/api/forecasts/evaluate")
    def evaluate_forecasts(payload: ForecastEvaluateRequest, request: Request):
        if payload.force:
            return request.app.state.dashboard_service.evaluate_due_forecasts()
        return request.app.state.dashboard_service.evaluate_due_forecasts()

    return app
