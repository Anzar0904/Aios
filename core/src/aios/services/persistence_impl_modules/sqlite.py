# ruff: noqa: F403, F405, E501, N802, E402, N806, B007
import logging
import os
import queue
import sqlite3
import threading
from typing import Any, Dict, List, Optional

from aios.services.persistence import (
    DatabaseTransport,
    PersistenceConfigurationService,
    PersistenceProvider,
    TransportCapabilities,
    TransportHealth,
    TransportResult,
    TransportTransaction,
)

from .migrations import MigrationManager
from .transactions import TransactionStackManager

logger = logging.getLogger(__name__)


class SQLiteTransport(DatabaseTransport):
    """Production runtime database transport utilizing local SQLite."""

    placeholder = "?"

    def __init__(self, config: PersistenceConfigurationService) -> None:
        super().__init__(config)
        self.pool = None
        self._local = threading.local()
        self.db_path = os.environ.get("SQLITE_DATABASE_PATH", "aios.db")

    @property
    def active_conn(self) -> Optional[sqlite3.Connection]:
        return getattr(self._local, "active_conn", None)

    @active_conn.setter
    def active_conn(self, val: Optional[sqlite3.Connection]) -> None:
        self._local.active_conn = val

    @property
    def tx_depth(self) -> int:
        return getattr(self._local, "tx_depth", 0)

    @tx_depth.setter
    def tx_depth(self, val: int) -> None:
        self._local.tx_depth = val

    def validate_configuration(self) -> List[str]:
        return []

    def connect(self) -> None:
        self._local.active_conn = None
        self._local.tx_depth = 0
        if self.pool:
            return

        def factory():
            conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
            conn.isolation_level = None
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA busy_timeout = 30000")
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn

        class SimplePool:
            def __init__(self, min_size: int, max_size: int, factory_fn) -> None:
                self.factory = factory_fn
                self.conns = queue.Queue(max_size)
                self.all_conns = []
                self.min_size = min_size
                self.max_size = max_size
                for _ in range(min_size):
                    c = factory_fn()
                    self.conns.put(c)
                    self.all_conns.append(c)

            def acquire(self):
                try:
                    return self.conns.get(block=True, timeout=1.0)
                except queue.Empty:
                    if len(self.all_conns) < self.max_size:
                        c = self.factory()
                        self.all_conns.append(c)
                        return c
                    raise TimeoutError("Pool exhausted") from None

            def release(self, c):
                try:
                    self.conns.put(c, block=False)
                except queue.Full:
                    c.close()

            def close(self):
                for c in self.all_conns:
                    try:
                        c.close()
                    except Exception:
                        pass
                self.all_conns.clear()

        min_size = max(1, self.config.pool_min_size)
        max_size = max(min_size, self.config.pool_max_size)
        self.pool = SimplePool(min_size, max_size, factory)
        logger.info(f"Initialized SQLite database transport connection pool at {self.db_path}")

    def disconnect(self) -> None:
        if self.pool:
            self.pool.close()
            self.pool = None
        self._local.active_conn = None
        self._local.tx_depth = 0

    def execute(self, query: str, params: Optional[tuple] = None) -> TransportResult:
        if not self.pool:
            raise RuntimeError("SQLite database is not connected")
        query = query.replace("%s", "?")

        if self.active_conn:
            cursor = self.active_conn.cursor()
            try:
                cursor.execute(query, params or ())
                desc = cursor.description
                if desc:
                    colnames = [d[0] for d in desc]
                    rows = [dict(zip(colnames, row, strict=False)) for row in cursor.fetchall()]
                else:
                    rows = []
                return TransportResult(
                    rows=rows, last_inserted_id=cursor.lastrowid, rows_affected=cursor.rowcount
                )
            except Exception as e:
                logger.error(
                    f"SQLite query execution error inside transaction: {e}. Query: {query}"
                )
                raise
            finally:
                cursor.close()

        conn = self.pool.acquire()
        try:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params or ())
                desc = cursor.description
                if desc:
                    colnames = [d[0] for d in desc]
                    rows = [dict(zip(colnames, row, strict=False)) for row in cursor.fetchall()]
                else:
                    rows = []
                return TransportResult(
                    rows=rows, last_inserted_id=cursor.lastrowid, rows_affected=cursor.rowcount
                )
            except Exception as e:
                logger.error(f"SQLite query execution error: {e}. Query: {query}")
                raise
            finally:
                cursor.close()
        finally:
            self.pool.release(conn)

    def execute_many(self, query: str, params_list: List[tuple]) -> List[TransportResult]:
        res = []
        for p in params_list:
            res.append(self.execute(query, p))
        return res

    def begin_transaction(self) -> TransportTransaction:
        if self.tx_depth == 0:
            self.active_conn = self.pool.acquire()
            self.active_conn.execute("BEGIN TRANSACTION")
        self.tx_depth += 1

        class SqliteTx(TransportTransaction):
            def __init__(self, transport) -> None:
                self.transport = transport

            def commit(self) -> None:
                self.transport.tx_depth = max(0, self.transport.tx_depth - 1)
                if self.transport.tx_depth == 0:
                    self.transport.active_conn.execute("COMMIT")
                    self.transport.pool.release(self.transport.active_conn)
                    self.transport.active_conn = None

            def rollback(self) -> None:
                self.transport.tx_depth = max(0, self.transport.tx_depth - 1)
                if self.transport.tx_depth == 0:
                    try:
                        self.transport.active_conn.execute("ROLLBACK")
                    except sqlite3.Error:
                        pass
                    self.transport.pool.release(self.transport.active_conn)
                    self.transport.active_conn = None

        return SqliteTx(self)

    def health(self) -> TransportHealth:
        if not self.pool:
            return TransportHealth(is_alive=False, latency_ms=0.0, error_message="Not connected")
        return TransportHealth(is_alive=True, latency_ms=1.0)

    def capabilities(self) -> TransportCapabilities:
        return TransportCapabilities(support_savepoints=True, support_json=True)


