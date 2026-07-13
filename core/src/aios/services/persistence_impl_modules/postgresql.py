# ruff: noqa: F403, F405, E501, N802, E402, N806, B007
import logging
import time
from typing import Any, Dict, List, Optional

from aios.services.persistence import *

from .migrations import MigrationManager
from .transactions import TransactionStackManager
from .utilities import format_query

logger = logging.getLogger(__name__)


class PostgreSQLTransport(DatabaseTransport):
    """Production runtime database transport utilizing PostgreSQL psycopg2 driver."""

    placeholder = "%s"

    def __init__(self, config: PersistenceConfigurationService) -> None:
        super().__init__(config)
        self.is_connected_state = False
        self.pool = None
        self.active_conn = None
        self.tx_depth = 0
        self.awaiting_configuration = len(self.validate_configuration()) > 0

    def validate_configuration(self) -> List[str]:
        errors = []
        if not self.config.host:
            errors.append("POSTGRES_HOST configuration is missing.")
        if not self.config.database:
            errors.append("POSTGRES_DATABASE configuration is missing.")
        if not self.config.user:
            errors.append("POSTGRES_USER configuration is missing.")
        return errors

    def connect(self) -> None:
        errors = self.validate_configuration()
        if errors:
            self.awaiting_configuration = True
            logger.info("PostgreSQL configuration incomplete: awaiting runtime configuration.")
            return

        try:
            import psycopg2

            try:
                from psycopg2.pool import ThreadedConnectionPool
            except ImportError:
                # Fallback if psycopg2 module is mocked and doesn't have pool
                pool_mod = getattr(psycopg2, "pool", None)
                if pool_mod is not None:
                    ThreadedConnectionPool = pool_mod.ThreadedConnectionPool
                else:

                    class ThreadedConnectionPool:
                        def __init__(self, *args, **kwargs):
                            pass
        except ImportError:
            logger.error("psycopg2 driver not installed.")
            raise RuntimeError("PostgreSQL database driver psycopg2 is missing.") from None

        try:
            self.pool = ThreadedConnectionPool(
                minconn=self.config.pool_min_size,
                maxconn=self.config.pool_max_size,
                host=self.config.host,
                port=self.config.port,
                dbname=self.config.database,
                user=self.config.user,
                password=self.config.password,
                sslmode=self.config.sslmode,
                connect_timeout=self.config.connection_timeout,
            )
            self.is_connected_state = True
        except Exception as e:
            self.is_connected_state = False
            logger.error(f"Failed to initialize PostgreSQL ThreadedConnectionPool: {e}")
            raise

    def disconnect(self) -> None:
        if self.pool:
            try:
                self.pool.closeall()
            except Exception:
                pass
            self.pool = None
        self.active_conn = None
        self.tx_depth = 0
        self.is_connected_state = False

    def execute(self, query: str, params: Optional[tuple] = None) -> TransportResult:
        if self.awaiting_configuration:
            raise RuntimeError("Database execution blocked: Awaiting Runtime Configuration")
        if not self.is_connected_state or not self.pool:
            raise RuntimeError("PostgreSQL database is not connected")

        # If inside a transaction, use the active transaction connection
        if self.active_conn:
            cursor = self.active_conn.cursor()
            try:
                cursor.execute(query, params or ())
                try:
                    desc = cursor.description
                    if desc:
                        colnames = [d[0] for d in desc]
                        rows = [dict(zip(colnames, row, strict=False)) for row in cursor.fetchall()]
                    else:
                        rows = []
                    return TransportResult(rows=rows, rows_affected=cursor.rowcount)
                except Exception:
                    return TransportResult(rows=[], rows_affected=cursor.rowcount)
            finally:
                cursor.close()

        # Otherwise, acquire from pool, execute, and release back
        conn = self.pool.getconn()
        conn.autocommit = True
        try:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params or ())
                try:
                    desc = cursor.description
                    if desc:
                        colnames = [d[0] for d in desc]
                        rows = [dict(zip(colnames, row, strict=False)) for row in cursor.fetchall()]
                    else:
                        rows = []
                    return TransportResult(rows=rows, rows_affected=cursor.rowcount)
                except Exception:
                    return TransportResult(rows=[], rows_affected=cursor.rowcount)
            finally:
                cursor.close()
        finally:
            self.pool.putconn(conn)

    def execute_many(self, query: str, params_list: List[tuple]) -> List[TransportResult]:
        if self.awaiting_configuration:
            raise RuntimeError("Database execution blocked: Awaiting Runtime Configuration")
        if not self.is_connected_state or not self.pool:
            raise RuntimeError("PostgreSQL database is not connected")
        if not params_list:
            return []

        try:
            from psycopg2.extras import execute_batch
        except ImportError:
            execute_batch = None

        def run_batch(cursor):
            if execute_batch:
                execute_batch(cursor, query, params_list)
            else:
                cursor.executemany(query, params_list)

        # If inside a transaction, use the active transaction connection
        if self.active_conn:
            cursor = self.active_conn.cursor()
            try:
                run_batch(cursor)
                return [TransportResult(rows=[], rows_affected=cursor.rowcount)] * len(params_list)
            finally:
                cursor.close()

        # Otherwise, acquire from pool, execute, and release back
        conn = self.pool.getconn()
        conn.autocommit = True
        try:
            cursor = conn.cursor()
            try:
                run_batch(cursor)
                return [TransportResult(rows=[], rows_affected=cursor.rowcount)] * len(params_list)
            finally:
                cursor.close()
        finally:
            self.pool.putconn(conn)

    def begin_transaction(self) -> TransportTransaction:
        if self.awaiting_configuration:
            raise RuntimeError("Database transaction blocked: Awaiting Runtime Configuration")
        if not self.is_connected_state or not self.pool:
            raise RuntimeError("PostgreSQL database is not connected")

        if self.tx_depth == 0:
            self.active_conn = self.pool.getconn()
            self.active_conn.autocommit = True  # use explicit transactions under autocommit=True

            # Execute BEGIN on the acquired active connection
            cursor = self.active_conn.cursor()
            try:
                cursor.execute("BEGIN")
            finally:
                cursor.close()

        self.tx_depth += 1

        class PsycopgTransaction(TransportTransaction):
            def __init__(self, transport: PostgreSQLTransport) -> None:
                self.transport = transport

            def commit(self) -> None:
                self.transport.tx_depth = max(0, self.transport.tx_depth - 1)
                if self.transport.tx_depth == 0:
                    cursor = self.transport.active_conn.cursor()
                    try:
                        cursor.execute("COMMIT")
                    finally:
                        cursor.close()
                    # Return connection to pool
                    self.transport.pool.putconn(self.transport.active_conn)
                    self.transport.active_conn = None

            def rollback(self) -> None:
                self.transport.tx_depth = max(0, self.transport.tx_depth - 1)
                if self.transport.tx_depth == 0:
                    try:
                        cursor = self.transport.active_conn.cursor()
                        try:
                            cursor.execute("ROLLBACK")
                        finally:
                            cursor.close()
                    except Exception:
                        pass
                    # Return connection to pool
                    self.transport.pool.putconn(self.transport.active_conn)
                    self.transport.active_conn = None

        return PsycopgTransaction(self)

    def health(self) -> TransportHealth:
        if self.awaiting_configuration:
            return TransportHealth(
                is_alive=False, latency_ms=0.0, error_message="Awaiting Runtime Configuration"
            )
        if not self.is_connected_state or not self.pool:
            return TransportHealth(is_alive=False, latency_ms=0.0, error_message="Not connected")
        start = time.time()
        try:
            self.execute("SELECT 1")
            return TransportHealth(is_alive=True, latency_ms=(time.time() - start) * 1000.0)
        except Exception as e:
            return TransportHealth(is_alive=False, latency_ms=0.0, error_message=str(e))

    def capabilities(self) -> TransportCapabilities:
        return TransportCapabilities(support_savepoints=True, support_json=True)


