from typing import List, Optional
from unittest.mock import MagicMock

import pytest
from aios.services.persistence import (
    DatabaseTransport,
    PersistenceConfigurationService,
    PersistencePolicy,
    PersistenceRegistry,
    PersistenceResult,
    PersistenceStatus,
    RepositoryRegistry,
    TransportCapabilities,
    TransportHealth,
    TransportResult,
    TransportTransaction,
)
from aios.services.persistence_impl import (
    MigrationManager,
    PersistenceServiceImpl,
    PostgreSQLProvider,
    TransactionStackManager,
    WorkspaceRepositoryImpl,
)


class OfflineDatabaseTransport(DatabaseTransport):
    """Database transport simulating an offline state."""
    def __init__(self, config: PersistenceConfigurationService) -> None:
        super().__init__(config)
        self.awaiting_configuration = False

    def validate_configuration(self) -> List[str]:
        return []

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def execute(self, query: str, params: Optional[tuple] = None) -> TransportResult:
        raise ConnectionError("Database host not reachable.")

    def execute_many(self, query: str, params_list: List[tuple]) -> List[TransportResult]:
        raise ConnectionError("Database host not reachable.")

    def begin_transaction(self) -> TransportTransaction:
        raise ConnectionError("Database host not reachable.")

    def health(self) -> TransportHealth:
        return TransportHealth(is_alive=False, latency_ms=0.0, error_message="Database host not reachable.")

    def capabilities(self) -> TransportCapabilities:
        return TransportCapabilities(support_savepoints=True, support_json=True)

class AwaitingConfigDatabaseTransport(OfflineDatabaseTransport):
    """Database transport simulating awaiting configuration state."""
    def __init__(self, config: PersistenceConfigurationService) -> None:
        super().__init__(config)
        self.awaiting_configuration = True

    def health(self) -> TransportHealth:
        return TransportHealth(is_alive=False, latency_ms=0.0, error_message="Awaiting Runtime Configuration")

class MockOfflinePostgreSQLProvider(PostgreSQLProvider):
    def initialize(self, config: PersistenceConfigurationService) -> None:
        self.config = config
        self.transport = OfflineDatabaseTransport(config)
        self.migration_manager = MigrationManager(self)
        self.tx_manager = TransactionStackManager(self.transport)

class MockAwaitingConfigPostgreSQLProvider(PostgreSQLProvider):
    def initialize(self, config: PersistenceConfigurationService) -> None:
        self.config = config
        self.transport = AwaitingConfigDatabaseTransport(config)
        self.migration_manager = MigrationManager(self)
        self.tx_manager = TransactionStackManager(self.transport)

def test_strict_policy_fails_immediately():
    config = PersistenceConfigurationService()
    config.policy = PersistencePolicy.STRICT
    config.provider_name = "postgresql"

    registry = PersistenceRegistry()
    registry.register_provider("postgresql", MockOfflinePostgreSQLProvider)

    repos = RepositoryRegistry()
    service = PersistenceServiceImpl(config, registry, repos)
    service.initialize()
    service.start()

    repo = WorkspaceRepositoryImpl(service)
    repos.register_repository("workspaces", repo)

    with pytest.raises(RuntimeError) as excinfo:
        repo.save({"id": "ws-1", "name": "Strict Test"})
    assert "Database is offline" in str(excinfo.value)

def test_awaiting_config_fails_immediately_in_strict():
    config = PersistenceConfigurationService()
    config.policy = PersistencePolicy.STRICT
    config.provider_name = "postgresql"

    registry = PersistenceRegistry()
    registry.register_provider("postgresql", MockAwaitingConfigPostgreSQLProvider)

    repos = RepositoryRegistry()
    service = PersistenceServiceImpl(config, registry, repos)
    service.initialize()
    service.start()

    repo = WorkspaceRepositoryImpl(service)
    repos.register_repository("workspaces", repo)

    with pytest.raises(RuntimeError) as excinfo:
        repo.save({"id": "ws-1", "name": "Strict Test"})
    assert "Awaiting Runtime Configuration" in str(excinfo.value)

def test_best_effort_policy_returns_failure_result():
    config = PersistenceConfigurationService()
    config.policy = PersistencePolicy.BEST_EFFORT
    config.provider_name = "postgresql"

    registry = PersistenceRegistry()
    registry.register_provider("postgresql", MockOfflinePostgreSQLProvider)
    registry.register_provider("sqlite", MockOfflinePostgreSQLProvider)

    repos = RepositoryRegistry()
    service = PersistenceServiceImpl(config, registry, repos)
    service.initialize()
    service.start()

    repo = WorkspaceRepositoryImpl(service)
    repos.register_repository("workspaces", repo)

    # Sabotage transport to test failure behavior
    service.active_provider.transport.health = lambda: TransportHealth(is_alive=False, latency_ms=0, error_message="Mock Offline")

    result = repo.save({"id": "ws-1", "name": "Best Effort Test"})
    assert result.status == PersistenceStatus.PERSISTENCE_UNAVAILABLE
    assert result.repository == "workspaces"
    assert "remediation" in result.diagnostics

def test_read_only_policy_blocks_writes():
    config = PersistenceConfigurationService()
    config.policy = PersistencePolicy.READ_ONLY
    config.provider_name = "postgresql"

    registry = PersistenceRegistry()
    registry.register_provider("postgresql", MockOfflinePostgreSQLProvider)

    repos = RepositoryRegistry()
    service = PersistenceServiceImpl(config, registry, repos)
    service.initialize()
    service.start()

    repo = WorkspaceRepositoryImpl(service)
    repos.register_repository("workspaces", repo)

    result = repo.save({"id": "ws-1", "name": "Read Only Test"})
    assert result.status == PersistenceStatus.READ_ONLY_MODE
    assert result.repository == "workspaces"

