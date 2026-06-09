import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional


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
                """
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
                ORDER BY ps.spread_zscore DESC
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

    @staticmethod
    def _decode_json(value: Optional[str]) -> Any:
        if value is None:
            return None
        return json.loads(value)

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