class SQLiteProvider(PersistenceProvider):
    """SQLite engine provider wrapping a SQLiteTransport."""

    def __init__(self, transport: Optional[DatabaseTransport] = None) -> None:
        self.config: Optional[PersistenceConfigurationService] = None
        self.transport: Optional[DatabaseTransport] = transport
        self.migration_manager: Optional[MigrationManager] = None
        self.tx_manager: Optional[TransactionStackManager] = None

    def initialize(self, config: PersistenceConfigurationService) -> None:
        self.config = config
        if not self.transport:
            self.transport = SQLiteTransport(config)
        self.migration_manager = MigrationManager(self)
        self.tx_manager = TransactionStackManager(self.transport)

    def connect(self) -> None:
        if self.transport:
            self.transport.connect()

    def disconnect(self) -> None:
        if self.transport:
            self.transport.disconnect()

    def execute(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        if not self.transport:
            raise RuntimeError("SQLite database transport not initialized")
        res = self.transport.execute(query, params)
        return res.rows

    def begin_transaction(self) -> None:
        if self.tx_manager:
            self.tx_manager.begin()

    def commit_transaction(self) -> None:
        if self.tx_manager:
            self.tx_manager.commit()

    def rollback_transaction(self) -> None:
        if self.tx_manager:
            self.tx_manager.rollback()

    def is_connected(self) -> bool:
        if not self.transport:
            return False
        return self.transport.health().is_alive

    def get_metrics(self) -> Dict[str, Any]:
        if not self.transport:
            return {}
        h = self.transport.health()
        applied = 0
        if self.migration_manager:
            try:
                applied = len(self.migration_manager.get_applied_versions())
            except Exception:
                pass
        return {
            "active_connections": 1 if h.is_alive else 0,
            "total_connections": 1 if h.is_alive else 0,
            "applied_migrations": applied,
        }
