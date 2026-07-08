import os
import time
import pytest
from typing import Dict, Any, List
from unittest.mock import MagicMock

from aios.registry import ServiceRegistry
from aios.services.persistence import (
    PersistenceConfigurationService,
    PersistenceRegistry,
    RepositoryRegistry,
    PersistenceService,
    SessionPolicy,
    SessionRegistry,
    SessionExpirationManager,
    SessionRecoveryManager,
    SessionStatisticsCollector,
    SessionHealthMonitor,
    SessionDiagnostics,
    SessionRecommendationEngine,
    SessionStore,
    SessionManager,
    RedisSessionService,
    RedisProvider,
)

from aios.services.persistence_impl import (
    PostgreSQLProvider,
    PersistenceServiceImpl,
    PersistenceBootstrapper,
    RedisConfigurationService,
    RedisConnectionManager,
    RedisTransportImpl,
    RedisProviderImpl,
    FakeRedisClient,
    SessionRegistryImpl,
    SessionStatisticsCollectorImpl,
    SessionDiagnosticsImpl,
    SessionHealthMonitorImpl,
    SessionRecommendationEngineImpl,
    SessionStoreImpl,
    SessionExpirationManagerImpl,
    SessionRecoveryManagerImpl,
    SessionManagerImpl,
    RedisSessionServiceImpl,
)

from tests.test_persistence import SQLiteTransportForTests


@pytest.fixture
def session_env():
    # 1. Setup SQLite database mock
    p_config = PersistenceConfigurationService()
    p_registry = PersistenceRegistry()
    p_registry.register_provider("postgresql", PostgreSQLProvider)
    p_repos = RepositoryRegistry()

    transport = SQLiteTransportForTests(p_config)
    provider = PostgreSQLProvider(transport=transport)

    p_service = PersistenceServiceImpl(p_config, p_registry, p_repos)
    p_service.active_provider = provider
    provider.initialize(p_config)
    provider.connect()

    bootstrapper = PersistenceBootstrapper(p_service)
    bootstrapper.initialize()
    bootstrapper.start()

    # 2. Setup Redis Session Platform Mock
    redis_cfg = RedisConfigurationService()
    redis_conn = RedisConnectionManager(redis_cfg)
    redis_transport = RedisTransportImpl(redis_cfg, redis_conn)
    redis_provider = RedisProviderImpl(redis_transport)

    # Force simulated client
    redis_conn.client = FakeRedisClient()
    redis_transport.client = redis_conn.client

    session_registry = SessionRegistryImpl()
    session_stats = SessionStatisticsCollectorImpl()
    session_diag = SessionDiagnosticsImpl(redis_provider)
    session_health = SessionHealthMonitorImpl(redis_provider)
    session_recommend = SessionRecommendationEngineImpl(session_stats, session_diag)
    session_store = SessionStoreImpl(
        redis_provider,
        session_registry,
        session_stats,
        session_diag
    )
    session_expiration = SessionExpirationManagerImpl(session_store, session_registry)
    session_recovery = SessionRecoveryManagerImpl(p_service, redis_provider, session_stats)
    session_manager = SessionManagerImpl(
        session_store,
        session_recovery,
        session_registry,
        session_stats
    )
    redis_session_service = RedisSessionServiceImpl(
        redis_provider,
        session_registry,
        session_store,
        session_manager,
        session_stats,
        session_diag
    )

    session_registry.initialize()
    session_stats.initialize()
    session_diag.initialize()
    session_health.initialize()
    session_recommend.initialize()
    session_store.initialize()
    session_expiration.initialize()
    session_recovery.initialize()
    session_manager.initialize()
    redis_session_service.initialize()

    # Global Registry setup
    registry = ServiceRegistry()
    registry.register(PersistenceService, p_service)
    registry.register(RedisProvider, redis_provider)
    registry.register(SessionRegistry, session_registry)
    registry.register(SessionStatisticsCollector, session_stats)
    registry.register(SessionDiagnostics, session_diag)
    registry.register(SessionHealthMonitor, session_health)
    registry.register(SessionRecommendationEngine, session_recommend)
    registry.register(SessionStore, session_store)
    registry.register(SessionExpirationManager, session_expiration)
    registry.register(SessionRecoveryManager, session_recovery)
    registry.register(SessionManager, session_manager)
    registry.register(RedisSessionService, redis_session_service)

    yield {
        "p_service": p_service,
        "redis_provider": redis_provider,
        "session_registry": session_registry,
        "session_stats": session_stats,
        "session_diag": session_diag,
        "session_health": session_health,
        "session_recommend": session_recommend,
        "session_store": session_store,
        "session_expiration": session_expiration,
        "session_recovery": session_recovery,
        "session_manager": session_manager,
        "redis_session_service": redis_session_service,
    }
    ServiceRegistry._global_registry = None


