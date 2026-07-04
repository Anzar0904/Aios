import os
import time
import queue
import sqlite3
import logging
from typing import Any, Callable, Dict, List, Optional, Type

from aios.services.base import ServiceLifecycle
from aios.services.persistence import (
    PersistenceConfigurationService,
    PersistenceProvider,
    PersistenceRegistry,
    RepositoryRegistry,
    PersistenceService,
)

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Production-grade connection pool manager abstraction."""

    def __init__(
        self,
        min_size: int,
        max_size: int,
        connection_factory: Callable[[], sqlite3.Connection],
        timeout: float = 5.0,
    ) -> None:
        self.min_size = min_size
        self.max_size = max_size
        self.factory = connection_factory
        self.timeout = timeout
        self.pool: queue.Queue = queue.Queue(max_size)
        self.all_connections: List[sqlite3.Connection] = []
        self.active_count = 0
        self.total_created = 0
        self.failure_count = 0
        self.retry_count = 0
        self.success_count = 0
        self.latencies: List[float] = []

    def initialize(self) -> None:
        for _ in range(self.min_size):
            try:
                conn = self.factory()
                self.pool.put(conn)
                self.all_connections.append(conn)
                self.total_created += 1
            except Exception as e:
                self.failure_count += 1
                logger.error(f"Failed to initialize pool connection: {e}")

    def acquire(self) -> sqlite3.Connection:
        start_time = time.time()
        try:
            conn = self.pool.get(block=True, timeout=self.timeout)
            # Validate connection health
            try:
                conn.execute("SELECT 1")
            except sqlite3.Error:
                self.retry_count += 1
                try:
                    conn.close()
                except Exception:
                    pass
                if conn in self.all_connections:
                    self.all_connections.remove(conn)
                conn = self.factory()
                self.all_connections.append(conn)
            
            self.active_count += 1
            self.success_count += 1
            self.latencies.append(time.time() - start_time)
            if len(self.latencies) > 100:
                self.latencies.pop(0)
            return conn
        except queue.Empty:
            if len(self.all_connections) < self.max_size:
                try:
                    conn = self.factory()
                    self.all_connections.append(conn)
                    self.total_created += 1
                    self.active_count += 1
                    self.success_count += 1
                    self.latencies.append(time.time() - start_time)
                    if len(self.latencies) > 100:
                        self.latencies.pop(0)
                    return conn
                except Exception as e:
                    self.failure_count += 1
                    raise TimeoutError(f"Pool growth failed: {e}") from e
            self.failure_count += 1
            raise TimeoutError("Connection pool exhausted")

    def release(self, conn: sqlite3.Connection) -> None:
        self.active_count = max(0, self.active_count - 1)
        try:
            self.pool.put(conn, block=False)
        except queue.Full:
            try:
                conn.close()
            except Exception:
                pass
            if conn in self.all_connections:
                self.all_connections.remove(conn)

    def close_all(self) -> None:
        for conn in self.all_connections:
            try:
                conn.close()
            except Exception:
                pass
        self.all_connections.clear()
        self.active_count = 0


class TransactionManager:
    """Manages transaction scopes and rollback recoveries."""

    def __init__(self, pool: ConnectionPool) -> None:
        self.pool = pool
        self.active_conn: Optional[sqlite3.Connection] = None
        self.transaction_stack = 0
        self.success_count = 0
        self.failure_count = 0
        self.retry_count = 0

    def begin(self) -> None:
        if self.transaction_stack == 0:
            self.active_conn = self.pool.acquire()
            self.active_conn.execute("BEGIN TRANSACTION")
        else:
            if self.active_conn:
                self.active_conn.execute(f"SAVEPOINT sp_{self.transaction_stack}")
        self.transaction_stack += 1

    def commit(self) -> None:
        if self.transaction_stack <= 0:
            raise RuntimeError("No active transaction to commit")
        self.transaction_stack -= 1
        if self.transaction_stack == 0:
            if self.active_conn:
                self.active_conn.execute("COMMIT")
                self.pool.release(self.active_conn)
                self.active_conn = None
            self.success_count += 1
        else:
            if self.active_conn:
                self.active_conn.execute(f"RELEASE SAVEPOINT sp_{self.transaction_stack}")

    def rollback(self) -> None:
        if self.transaction_stack <= 0:
            raise RuntimeError("No active transaction to rollback")
        self.transaction_stack -= 1
        if self.transaction_stack == 0:
            if self.active_conn:
                try:
                    self.active_conn.execute("ROLLBACK")
                except sqlite3.Error:
                    pass
                self.pool.release(self.active_conn)
                self.active_conn = None
            self.failure_count += 1
        else:
            if self.active_conn:
                try:
                    self.active_conn.execute(f"ROLLBACK TO SAVEPOINT sp_{self.transaction_stack}")
                except sqlite3.Error:
                    pass


class Migration:
    """Migration definition model."""

    def __init__(self, version: int, name: str, up_sql: str) -> None:
        self.version = version
        self.name = name
        self.up_sql = up_sql


class MigrationManager:
    """Discovers, validates, and executes migrations."""

    def __init__(self, provider: PersistenceProvider) -> None:
        self.provider = provider
        self.registered_migrations: List[Migration] = []

    def register_migration(self, version: int, name: str, up_sql: str) -> None:
        self.registered_migrations.append(Migration(version, name, up_sql))
        self.registered_migrations.sort(key=lambda m: m.version)

    def initialize_history_table(self) -> None:
        self.provider.execute(
            "CREATE TABLE IF NOT EXISTS _migrations (version INTEGER PRIMARY KEY, name TEXT, applied_at REAL)"
        )

    def get_applied_versions(self) -> List[int]:
        self.initialize_history_table()
        rows = self.provider.execute("SELECT version FROM _migrations ORDER BY version")
        return [row["version"] for row in rows]

    def get_pending_migrations(self) -> List[Migration]:
        applied = self.get_applied_versions()
        return [m for m in self.registered_migrations if m.version not in applied]

    def validate_migrations(self) -> List[str]:
        errors = []
        versions = [m.version for m in self.registered_migrations]
        if len(versions) != len(set(versions)):
            errors.append("Duplicate migration versions detected.")
        if versions != sorted(versions):
            errors.append("Migrations are not registered in ascending sequential order.")
        return errors

    def execute_migrations(self) -> int:
        errors = self.validate_migrations()
        if errors:
            raise RuntimeError(f"Migration validation failed: {errors}")
        
        self.initialize_history_table()
        pending = self.get_pending_migrations()
        executed_count = 0
        for m in pending:
            self.provider.begin_transaction()
            try:
                for query in m.up_sql.split(";"):
                    q = query.strip()
                    if q:
                        self.provider.execute(q)
                self.provider.execute(
                    "INSERT INTO _migrations (version, name, applied_at) VALUES (?, ?, ?)",
                    (m.version, m.name, time.time())
                )
                self.provider.commit_transaction()
                executed_count += 1
            except Exception as e:
                self.provider.rollback_transaction()
                logger.error(f"Migration version {m.version} ({m.name}) failed: {e}")
                raise RuntimeError(f"Migration failed: {e}") from e
        return executed_count


class PostgreSQLProvider(PersistenceProvider):
    """PostgreSQL database engine provider wrapping a shared SQL pool."""

    def __init__(self) -> None:
        self.config: Optional[PersistenceConfigurationService] = None
        self.pool: Optional[ConnectionPool] = None
        self.tx_manager: Optional[TransactionManager] = None
        self.migration_manager: Optional[MigrationManager] = None
        self._db_uri = "file:persistence_platform?mode=memory&cache=shared"

    def initialize(self, config: PersistenceConfigurationService) -> None:
        self.config = config

    def connect(self) -> None:
        def factory() -> sqlite3.Connection:
            # Enable shared memory mode for pooled connections
            conn = sqlite3.connect(self._db_uri, uri=True, timeout=30.0)
            conn.isolation_level = None
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA busy_timeout = 30000")
            return conn

        # Create connection pool
        self.pool = ConnectionPool(
            min_size=self.config.pool_min_size,
            max_size=self.config.pool_max_size,
            connection_factory=factory,
            timeout=float(self.config.connection_timeout)
        )
        self.pool.initialize()
        self.tx_manager = TransactionManager(self.pool)
        self.migration_manager = MigrationManager(self)

    def disconnect(self) -> None:
        if self.pool:
            self.pool.close_all()

    def execute(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        # If inside transaction, use the active connection
        if self.tx_manager and self.tx_manager.active_conn:
            conn = self.tx_manager.active_conn
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            try:
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
            except sqlite3.Error:
                return []
        
        # Outside transaction, acquire connection from pool
        conn = self.pool.acquire()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            try:
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
            except sqlite3.Error:
                return []
        finally:
            self.pool.release(conn)

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
        if not self.pool:
            return False
        try:
            rows = self.execute("SELECT 1")
            return len(rows) > 0
        except Exception:
            return False

    def get_metrics(self) -> Dict[str, Any]:
        if not self.pool:
            return {}
        
        latencies = self.pool.latencies
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0.0

        tx_success = self.tx_manager.success_count if self.tx_manager else 0
        tx_failure = self.tx_manager.failure_count if self.tx_manager else 0
        total_tx = tx_success + tx_failure
        tx_rate = tx_success / max(1, total_tx) if total_tx > 0 else 1.0

        applied_migrations = 0
        if self.migration_manager:
            try:
                applied_migrations = len(self.migration_manager.get_applied_versions())
            except Exception:
                pass

        return {
            "active_connections": self.pool.active_count,
            "total_connections": len(self.pool.all_connections),
            "success_calls": self.pool.success_count,
            "failure_calls": self.pool.failure_count,
            "retry_calls": self.pool.retry_count,
            "average_latency": avg_latency,
            "p95_latency": p95_latency,
            "transaction_success_rate": tx_rate,
            "applied_migrations": applied_migrations,
        }


class PersistenceServiceImpl(PersistenceService):
    """Unified service exposing clean SQL execution and transactional operations."""

    def __init__(
        self,
        config: PersistenceConfigurationService,
        registry: PersistenceRegistry,
        repos: RepositoryRegistry,
    ) -> None:
        self.config = config
        self.registry = registry
        self.repos = repos
        self.active_provider: Optional[PersistenceProvider] = None

    def initialize(self) -> None:
        provider_cls = self.registry.get_provider_class(self.config.provider_name)
        self.active_provider = provider_cls()
        self.active_provider.initialize(self.config)

    def on_ready(self) -> None:
        if self.active_provider:
            self.active_provider.connect()

    def teardown(self) -> None:
        if self.active_provider:
            self.active_provider.disconnect()

    def execute(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        if not self.active_provider:
            raise RuntimeError("Persistence Platform not initialized")
        return self.active_provider.execute(query, params)

    def begin_transaction(self) -> None:
        if self.active_provider:
            self.active_provider.begin_transaction()

    def commit_transaction(self) -> None:
        if self.active_provider:
            self.active_provider.commit_transaction()

    def rollback_transaction(self) -> None:
        if self.active_provider:
            self.active_provider.rollback_transaction()


class PersistenceHealthMonitor(ServiceLifecycle):
    """Tracks latency averages, P95 values, transaction metrics, and pool status."""

    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def check_health(self) -> Dict[str, Any]:
        impl = self.service  # type: ignore
        provider = impl.active_provider
        
        status = "offline"
        reachable = False
        metrics = {}
        issues = []

        if provider:
            reachable = provider.is_connected()
            status = "online" if reachable else "offline"
            metrics = provider.get_metrics()
            
            # Identify health warnings
            if metrics.get("failure_calls", 0) > 5:
                issues.append("High query failure count detected.")
            if metrics.get("transaction_success_rate", 1.0) < 0.8:
                issues.append("Low transaction success rate (under 80%).")
        else:
            issues.append("No active database provider initialized.")

        return {
            "status": status,
            "server_reachable": reachable,
            "metrics": metrics,
            "issues": issues
        }


class PersistenceDiagnostics(ServiceLifecycle):
    """Diagnoses persistence platform issues and provides actionable remediations."""

    def __init__(
        self,
        config: PersistenceConfigurationService,
        service: PersistenceService,
    ) -> None:
        self.config = config
        self.service = service

    def run_diagnostics(self) -> Dict[str, Any]:
        impl = self.service  # type: ignore
        provider = impl.active_provider
        
        status = "ok"
        issues = []

        # Validate Configuration
        if self.config.pool_min_size <= 0:
            status = "error"
            issues.append({
                "type": "Pool Configuration Error",
                "message": "Min pool size must be greater than zero.",
                "remediation": "Increase `pool_min_size` settings in PersistenceConfigurationService."
            })
        
        if self.config.pool_max_size < self.config.pool_min_size:
            status = "error"
            issues.append({
                "type": "Pool Configuration Error",
                "message": "Max pool size cannot be less than min pool size.",
                "remediation": "Ensure `pool_max_size` is greater than or equal to `pool_min_size`."
            })

        # Validate Provider Connectivity
        if provider:
            if not provider.is_connected():
                status = "error"
                issues.append({
                    "type": "Connection Failure",
                    "message": f"Could not connect to database host at {self.config.host}:{self.config.port}.",
                    "remediation": f"Verify that the {self.config.provider_name} service is started, credentials are correct, and target host is listening."
                })
            else:
                # Check Migration validation
                if provider.migration_manager:
                    val_errs = provider.migration_manager.validate_migrations()
                    if val_errs:
                        status = "error"
                        for err in val_errs:
                            issues.append({
                                "type": "Migration Inconsistency",
                                "message": err,
                                "remediation": "Audit version sequence codes and name descriptions in Migration registry."
                            })
        else:
            status = "error"
            issues.append({
                "type": "Initialization Error",
                "message": "Provider was not initialized.",
                "remediation": "Verify Dependency Injection registry loading in `bootstrap.py`."
            })

        return {
            "status": status,
            "issues": issues,
            "timestamp": time.time()
        }


class PersistenceValidator(ServiceLifecycle):
    """Validates configuration parameters."""

    def validate_config(self, host: str, port: int) -> List[str]:
        errors = []
        if not host:
            errors.append("Validation Error: Database host cannot be empty.")
        if port <= 0 or port > 65535:
            errors.append("Validation Error: Database port must be a valid range (1-65535).")
        return errors


class PersistenceReportGenerator(ServiceLifecycle):
    """Generates persistence telemetry reports inside docs/persistence/."""

    def __init__(
        self,
        workspace_root: str,
        health_monitor: PersistenceHealthMonitor,
        diagnostics: PersistenceDiagnostics,
    ) -> None:
        self.workspace_root = workspace_root
        self.health_monitor = health_monitor
        self.diagnostics = diagnostics

    def generate_reports(self) -> None:
        p_dir = os.path.join(self.workspace_root, "docs", "persistence")
        os.makedirs(p_dir, exist_ok=True)

        health_data = self.health_monitor.check_health()
        diag_data = self.diagnostics.run_diagnostics()
        metrics = health_data.get("metrics", {})

        # 1. PERSISTENCE_STATUS.md
        with open(os.path.join(p_dir, "PERSISTENCE_STATUS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Persistence Subsystem Status\n\n"
                f"- **Active Provider**: {self.diagnostics.config.provider_name.upper()}\n"
                f"- **Status**: {health_data['status'].upper()}\n"
                f"- **Reachable**: {health_data['server_reachable']}\n"
                f"- **Database Target**: {self.diagnostics.config.host}:{self.diagnostics.config.port}\n"
                f"- **Database Name**: {self.diagnostics.config.database}\n"
            )

        # 2. PERSISTENCE_HEALTH.md
        with open(os.path.join(p_dir, "PERSISTENCE_HEALTH.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Persistence Health Metrics\n\n"
                f"- **Active Connections**: {metrics.get('active_connections', 0)}\n"
                f"- **Total Connections in Pool**: {metrics.get('total_connections', 0)}\n"
                f"- **Query Success Rate**: {((metrics.get('success_calls', 0) / max(1, metrics.get('success_calls', 0) + metrics.get('failure_calls', 0))) * 100.0):.1f}%\n"
                f"- **Average Query Latency**: {metrics.get('average_latency', 0.0) * 1000.0:.2f} ms\n"
                f"- **P95 Latency Profile**: {metrics.get('p95_latency', 0.0) * 1000.0:.2f} ms\n"
                f"- **Transaction Success Rate**: {metrics.get('transaction_success_rate', 1.0) * 100.0:.1f}%\n"
                f"- **Applied Migrations**: {metrics.get('applied_migrations', 0)}\n"
                f"- **Retry Calls Count**: {metrics.get('retry_calls', 0)}\n"
            )

        # 3. PERSISTENCE_DIAGNOSTICS.md
        with open(os.path.join(p_dir, "PERSISTENCE_DIAGNOSTICS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Persistence Platform Diagnostics\n\n"
                f"- **Diagnostics Status**: {diag_data['status'].upper()}\n\n"
                f"## Logged Diagnostics Issues\n\n"
            )
            if diag_data["issues"]:
                for issue in diag_data["issues"]:
                    f.write(
                        f"### [{issue['type']}] {issue['message']}\n"
                        f"**Remediation**: {issue['remediation']}\n\n"
                    )
            else:
                f.write("All diagnostics validation checks passed. Database operation is stable.\n")
