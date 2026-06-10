import json
import math
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


_UNSET = object()


class DashboardStorage:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self.connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_type TEXT NOT NULL,
                    pair TEXT,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    message TEXT,
                    error TEXT,
                    payload_json TEXT
                );

                CREATE TABLE IF NOT EXISTS pair_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    pair TEXT NOT NULL,
                    base_asset TEXT NOT NULL,
                    quote_asset TEXT NOT NULL,
                    status TEXT NOT NULL,
                    direction TEXT,
                    conviction_score INTEGER,
                    spread_zscore REAL,
                    market_regime TEXT,
                    divergence_state TEXT,
                    correlation REAL,
                    base_vs_peer_average_return_pct REAL,
                    backtest_json TEXT,
                    spec_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(run_id) REFERENCES runs(id)
                );

                CREATE TABLE IF NOT EXISTS watchlist_pairs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    base_asset TEXT NOT NULL,
                    quote_asset TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    position INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(base_asset, quote_asset)
                );

                CREATE TABLE IF NOT EXISTS monitor_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    enabled INTEGER NOT NULL DEFAULT 1,
                    interval_sec INTEGER NOT NULL,
                    lookback_days INTEGER NOT NULL,
                    next_run_at TEXT,
                    last_started_at TEXT,
                    last_finished_at TEXT,
                    last_status TEXT,
                    last_message TEXT,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS trade_forecasts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pair TEXT NOT NULL,
                    base_asset TEXT NOT NULL,
                    quote_asset TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    spread_zscore REAL,
                    conviction_score INTEGER,
                    market_regime TEXT,
                    divergence_state TEXT,
                    correlation REAL,
                    entry_price_base REAL NOT NULL,
                    entry_price_quote REAL NOT NULL,
                    entry_spread_ratio REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    due_at TEXT NOT NULL,
                    evaluated_at TEXT,
                    status TEXT NOT NULL,
                    outcome TEXT,
                    pnl_pct REAL,
                    signal_json TEXT,
                    evaluation_json TEXT
                );

                CREATE TABLE IF NOT EXISTS background_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    params_json TEXT,
                    result_json TEXT,
                    error TEXT,
                    message TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_runs_type_id
                ON runs (run_type, id DESC);

                CREATE INDEX IF NOT EXISTS idx_pair_signals_pair_id
                ON pair_signals (pair, id DESC);

                CREATE INDEX IF NOT EXISTS idx_trade_forecasts_status_due
                ON trade_forecasts (status, due_at, id);

                CREATE INDEX IF NOT EXISTS idx_trade_forecasts_pair_status
                ON trade_forecasts (pair, direction, status, due_at);

                CREATE INDEX IF NOT EXISTS idx_background_jobs_status_created
                ON background_jobs (status, created_at, id);
                """
            )
            conn.execute("PRAGMA journal_mode=WAL")

    def seed_watchlist(
        self,
        pairs: Iterable[Tuple[str, str]],
        enabled: bool,
        interval_sec: int,
        lookback_days: int,
        now_iso: str,
    ) -> None:
        normalized = self._normalize_pairs(pairs)
        with self.connection() as conn:
            existing_count = conn.execute("SELECT COUNT(*) FROM watchlist_pairs").fetchone()[0]
            if existing_count == 0:
                conn.executemany(
                    """
                    INSERT INTO watchlist_pairs (
                        base_asset, quote_asset, enabled, position, created_at, updated_at
                    )
                    VALUES (?, ?, 1, ?, ?, ?)
                    """,
                    [
                        (base_asset, quote_asset, index, now_iso, now_iso)
                        for index, (base_asset, quote_asset) in enumerate(normalized, start=1)
                    ],
                )

            exists = conn.execute("SELECT 1 FROM monitor_settings WHERE id = 1").fetchone()
            if not exists:
                conn.execute(
                    """
                    INSERT INTO monitor_settings (
                        id, enabled, interval_sec, lookback_days, updated_at
                    )
                    VALUES (1, ?, ?, ?, ?)
                    """,
                    (1 if enabled else 0, interval_sec, lookback_days, now_iso),
                )

    def create_run(self, run_type: str, pair: Optional[str], status: str, started_at: str) -> int:
        with self.connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO runs (run_type, pair, status, started_at)
                VALUES (?, ?, ?, ?)
                """,
                (run_type, pair, status, started_at),
            )
            return int(cur.lastrowid)

    def complete_run(
        self,
        run_id: int,
        status: str,
        finished_at: str,
        message: Optional[str] = None,
        error: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                UPDATE runs
                SET status = ?, finished_at = ?, message = ?, error = ?, payload_json = ?
                WHERE id = ?
                """,
                (
                    status,
                    finished_at,
                    message,
                    error,
                    json.dumps(payload) if payload is not None else None,
                    run_id,
                ),
            )

    def add_pair_signal(self, run_id: int, signal: Dict[str, Any], created_at: str) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO pair_signals (
                    run_id, pair, base_asset, quote_asset, status, direction,
                    conviction_score, spread_zscore, market_regime, divergence_state,
                    correlation, base_vs_peer_average_return_pct, backtest_json,
                    spec_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    signal["pair"],
                    signal["base_asset"],
                    signal["quote_asset"],
                    signal["status"],
                    signal.get("direction"),
                    signal.get("conviction_score"),
                    signal.get("spread_zscore"),
                    signal.get("market_regime"),
                    signal.get("divergence_state"),
                    signal.get("correlation"),
                    signal.get("base_vs_peer_average_return_pct"),
                    json.dumps(signal.get("backtest_results")) if signal.get("backtest_results") is not None else None,
                    json.dumps(signal.get("spec")) if signal.get("spec") is not None else None,
                    created_at,
                ),
            )

    def get_latest_run(self, run_type: str) -> Optional[Dict[str, Any]]:
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM runs
                WHERE run_type = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (run_type,),
            ).fetchone()
            return self._row_to_run(row) if row else None

    def list_recent_runs(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM runs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [self._row_to_run(row) for row in rows]

    def list_latest_pair_signals(self) -> List[Dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT ps.*
                FROM pair_signals ps
                JOIN (
                    SELECT pair, MAX(id) AS max_id
                    FROM pair_signals
                    GROUP BY pair
                ) latest
                ON latest.max_id = ps.id
                ORDER BY ABS(COALESCE(ps.spread_zscore, 0)) DESC, ps.id DESC
                """
            ).fetchall()
            return [self._row_to_signal(row) for row in rows]

    def get_pair_history(self, pair: str, limit: int = 10) -> List[Dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM pair_signals
                WHERE pair = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (pair, limit),
            ).fetchall()
            return [self._row_to_signal(row) for row in rows]

    def get_pair_latest(self, pair: str) -> Optional[Dict[str, Any]]:
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM pair_signals
                WHERE pair = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (pair,),
            ).fetchone()
            return self._row_to_signal(row) if row else None

    def list_watchlist_pairs(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        query = """
            SELECT *
            FROM watchlist_pairs
            {where_clause}
            ORDER BY position ASC, id ASC
        """
        where_clause = "WHERE enabled = 1" if enabled_only else ""
        with self.connection() as conn:
            rows = conn.execute(query.format(where_clause=where_clause)).fetchall()
            return [self._row_to_watchlist_pair(row) for row in rows]

    def replace_watchlist(self, pairs: Iterable[Tuple[str, str]], now_iso: str) -> List[Dict[str, Any]]:
        normalized = self._normalize_pairs(pairs)
        with self.connection() as conn:
            conn.execute("DELETE FROM watchlist_pairs")
            conn.executemany(
                """
                INSERT INTO watchlist_pairs (
                    base_asset, quote_asset, enabled, position, created_at, updated_at
                )
                VALUES (?, ?, 1, ?, ?, ?)
                """,
                [
                    (base_asset, quote_asset, index, now_iso, now_iso)
                    for index, (base_asset, quote_asset) in enumerate(normalized, start=1)
                ],
            )
        return self.list_watchlist_pairs(enabled_only=False)

    def get_monitor_settings(self) -> Dict[str, Any]:
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM monitor_settings
                WHERE id = 1
                """
            ).fetchone()
            if row is None:
                raise RuntimeError("Monitor settings were not initialized.")
            return self._row_to_monitor_settings(row)

    def update_monitor_settings(
        self,
        *,
        enabled: Optional[bool] = None,
        interval_sec: Optional[int] = None,
        lookback_days: Optional[int] = None,
        next_run_at: Optional[str] = None,
        last_started_at: Optional[str] = None,
        last_finished_at: Optional[str] = None,
        last_status: Optional[str] = None,
        last_message: Optional[str] = None,
        now_iso: str,
    ) -> Dict[str, Any]:
        current = self.get_monitor_settings()
        payload = {
            "enabled": current["enabled"] if enabled is None else enabled,
            "interval_sec": current["interval_sec"] if interval_sec is None else interval_sec,
            "lookback_days": current["lookback_days"] if lookback_days is None else lookback_days,
            "next_run_at": current["next_run_at"] if next_run_at is None else next_run_at,
            "last_started_at": current["last_started_at"] if last_started_at is None else last_started_at,
            "last_finished_at": current["last_finished_at"] if last_finished_at is None else last_finished_at,
            "last_status": current["last_status"] if last_status is None else last_status,
            "last_message": current["last_message"] if last_message is None else last_message,
        }
        with self.connection() as conn:
            conn.execute(
                """
                UPDATE monitor_settings
                SET enabled = ?,
                    interval_sec = ?,
                    lookback_days = ?,
                    next_run_at = ?,
                    last_started_at = ?,
                    last_finished_at = ?,
                    last_status = ?,
                    last_message = ?,
                    updated_at = ?
                WHERE id = 1
                """,
                (
                    1 if payload["enabled"] else 0,
                    payload["interval_sec"],
                    payload["lookback_days"],
                    payload["next_run_at"],
                    payload["last_started_at"],
                    payload["last_finished_at"],
                    payload["last_status"],
                    payload["last_message"],
                    now_iso,
                ),
            )
        return self.get_monitor_settings()

    def create_forecast(self, forecast: Dict[str, Any]) -> int:
        with self.connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO trade_forecasts (
                    pair, base_asset, quote_asset, direction, spread_zscore,
                    conviction_score, market_regime, divergence_state, correlation,
                    entry_price_base, entry_price_quote, entry_spread_ratio,
                    created_at, due_at, evaluated_at, status, outcome, pnl_pct,
                    signal_json, evaluation_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    forecast["pair"],
                    forecast["base_asset"],
                    forecast["quote_asset"],
                    forecast["direction"],
                    forecast.get("spread_zscore"),
                    forecast.get("conviction_score"),
                    forecast.get("market_regime"),
                    forecast.get("divergence_state"),
                    forecast.get("correlation"),
                    forecast["entry_price_base"],
                    forecast["entry_price_quote"],
                    forecast["entry_spread_ratio"],
                    forecast["created_at"],
                    forecast["due_at"],
                    forecast.get("evaluated_at"),
                    forecast["status"],
                    forecast.get("outcome"),
                    forecast.get("pnl_pct"),
                    json.dumps(forecast.get("signal")) if forecast.get("signal") is not None else None,
                    json.dumps(forecast.get("evaluation")) if forecast.get("evaluation") is not None else None,
                ),
            )
            return int(cur.lastrowid)

    def create_job(
        self,
        job_type: str,
        *,
        status: str,
        created_at: str,
        params: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
    ) -> Dict[str, Any]:
        with self.connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO background_jobs (
                    job_type, status, params_json, message, created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    job_type,
                    status,
                    json.dumps(params) if params is not None else None,
                    message,
                    created_at,
                ),
            )
            job_id = int(cur.lastrowid)
        job = self.get_job(job_id)
        if job is None:
            raise RuntimeError(f"Background job {job_id} was not created.")
        return job

    def get_job(self, job_id: int) -> Optional[Dict[str, Any]]:
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM background_jobs
                WHERE id = ?
                """,
                (job_id,),
            ).fetchone()
            return self._row_to_job(row) if row else None

    def list_jobs(
        self,
        *,
        statuses: Optional[Sequence[str]] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        with self.connection() as conn:
            if statuses:
                placeholders = ", ".join("?" for _ in statuses)
                rows = conn.execute(
                    f"""
                    SELECT *
                    FROM background_jobs
                    WHERE status IN ({placeholders})
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    tuple(statuses) + (limit,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM background_jobs
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
            return [self._row_to_job(row) for row in rows]

    def start_job(self, job_id: int, *, started_at: str, message: Optional[str] = None) -> Dict[str, Any]:
        return self._update_job(
            job_id,
            status="running",
            started_at=started_at,
            message=message,
        )

    def complete_job(
        self,
        job_id: int,
        *,
        finished_at: str,
        result: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self._update_job(
            job_id,
            status="completed",
            finished_at=finished_at,
            result=result,
            message=message,
            error=None,
        )

    def fail_job(
        self,
        job_id: int,
        *,
        finished_at: str,
        error: str,
        message: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self._update_job(
            job_id,
            status="error",
            finished_at=finished_at,
            result=None,
            error=error,
            message=message,
        )

    def has_pending_forecast(self, pair: str, direction: str, due_after_iso: str) -> bool:
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT 1
                FROM trade_forecasts
                WHERE pair = ?
                  AND direction = ?
                  AND status = 'pending'
                  AND due_at >= ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (pair, direction, due_after_iso),
            ).fetchone()
            return row is not None

    def list_due_forecasts(self, now_iso: str) -> List[Dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM trade_forecasts
                WHERE status = 'pending'
                  AND due_at <= ?
                ORDER BY due_at ASC, id ASC
                """,
                (now_iso,),
            ).fetchall()
            return [self._row_to_forecast(row) for row in rows]

    def update_forecast_evaluation(
        self,
        forecast_id: int,
        *,
        evaluated_at: str,
        status: str,
        outcome: str,
        pnl_pct: float,
        evaluation: Dict[str, Any],
    ) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                UPDATE trade_forecasts
                SET evaluated_at = ?,
                    status = ?,
                    outcome = ?,
                    pnl_pct = ?,
                    evaluation_json = ?
                WHERE id = ?
                """,
                (
                    evaluated_at,
                    status,
                    outcome,
                    pnl_pct,
                    json.dumps(evaluation),
                    forecast_id,
                ),
            )

    def list_forecasts(self, limit: int = 20, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.connection() as conn:
            if status:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM trade_forecasts
                    WHERE status = ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (status, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM trade_forecasts
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
            return [self._row_to_forecast(row) for row in rows]

    def get_forecast_summary(self) -> Dict[str, int]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT status, COALESCE(outcome, status) AS bucket, COUNT(*) AS count
                FROM trade_forecasts
                GROUP BY status, bucket
                """
            ).fetchall()

        summary = {
            "total": 0,
            "pending": 0,
            "evaluated": 0,
            "wins": 0,
            "losses": 0,
            "flat": 0,
        }
        for row in rows:
            count = int(row["count"])
            summary["total"] += count
            if row["status"] == "pending":
                summary["pending"] += count
            if row["status"] == "evaluated":
                summary["evaluated"] += count
                if row["bucket"] == "win":
                    summary["wins"] += count
                elif row["bucket"] == "loss":
                    summary["losses"] += count
                elif row["bucket"] == "flat":
                    summary["flat"] += count
        return summary

    @staticmethod
    def _normalize_pairs(pairs: Iterable[Tuple[str, str]]) -> List[Tuple[str, str]]:
        normalized: List[Tuple[str, str]] = []
        seen = set()
        for base_asset, quote_asset in pairs:
            base = str(base_asset).strip().upper()
            quote = str(quote_asset).strip().upper()
            if not base or not quote or base == quote:
                continue
            key = (base, quote)
            if key in seen:
                continue
            seen.add(key)
            normalized.append(key)
        return normalized

    @staticmethod
    def _decode_json(value: Optional[str]) -> Any:
        if value is None:
            return None
        return DashboardStorage._sanitize_json_numbers(json.loads(value))

    @staticmethod
    def _sanitize_json_numbers(value: Any) -> Any:
        if isinstance(value, float):
            return value if math.isfinite(value) else None
        if isinstance(value, list):
            return [DashboardStorage._sanitize_json_numbers(item) for item in value]
        if isinstance(value, dict):
            return {
                key: DashboardStorage._sanitize_json_numbers(item)
                for key, item in value.items()
            }
        return value

    def _update_job(
        self,
        job_id: int,
        *,
        status: Optional[str] = None,
        started_at: Any = _UNSET,
        finished_at: Any = _UNSET,
        result: Any = _UNSET,
        error: Any = _UNSET,
        message: Any = _UNSET,
    ) -> Dict[str, Any]:
        current = self.get_job(job_id)
        if current is None:
            raise KeyError(job_id)

        payload = {
            "status": current["status"] if status is None else status,
            "started_at": current["started_at"] if started_at is _UNSET else started_at,
            "finished_at": current["finished_at"] if finished_at is _UNSET else finished_at,
            "result": current["result"] if result is _UNSET else result,
            "error": current["error"] if error is _UNSET else error,
            "message": current["message"] if message is _UNSET else message,
        }
        with self.connection() as conn:
            conn.execute(
                """
                UPDATE background_jobs
                SET status = ?,
                    started_at = ?,
                    finished_at = ?,
                    result_json = ?,
                    error = ?,
                    message = ?
                WHERE id = ?
                """,
                (
                    payload["status"],
                    payload["started_at"],
                    payload["finished_at"],
                    json.dumps(payload["result"]) if payload["result"] is not None else None,
                    payload["error"],
                    payload["message"],
                    job_id,
                ),
            )
        updated = self.get_job(job_id)
        if updated is None:
            raise RuntimeError(f"Background job {job_id} disappeared after update.")
        return updated

    def _row_to_run(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "run_type": row["run_type"],
            "pair": row["pair"],
            "status": row["status"],
            "started_at": row["started_at"],
            "finished_at": row["finished_at"],
            "message": row["message"],
            "error": row["error"],
            "payload": self._decode_json(row["payload_json"]),
        }

    def _row_to_signal(self, row: sqlite3.Row) -> Dict[str, Any]:
        spec = self._decode_json(row["spec_json"])
        backtest = self._decode_json(row["backtest_json"])
        return {
            "id": row["id"],
            "run_id": row["run_id"],
            "pair": row["pair"],
            "base_asset": row["base_asset"],
            "quote_asset": row["quote_asset"],
            "status": row["status"],
            "direction": row["direction"],
            "conviction_score": row["conviction_score"],
            "spread_zscore": row["spread_zscore"],
            "market_regime": row["market_regime"],
            "divergence_state": row["divergence_state"],
            "correlation": row["correlation"],
            "base_vs_peer_average_return_pct": row["base_vs_peer_average_return_pct"],
            "backtest_results": backtest,
            "spec": spec,
            "created_at": row["created_at"],
        }

    def _row_to_watchlist_pair(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "pair": f"{row['base_asset']}/{row['quote_asset']}",
            "base_asset": row["base_asset"],
            "quote_asset": row["quote_asset"],
            "enabled": bool(row["enabled"]),
            "position": row["position"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _row_to_monitor_settings(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "enabled": bool(row["enabled"]),
            "interval_sec": row["interval_sec"],
            "lookback_days": row["lookback_days"],
            "next_run_at": row["next_run_at"],
            "last_started_at": row["last_started_at"],
            "last_finished_at": row["last_finished_at"],
            "last_status": row["last_status"],
            "last_message": row["last_message"],
            "updated_at": row["updated_at"],
        }

    def _row_to_forecast(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "pair": row["pair"],
            "base_asset": row["base_asset"],
            "quote_asset": row["quote_asset"],
            "direction": row["direction"],
            "spread_zscore": row["spread_zscore"],
            "conviction_score": row["conviction_score"],
            "market_regime": row["market_regime"],
            "divergence_state": row["divergence_state"],
            "correlation": row["correlation"],
            "entry_price_base": row["entry_price_base"],
            "entry_price_quote": row["entry_price_quote"],
            "entry_spread_ratio": row["entry_spread_ratio"],
            "created_at": row["created_at"],
            "due_at": row["due_at"],
            "evaluated_at": row["evaluated_at"],
            "status": row["status"],
            "outcome": row["outcome"],
            "pnl_pct": row["pnl_pct"],
            "signal": self._decode_json(row["signal_json"]),
            "evaluation": self._decode_json(row["evaluation_json"]),
        }

    def _row_to_job(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "job_type": row["job_type"],
            "status": row["status"],
            "params": self._decode_json(row["params_json"]),
            "result": self._decode_json(row["result_json"]),
            "error": row["error"],
            "message": row["message"],
            "created_at": row["created_at"],
            "started_at": row["started_at"],
            "finished_at": row["finished_at"],
        }
