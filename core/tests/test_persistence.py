import queue
import sqlite3
import pytest
from unittest.mock import MagicMock
from typing import List, Dict, Any, Optional

from aios.services.persistence import (
    PersistenceConfigurationService,
    PersistenceRegistry,
    RepositoryRegistry,
    PersistenceService,
    DatabaseTransport,
    TransportTransaction,
    TransportResult,
    TransportCapabilities,
    TransportHealth,
)
from aios.services.persistence_impl import (
    PostgreSQLProvider,
    PersistenceServiceImpl,
    PersistenceHealthMonitor,
    PersistenceDiagnostics,
    PersistenceValidator,
    PersistenceReportGenerator,
)


class SQLiteTransportForTests(DatabaseTransport):
    """SQLite-backed database transport used strictly inside tests."""

    def __init__(self, config: PersistenceConfigurationService) -> None:
        super().__init__(config)
        self.pool = None
        self.active_conn = None
        self.tx_depth = 0
        self._db_uri = "file:persistence_test_db?mode=memory&cache=shared"

    def validate_configuration(self) -> List[str]:
        return []

    def connect(self) -> None:
        def factory():
            conn = sqlite3.connect(self._db_uri, uri=True, timeout=30.0)
            conn.isolation_level = None
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA busy_timeout = 30000")
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
                    raise TimeoutError("Pool exhausted")

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

        self.pool = SimplePool(self.config.pool_min_size, self.config.pool_max_size, factory)

    def disconnect(self) -> None:
        if self.pool:
            self.pool.close()

    def execute(self, query: str, params: Optional[tuple] = None) -> TransportResult:
        if not self.pool:
            raise RuntimeError("Not connected")
        
        if self.active_conn:
            cursor = self.active_conn.cursor()
            cursor.execute(query, params or ())
            try:
                desc = cursor.description
                if desc:
                    colnames = [d[0] for d in desc]
                    rows = [dict(zip(colnames, row)) for row in cursor.fetchall()]
                else:
                    rows = []
                return TransportResult(rows=rows, rows_affected=cursor.rowcount)
            except Exception:
                return TransportResult(rows=[], rows_affected=cursor.rowcount)
            finally:
                cursor.close()

        conn = self.pool.acquire()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            try:
                desc = cursor.description
                if desc:
                    colnames = [d[0] for d in desc]
                    rows = [dict(zip(colnames, row)) for row in cursor.fetchall()]
                else:
                    rows = []
                return TransportResult(rows=rows, rows_affected=cursor.rowcount)
            except Exception:
                return TransportResult(rows=[], rows_affected=cursor.rowcount)
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


class MockDatabaseTransport(DatabaseTransport):
    """Mock transport utilized to verify configurations and diagnostics."""

    def __init__(self, config: PersistenceConfigurationService) -> None:
        super().__init__(config)
        self.connect_called = False
        self.disconnect_called = False
        self.is_alive = True

    def validate_configuration(self) -> List[str]:
        return []

    def connect(self) -> None:
        self.connect_called = True

    def disconnect(self) -> None:
        self.disconnect_called = True

    def execute(self, query: str, params: Optional[tuple] = None) -> TransportResult:
        return TransportResult(rows=[{"result": "mocked"}])

    def execute_many(self, query: str, params_list: List[tuple]) -> List[TransportResult]:
        return [TransportResult(rows=[{"result": "mocked"}])]

    def begin_transaction(self) -> TransportTransaction:
        class MockTx(TransportTransaction):
            def commit(self) -> None:
                pass
            def rollback(self) -> None:
                pass
        return MockTx()

    def health(self) -> TransportHealth:
        return TransportHealth(is_alive=self.is_alive, latency_ms=5.0, error_message=None if self.is_alive else "Mock Offline")

    def capabilities(self) -> TransportCapabilities:
        return TransportCapabilities(support_savepoints=True, support_json=True)


def test_configuration():
    config = PersistenceConfigurationService()
    assert config.provider_name == "postgresql"
    assert config.pool_min_size == 2
    assert config.pool_max_size == 10


def test_connection_lifecycle_and_pool():
    config = PersistenceConfigurationService()
    config.pool_min_size = 2
    config.pool_max_size = 3

    # Inject SQLite test transport
    transport = SQLiteTransportForTests(config)
    provider = PostgreSQLProvider(transport=transport)
    provider.initialize(config)
    provider.connect()

    assert provider.is_connected() is True
    assert len(provider.transport.pool.all_conns) == 2

    # Acquire connection
    conn1 = provider.transport.pool.acquire()
    conn2 = provider.transport.pool.acquire()
    conn3 = provider.transport.pool.acquire()
    assert len(provider.transport.pool.all_conns) == 3

    # Try to acquire another -> exhausted timeout
    with pytest.raises(TimeoutError):
        provider.transport.pool.acquire()

    # Release connection back
    provider.transport.pool.release(conn1)
    provider.disconnect()


def test_transactions():
    config = PersistenceConfigurationService()
    transport = SQLiteTransportForTests(config)
    provider = PostgreSQLProvider(transport=transport)
    provider.initialize(config)
    provider.connect()

    provider.execute("CREATE TABLE test_tx (id INTEGER PRIMARY KEY, val TEXT)")

    # Test commit
    provider.begin_transaction()
    provider.execute("INSERT INTO test_tx (id, val) VALUES (1, 'commit_me')")
    provider.commit_transaction()

    rows = provider.execute("SELECT * FROM test_tx WHERE id = 1")
    assert len(rows) == 1
    assert rows[0]["val"] == "commit_me"

    # Test rollback
    provider.begin_transaction()
    provider.execute("INSERT INTO test_tx (id, val) VALUES (2, 'rollback_me')")
    provider.rollback_transaction()

    rows = provider.execute("SELECT * FROM test_tx WHERE id = 2")
    assert len(rows) == 0

    provider.disconnect()


