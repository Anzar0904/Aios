import pytest
import sqlite3
from unittest.mock import MagicMock

from aios.services.persistence import (
    PersistenceConfigurationService,
    PersistenceRegistry,
    RepositoryRegistry,
    PersistenceService,
)
from aios.services.persistence_impl import (
    PostgreSQLProvider,
    PersistenceServiceImpl,
    PersistenceHealthMonitor,
    PersistenceDiagnostics,
    PersistenceValidator,
    PersistenceReportGenerator,
)


def test_configuration():
    config = PersistenceConfigurationService()
    assert config.provider_name == "postgresql"
    assert config.host == "localhost"
    assert config.port == 5432
    assert config.pool_min_size == 2
    assert config.pool_max_size == 10


def test_connection_lifecycle_and_pool():
    config = PersistenceConfigurationService()
    config.pool_min_size = 2
    config.pool_max_size = 3
    config.connection_timeout = 1

    provider = PostgreSQLProvider()
    provider.initialize(config)
    provider.connect()

    assert provider.is_connected() is True
    assert len(provider.pool.all_connections) == 2
    assert provider.pool.active_count == 0

    # Acquire connection
    conn1 = provider.pool.acquire()
    assert provider.pool.active_count == 1
    assert isinstance(conn1, sqlite3.Connection)

    conn2 = provider.pool.acquire()
    assert provider.pool.active_count == 2

    # Pool grows up to max_size
    conn3 = provider.pool.acquire()
    assert provider.pool.active_count == 3
    assert len(provider.pool.all_connections) == 3

    # Try to acquire another -> exhausted timeout
    with pytest.raises(TimeoutError):
        provider.pool.acquire()

    # Release connection back
    provider.pool.release(conn1)
    assert provider.pool.active_count == 2

    # Acquire again after release
    conn4 = provider.pool.acquire()
    assert provider.pool.active_count == 3

    provider.disconnect()
    assert len(provider.pool.all_connections) == 0


def test_transactions():
    config = PersistenceConfigurationService()
    provider = PostgreSQLProvider()
    provider.initialize(config)
    provider.connect()

    # Create dummy table for testing transactions
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
    provider = PostgreSQLProvider()
    provider.initialize(config)
    provider.connect()

    provider.execute("CREATE TABLE test_nested (id INTEGER PRIMARY KEY, val TEXT)")

    # Start outer transaction
    provider.begin_transaction()
    provider.execute("INSERT INTO test_nested (id, val) VALUES (1, 'outer')")

    # Start inner nested transaction (Savepoint sp_1)
    provider.begin_transaction()
    provider.execute("INSERT INTO test_nested (id, val) VALUES (2, 'inner')")
    provider.rollback_transaction()  # Rollback inner only

    # Outer insert should still exist, inner rolled back
    provider.commit_transaction()  # Commit outer

    rows = provider.execute("SELECT * FROM test_nested ORDER BY id")
    assert len(rows) == 1
    assert rows[0]["id"] == 1
    assert rows[0]["val"] == "outer"

    provider.disconnect()