def test_persistence_result_attributes():
    res = PersistenceResult(
        status=PersistenceStatus.SUCCESS,
        message="Success message",
        provider="postgresql",
        latency=12.5,
        repository="workspaces",
        payload={"some": "data"}
    )
    assert res.status == PersistenceStatus.SUCCESS
    assert res.message == "Success message"
    assert res.provider == "postgresql"
    assert res.latency == 12.5
    assert res.repository == "workspaces"
    assert res.payload == {"some": "data"}
    assert res.operation_id is not None
    assert res.timestamp is not None

def test_profile_service_strict_policy_fails_on_db_disconnect():
    from aios.services.engineering_profile import EngineeringProfile
    from aios.services.engineering_profile_impl import LocalEngineeringProfileService
    from aios.services.memory import MemoryService
    from aios.services.persistence_impl import EngineeringProfileRepositoryImpl

    config = PersistenceConfigurationService()
    config.policy = PersistencePolicy.STRICT
    config.provider_name = "postgresql"

    registry = PersistenceRegistry()
    registry.register_provider("postgresql", MockOfflinePostgreSQLProvider)

    repos = RepositoryRegistry()
    service = PersistenceServiceImpl(config, registry, repos)
    service.initialize()
    service.start()

    repo = EngineeringProfileRepositoryImpl(service)
    repos.register_repository("engineering_profiles", repo)

    memory_svc = MagicMock(spec=MemoryService)
    profile_svc = LocalEngineeringProfileService(
        memory_service=memory_svc,
        registry=None,
        profile_repo=repo
    )

    from aios.services.engineering_profile import (
        AutomationProfile,
        CodingProfile,
        DocumentationProfile,
        ExecutionProfile,
        GitHubProfile,
        ProjectProfile,
        ReleaseProfile,
        TestingProfile,
        WorkspaceProfile,
    )
    profile = EngineeringProfile(
        profile_id="test_profile",
        project=ProjectProfile(project_name="Test Project", version="1.0.0", description=""),
        coding=CodingProfile(language="python", coding_standards=[], naming_conventions={}),
        testing=TestingProfile(framework="pytest", min_statement_coverage=80.0, min_branch_coverage=75.0),
        execution=ExecutionProfile(max_timeout_seconds=300, sandbox_enabled=True),
        documentation=DocumentationProfile(format="markdown", generate_api_docs=True, release_formatting_rules={}, markdown_preferences={}, section_ordering=[], naming_conventions={}, versioning_preferences={}),
        github=GitHubProfile(org_name="org", repo_name="repo", default_branch="main"),
        release=ReleaseProfile(auto_release=False, versioning_scheme="semver"),
        automation=AutomationProfile(cron_expression="", max_retries=3),
        workspace=WorkspaceProfile(workspace_root="/tmp", exclude_patterns=[]),
        timestamp=0.0
    )

    with pytest.raises(RuntimeError) as excinfo:
        profile_svc.save_profile(profile)
    assert "Strict persistence save failure" in str(excinfo.value)

def test_profile_service_best_effort_policy_registers_in_memory():
    from aios.services.engineering_profile import EngineeringProfile
    from aios.services.engineering_profile_impl import LocalEngineeringProfileService
    from aios.services.memory import MemoryService
    from aios.services.persistence_impl import EngineeringProfileRepositoryImpl

    config = PersistenceConfigurationService()
    config.policy = PersistencePolicy.BEST_EFFORT
    config.provider_name = "postgresql"

    registry = PersistenceRegistry()
    registry.register_provider("postgresql", MockOfflinePostgreSQLProvider)

    repos = RepositoryRegistry()
    service = PersistenceServiceImpl(config, registry, repos)
    service.initialize()
    service.start()

    repo = EngineeringProfileRepositoryImpl(service)
    repos.register_repository("engineering_profiles", repo)

    memory_svc = MagicMock(spec=MemoryService)
    profile_svc = LocalEngineeringProfileService(
        memory_service=memory_svc,
        registry=None,
        profile_repo=repo
    )

    from aios.services.engineering_profile import (
        AutomationProfile,
        CodingProfile,
        DocumentationProfile,
        ExecutionProfile,
        GitHubProfile,
        ProjectProfile,
        ReleaseProfile,
        TestingProfile,
        WorkspaceProfile,
    )
    profile = EngineeringProfile(
        profile_id="test_profile",
        project=ProjectProfile(project_name="Test Project", version="1.0.0", description=""),
        coding=CodingProfile(language="python", coding_standards=[], naming_conventions={}),
        testing=TestingProfile(framework="pytest", min_statement_coverage=80.0, min_branch_coverage=75.0),
        execution=ExecutionProfile(max_timeout_seconds=300, sandbox_enabled=True),
        documentation=DocumentationProfile(format="markdown", generate_api_docs=True, release_formatting_rules={}, markdown_preferences={}, section_ordering=[], naming_conventions={}, versioning_preferences={}),
        github=GitHubProfile(org_name="org", repo_name="repo", default_branch="main"),
        release=ReleaseProfile(auto_release=False, versioning_scheme="semver"),
        automation=AutomationProfile(cron_expression="", max_retries=3),
        workspace=WorkspaceProfile(workspace_root="/tmp", exclude_patterns=[]),
        timestamp=0.0
    )

    # Under BEST_EFFORT, saving shouldn't raise even if db is offline
    profile_svc.save_profile(profile)
    # The profile should be registered in memory successfully
    loaded = profile_svc.get_profile("test_profile")
    assert loaded is not None
    assert loaded.project.project_name == "Test Project"
