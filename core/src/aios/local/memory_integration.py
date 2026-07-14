"""
aios/local/memory_integration.py

Memory Integration for Local Model Executions.

Every local model execution is persisted with:
prompt, model, execution time, output, success/failure, memory usage.
Integrates with the existing aios.db SQLite database.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS local_model_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    capability TEXT NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    success INTEGER NOT NULL DEFAULT 1,
    inference_time_ms REAL NOT NULL DEFAULT 0.0,
    tokens_estimated INTEGER NOT NULL DEFAULT 0,
    tokens_per_second REAL NOT NULL DEFAULT 0.0,
    memory_mb REAL NOT NULL DEFAULT 0.0,
    error TEXT,
    metadata TEXT NOT NULL DEFAULT '{}',
    timestamp REAL NOT NULL,
    session_id TEXT
);
"""

_CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_local_exec_model ON local_model_executions(model_name);
CREATE INDEX IF NOT EXISTS idx_local_exec_timestamp ON local_model_executions(timestamp);
CREATE INDEX IF NOT EXISTS idx_local_exec_capability ON local_model_executions(capability);
"""


@dataclass
class LocalExecutionRecord:
    """
    Full record of a single local model execution, as persisted to the database.
    """

    model_name: str
    capability: str
    prompt: str
    response: str
    success: bool
    inference_time_ms: float
    tokens_estimated: int = 0
    tokens_per_second: float = 0.0
    memory_mb: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    session_id: Optional[str] = None
    record_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["metadata"] = json.dumps(d["metadata"])
        return d


class LocalMemoryIntegration:
    """
    Persists local model execution records to the aios SQLite database.

    Design decisions:
    - Uses the existing aios.db database to co-locate execution logs
      with other system data.
    - Thread-safe: each operation creates its own connection (WAL mode).
    - Provides query interface for analytics and health monitoring.
    - If the database is unavailable, logs a warning but does NOT raise —
      memory integration is non-critical to execution flow.
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._ensure_table()

    def record(self, execution: LocalExecutionRecord) -> Optional[int]:
        """
        Persists a single execution record to the database.

        Returns the auto-generated row ID, or None on failure.
        """
        try:
            with sqlite3.connect(str(self._db_path)) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                cursor = conn.execute(
                    """
                    INSERT INTO local_model_executions
                        (model_name, capability, prompt, response, success,
                         inference_time_ms, tokens_estimated, tokens_per_second,
                         memory_mb, error, metadata, timestamp, session_id)
                    VALUES
                        (:model_name, :capability, :prompt, :response, :success,
                         :inference_time_ms, :tokens_estimated, :tokens_per_second,
                         :memory_mb, :error, :metadata, :timestamp, :session_id)
                    """,
                    {
                        "model_name": execution.model_name,
                        "capability": execution.capability,
                        "prompt": execution.prompt[:4096],  # Cap at 4KB
                        "response": execution.response[:16384],  # Cap at 16KB
                        "success": 1 if execution.success else 0,
                        "inference_time_ms": execution.inference_time_ms,
                        "tokens_estimated": execution.tokens_estimated,
                        "tokens_per_second": execution.tokens_per_second,
                        "memory_mb": execution.memory_mb,
                        "error": execution.error,
                        "metadata": json.dumps(execution.metadata),
                        "timestamp": execution.timestamp,
                        "session_id": execution.session_id,
                    },
                )
                row_id = cursor.lastrowid
                logger.debug(
                    "Recorded execution: model=%s capability=%s id=%d",
                    execution.model_name,
                    execution.capability,
                    row_id,
                )
                return row_id
        except Exception as exc:
            logger.warning("Failed to record execution to database: %s", exc)
            return None

    def get_recent_executions(
        self,
        limit: int = 50,
        model_name: Optional[str] = None,
        capability: Optional[str] = None,
    ) -> List[LocalExecutionRecord]:
        """
        Retrieves the most recent execution records, optionally filtered.
        """
        conditions = []
        params: Dict[str, Any] = {"limit": limit}

        if model_name:
            conditions.append("model_name = :model_name")
            params["model_name"] = model_name
        if capability:
            conditions.append("capability = :capability")
            params["capability"] = capability

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        try:
            with sqlite3.connect(str(self._db_path)) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    f"""
                    SELECT * FROM local_model_executions
                    {where}
                    ORDER BY timestamp DESC
                    LIMIT :limit
                    """,
                    params,
                ).fetchall()
                return [self._row_to_record(r) for r in rows]
        except Exception as exc:
            logger.warning("Failed to query executions: %s", exc)
            return []

    def get_model_stats(self, model_name: str) -> Dict[str, Any]:
        """
        Returns aggregate statistics for a specific model.
        """
        try:
            with sqlite3.connect(str(self._db_path)) as conn:
                row = conn.execute(
                    """
                    SELECT
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                        AVG(inference_time_ms) as avg_latency_ms,
                        AVG(tokens_per_second) as avg_tps,
                        MAX(timestamp) as last_used
                    FROM local_model_executions
                    WHERE model_name = ?
                    """,
                    (model_name,),
                ).fetchone()
                if row:
                    total = row[0] or 0
                    successes = row[1] or 0
                    return {
                        "model_name": model_name,
                        "total_requests": total,
                        "success_count": successes,
                        "failure_count": total - successes,
                        "success_rate": (successes / total) if total > 0 else 1.0,
                        "avg_latency_ms": round(row[2] or 0.0, 2),
                        "avg_tps": round(row[3] or 0.0, 2),
                        "last_used": row[4],
                    }
        except Exception as exc:
            logger.warning("Failed to compute model stats for '%s': %s", model_name, exc)
        return {"model_name": model_name, "total_requests": 0}

    def get_capability_stats(self) -> Dict[str, Any]:
        """
        Returns aggregate statistics grouped by capability.
        """
        try:
            with sqlite3.connect(str(self._db_path)) as conn:
                rows = conn.execute(
                    """
                    SELECT
                        capability,
                        COUNT(*) as total,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes
                    FROM local_model_executions
                    GROUP BY capability
                    ORDER BY total DESC
                    """,
                ).fetchall()
                return {
                    row[0]: {
                        "total": row[1],
                        "successes": row[2],
                        "failures": row[1] - row[2],
                    }
                    for row in rows
                }
        except Exception as exc:
            logger.warning("Failed to compute capability stats: %s", exc)
            return {}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure_table(self) -> None:
        """Creates the executions table if it does not exist."""
        try:
            with sqlite3.connect(str(self._db_path)) as conn:
                conn.execute(_CREATE_TABLE_SQL)
                for stmt in _CREATE_INDEX_SQL.strip().split(";"):
                    stmt = stmt.strip()
                    if stmt:
                        conn.execute(stmt)
        except Exception as exc:
            logger.warning("Could not create local_model_executions table: %s", exc)

    def _row_to_record(self, row: sqlite3.Row) -> LocalExecutionRecord:
        """Converts a sqlite3.Row to a LocalExecutionRecord."""
        d = dict(row)
        d["success"] = bool(d.get("success", 1))
        metadata_raw = d.pop("metadata", "{}")
        try:
            metadata = json.loads(metadata_raw)
        except Exception:
            metadata = {}
        record_id = d.pop("id", None)
        return LocalExecutionRecord(
            record_id=record_id,
            metadata=metadata,
            **{k: v for k, v in d.items() if k in LocalExecutionRecord.__dataclass_fields__},
        )