def test_nested_transactions():
    config = PersistenceConfigurationService()
    transport = SQLiteTransportForTests(config)
    provider = PostgreSQLProvider(transport=transport)
    provider.initialize(config)
    provider.connect()

    provider.execute("CREATE TABLE test_nested (id INTEGER PRIMARY KEY, val TEXT)")

    # Start outer transaction
    provider.begin_transaction()
    provider.execute("INSERT INTO test_nested (id, val) VALUES (1, 'outer')")

    # Start inner nested transaction
    provider.begin_transaction()
    provider.execute("INSERT INTO test_nested (id, val) VALUES (2, 'inner')")
    provider.rollback_transaction()

    # Outer insert should still exist, inner rolled back
    provider.commit_transaction()

    rows = provider.execute("SELECT * FROM test_nested ORDER BY id")
    assert len(rows) == 1
    assert rows[0]["id"] == 1
    assert rows[0]["val"] == "outer"

    provider.disconnect()


def test_migrations():
    config = PersistenceConfigurationService()
    transport = SQLiteTransportForTests(config)
    provider = PostgreSQLProvider(transport=transport)
    provider.initialize(config)
    provider.connect()

    mgr = provider.migration_manager
    assert mgr is not None

    mgr.register_migration(1, "Create Users", "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    mgr.register_migration(2, "Create Logins", "CREATE TABLE logins (id INTEGER PRIMARY KEY, user_id INTEGER)")

    assert len(mgr.validate_migrations()) == 0

    pending = mgr.get_pending_migrations()
    assert len(pending) == 2

    executed = mgr.execute_migrations()
    assert executed == 2

    applied = mgr.get_applied_versions()
    assert applied == [1, 2]

    provider.execute("INSERT INTO users (id, name) VALUES (1, 'Anzar')")
    rows = provider.execute("SELECT * FROM users")
    assert len(rows) == 1
    assert rows[0]["name"] == "Anzar"

    executed_again = mgr.execute_migrations()
    assert executed_again == 0

    provider.disconnect()


def test_repository_registry():
    registry = RepositoryRegistry()
    mock_repo = MagicMock()

    registry.register_repository("user_repo", mock_repo)
    assert registry.get_repository("user_repo") == mock_repo


def test_diagnostics():
    config = PersistenceConfigurationService()
    registry = PersistenceRegistry()
    p_repos = RepositoryRegistry()
    registry.register_provider("postgresql", PostgreSQLProvider)
    
    service = PersistenceServiceImpl(config, registry, p_repos)
    diagnostics = PersistenceDiagnostics(config, service)

    # 1. Awaiting Configuration before real credentials
    service.initialize()
    diag = diagnostics.run_diagnostics()
    assert diag["status"] == "error"
    assert "Awaiting Runtime Configuration" in diag["issues"][0]["message"]

    # 2. Inject Mock Transport for Healthy Validation
    mock_transport = MockDatabaseTransport(config)
    service.active_provider.transport = mock_transport
    service.active_provider.connect()
    
    diag2 = diagnostics.run_diagnostics()
    assert diag2["status"] == "ok"
    assert len(diag2["issues"]) == 0

    # 3. Connection Failure warning mapping
    mock_transport.is_alive = False
    diag3 = diagnostics.run_diagnostics()
    assert diag3["status"] == "error"
    assert "Connection Failure" in diag3["issues"][0]["type"]


def test_health_monitor():
    config = PersistenceConfigurationService()
    registry = PersistenceRegistry()
    p_repos = RepositoryRegistry()
    registry.register_provider("postgresql", PostgreSQLProvider)
    
    service = PersistenceServiceImpl(config, registry, p_repos)
    health_monitor = PersistenceHealthMonitor(service)

    service.initialize()
    # Awaiting config health check
    h = health_monitor.check_health()
    assert h["status"] == "offline"
    assert "Awaiting Runtime Configuration" in h["issues"][0]

    # Inject SQLite test transport
    transport = SQLiteTransportForTests(config)
    service.active_provider.transport = transport
    service.on_ready()

    service.execute("SELECT 1")
    h2 = health_monitor.check_health()
    assert h2["status"] == "online"
    assert h2["server_reachable"] is True


def test_validator():
    validator = PersistenceValidator()
    errs = validator.validate_config("", 5432)
    assert len(errs) == 1
    assert "Database host cannot be empty" in errs[0]


def test_report_generator(tmp_path):
    config = PersistenceConfigurationService()
    registry = PersistenceRegistry()
    p_repos = RepositoryRegistry()
    registry.register_provider("postgresql", PostgreSQLProvider)
    
    service = PersistenceServiceImpl(config, registry, p_repos)
    service.initialize()
    mock_transport = MockDatabaseTransport(config)
    service.active_provider.transport = mock_transport
    service.on_ready()

    health = PersistenceHealthMonitor(service)
    diagnostics = PersistenceDiagnostics(config, service)
    report_gen = PersistenceReportGenerator(str(tmp_path), health, diagnostics)

    report_gen.generate_reports()
    assert (tmp_path / "docs" / "persistence" / "PERSISTENCE_STATUS.md").exists()