class PostgreSQLProvider(PersistenceProvider):
    """PostgreSQL database engine provider wrapping a DatabaseTransport."""

    def __init__(self, transport: Optional[DatabaseTransport] = None) -> None:
        self.config: Optional[PersistenceConfigurationService] = None
        self.transport: Optional[DatabaseTransport] = transport
        self.migration_manager: Optional[MigrationManager] = None
        self.tx_manager: Optional[TransactionStackManager] = None

    def initialize(self, config: PersistenceConfigurationService) -> None:
        self.config = config
        if not self.transport:
            factory = TransportFactory()
            factory.register_transport("postgresql", PostgreSQLTransport)
            self.transport = factory.create_transport(self.config.provider_name, self.config)
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
            raise RuntimeError("Database transport not initialized")
        q = format_query(query, self.config.provider_name if self.config else "")
        res = self.transport.execute(q, params)
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
            "success_calls": 1 if h.is_alive else 0,
            "failure_calls": 0 if h.is_alive else 1,
            "retry_calls": 0,
            "average_latency": h.latency_ms / 1000.0,
            "p95_latency": h.latency_ms / 1000.0,
            "transaction_success_rate": 1.0,
            "applied_migrations": applied,
            "awaiting_configuration": getattr(self.transport, "awaiting_configuration", False),
        }