def test_migrations():
    config = PersistenceConfigurationService()
    provider = PostgreSQLProvider()
    provider.initialize(config)
    provider.connect()

    mgr = provider.migration_manager
    assert mgr is not None

    # Register migrations
    mgr.register_migration(1, "Create Users", "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    mgr.register_migration(2, "Create Logins", "CREATE TABLE logins (id INTEGER PRIMARY KEY, user_id INTEGER)")

    # Validate sequence
    assert len(mgr.validate_migrations()) == 0

    # Test pending discovery
    pending = mgr.get_pending_migrations()
    assert len(pending) == 2
    assert pending[0].version == 1

    # Execute migrations
    executed = mgr.execute_migrations()
    assert executed == 2

    # Check database migration history table
    applied = mgr.get_applied_versions()
    assert applied == [1, 2]

    # Verify tables actually created
    provider.execute("INSERT INTO users (id, name) VALUES (1, 'Anzar')")
    rows = provider.execute("SELECT * FROM users")
    assert len(rows) == 1
    assert rows[0]["name"] == "Anzar"

    # Subsequent run should execute 0 pending migrations
    executed_again = mgr.execute_migrations()
    assert executed_again == 0

    provider.disconnect()


def test_migration_sequence_validation():
    config = PersistenceConfigurationService()
    provider = PostgreSQLProvider()
    provider.initialize(config)
    provider.connect()

    mgr = provider.migration_manager

    # Duplicate versions
    mgr.register_migration(1, "First", "SELECT 1")
    mgr.register_migration(1, "Duplicate", "SELECT 1")
    errors = mgr.validate_migrations()
    assert len(errors) > 0
    assert "Duplicate migration versions detected" in errors[0]

    # Out of order registration (should be sorted by register_migration automatically)
    mgr.registered_migrations.clear()
    mgr.register_migration(2, "Second", "SELECT 1")
    mgr.register_migration(1, "First", "SELECT 1")
    assert mgr.registered_migrations[0].version == 1
    assert mgr.registered_migrations[1].version == 2
    assert len(mgr.validate_migrations()) == 0

    provider.disconnect()


def test_repository_registry():
    registry = RepositoryRegistry()
    mock_repo = MagicMock()

    registry.register_repository("user_repo", mock_repo)
    assert registry.get_repository("user_repo") == mock_repo

    with pytest.raises(KeyError):
        registry.get_repository("non_existent")


def test_diagnostics():
    config = PersistenceConfigurationService()
    registry = PersistenceRegistry()
    p_repos = RepositoryRegistry()
    registry.register_provider("postgresql", PostgreSQLProvider)
    
    service = PersistenceServiceImpl(config, registry, p_repos)
    diagnostics = PersistenceDiagnostics(config, service)

    # 1. Test before initialization (provider is None)
    diag1 = diagnostics.run_diagnostics()
    assert diag1["status"] == "error"
    assert "Provider was not initialized" in diag1["issues"][0]["message"]

    service.initialize()
    # 2. Test before connect (connected is False)
    diag2 = diagnostics.run_diagnostics()
    assert diag2["status"] == "error"
    assert "Connection Failure" in diag2["issues"][0]["type"]

    service.on_ready()
    # 3. Test after healthy connection (connected is True)
    diag3 = diagnostics.run_diagnostics()
    assert diag3["status"] == "ok"
    assert len(diag3["issues"]) == 0

    # 4. Test Configuration Errors
    config.pool_min_size = 0
    diag_config = diagnostics.run_diagnostics()
    assert diag_config["status"] == "error"
    assert "Min pool size must be greater than zero" in diag_config["issues"][0]["message"]

    service.teardown()


def test_health_monitor():
    config = PersistenceConfigurationService()
    registry = PersistenceRegistry()
    p_repos = RepositoryRegistry()
    registry.register_provider("postgresql", PostgreSQLProvider)
    
    service = PersistenceServiceImpl(config, registry, p_repos)
    health_monitor = PersistenceHealthMonitor(service)

    # Health check before initialization
    h1 = health_monitor.check_health()
    assert h1["status"] == "offline"
    assert h1["server_reachable"] is False

    service.initialize()
    service.on_ready()

    # Make some query calls to record metrics/latencies
    service.execute("SELECT 1")
    service.execute("SELECT 2")

    h2 = health_monitor.check_health()
    assert h2["status"] == "online"
    assert h2["server_reachable"] is True
    assert h2["metrics"]["success_calls"] >= 3  # select 1, select 2, and health check validation select 1

    service.teardown()


def test_validator():
    validator = PersistenceValidator()
    errs = validator.validate_config("", 5432)
    assert len(errs) == 1
    assert "Database host cannot be empty" in errs[0]

    errs2 = validator.validate_config("localhost", 999999)
    assert len(errs2) == 1
    assert "Database port must be a valid range" in errs2[0]


def test_report_generator(tmp_path):
    config = PersistenceConfigurationService()
    registry = PersistenceRegistry()
    p_repos = RepositoryRegistry()
    registry.register_provider("postgresql", PostgreSQLProvider)
    
    service = PersistenceServiceImpl(config, registry, p_repos)
    service.initialize()
    service.on_ready()

    health = PersistenceHealthMonitor(service)
    diagnostics = PersistenceDiagnostics(config, service)
    report_gen = PersistenceReportGenerator(str(tmp_path), health, diagnostics)

    report_gen.generate_reports()

    # Verify generated markdown files exist
    assert (tmp_path / "docs" / "persistence" / "PERSISTENCE_STATUS.md").exists()
    assert (tmp_path / "docs" / "persistence" / "PERSISTENCE_HEALTH.md").exists()
    assert (tmp_path / "docs" / "persistence" / "PERSISTENCE_DIAGNOSTICS.md").exists()

    service.teardown()