def test_session_ownership_registry(session_env):
    reg = session_env["session_registry"]
    
    # Check default pre-registered session types
    all_types = reg.get_all_types()
    assert "ai" in all_types
    assert "workspace" in all_types
    assert "workflow" in all_types
    assert "provider" in all_types
    assert "engineering" in all_types
    assert "automation" in all_types
    assert "temporary_execution" in all_types
    assert "runtime_validation" in all_types

    cfg = reg.get_configuration("workspace")
    assert cfg["owner_service"] == "WorkspaceService"
    assert cfg["ttl"] == 86400.0
    assert cfg["policy"] == SessionPolicy.PERSISTENT_REFERENCE
    assert cfg["redis_prefix"] == "workspace"


def test_session_creation_read_update_delete(session_env):
    mgr = session_env["session_manager"]
    stats = session_env["session_stats"]

    session_data = {"user": "alice", "active": True}

    # Create Session
    created = mgr.create_session("ai", "session-123", session_data, workspace_id="ws-abc", project_id="proj-xyz")
    assert created is True
    assert stats.creates.get("ai", 0) == 1

    # Read Session
    read_data = mgr.get_session("ai", "session-123")
    assert read_data is not None
    assert read_data["user"] == "alice"
    assert stats.reads.get("ai:hit", 0) == 1

    # Update Session
    updated_data = {"user": "alice", "active": False, "role": "admin"}
    updated = mgr.update_session("ai", "session-123", updated_data)
    assert updated is True
    assert stats.updates.get("ai", 0) == 1

    # Verify updated content
    read_updated = mgr.get_session("ai", "session-123")
    assert read_updated["role"] == "admin"

    # Delete Session
    deleted = mgr.delete_session("ai", "session-123")
    assert deleted is True
    assert stats.deletes.get("ai", 0) == 1

    # Read deleted session -> should be None
    read_deleted = mgr.get_session("ai", "session-123")
    assert read_deleted is None


def test_sliding_expiration_and_heartbeat(session_env):
    mgr = session_env["session_manager"]
    stats = session_env["session_stats"]
    provider = session_env["redis_provider"]

    mgr.create_session("ai", "session-exp", {"status": "ok"})
    
    # Explicitly check stats are clean
    stats.renewals["ai"] = 0
    stats.heartbeats["ai"] = 0

    # Renew Session
    renewed = mgr.renew_session("ai", "session-exp")
    assert renewed is True
    assert stats.renewals.get("ai", 0) == 1

    # Heartbeat updates
    hb = mgr.heartbeat("ai", "session-exp")
    assert hb is True
    assert stats.heartbeats.get("ai", 0) == 1
    assert stats.renewals.get("ai", 0) == 2 # heartbeat calls renew internally


def test_session_recovery_and_reconstruct(session_env):
    mgr = session_env["session_manager"]
    recovery = session_env["session_recovery"]
    stats = session_env["session_stats"]

    # Register recovery handler for recoverable workflow session type
    mock_handler = MagicMock(return_value={"workflow_state": "running", "step": 3})
    recovery.register_recovery_handler("workflow", mock_handler)

    # Read workflow session that does not exist in Redis -> trigger recovery
    recovered_data = mgr.get_session("workflow", "wf-session-999")
    assert recovered_data is not None
    assert recovered_data["step"] == 3
    
    mock_handler.assert_called_once_with("wf-session-999")
    assert stats.recoveries.get("workflow", 0) == 1
    assert stats.recovery_success.get("workflow", 0) == 1

    # Next get should hit cache/Redis directly without handler call
    recovered_data_cached = mgr.get_session("workflow", "wf-session-999")
    assert recovered_data_cached is not None
    assert mock_handler.call_count == 1


def test_session_outage_fallback(session_env):
    mgr = session_env["session_manager"]
    store = session_env["session_store"]
    provider = session_env["redis_provider"]

    # Simulate connection outage on low-level client
    provider.transport.execute_command = MagicMock(side_effect=RuntimeError("Redis connection lost"))

    # Session Platform should automatically degrade to fallback local memory store
    created = mgr.create_session("provider", "prov-session-1", {"provider": "openai"})
    assert created is True

    # Read from fallback store
    data = mgr.get_session("provider", "prov-session-1")
    assert data is not None
    assert data["provider"] == "openai"


def test_session_statistics_diagnostics_recommendations(session_env):
    mgr = session_env["session_manager"]
    stats = session_env["session_stats"]
    diag = session_env["session_diag"]
    recommend = session_env["session_recommend"]

    mgr.create_session("temporary_execution", "temp-1", {"val": "exec"})
    mgr.get_session("temporary_execution", "temp-1")

    # Metrics
    metrics = stats.get_metrics()
    assert metrics["session_creates"]["temporary_execution"] == 1
    assert metrics["session_reads"]["temporary_execution:hit"] == 1
    assert metrics["learning_metadata"]["session_duration_trends"] == "stable"

    # Diagnostics
    diag_info = diag.get_diagnostics()
    assert diag_info["status"] in ("healthy", "degraded")

    # Recommendations
    recs = recommend.get_recommendations()
    assert len(recs) > 0
