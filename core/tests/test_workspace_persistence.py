import os
import time
import pytest
from typing import Dict, Any, List

from aios.services.persistence import (
    PersistenceConfigurationService,
    PersistenceRegistry,
    RepositoryRegistry,
    PersistenceService,
    WorkspaceRepository,
    WorkspaceSessionRepository,
    ProjectRepository,
    EngineeringProfileRepository,
    ConfigurationRepository,
    WorkspacePersistenceService,
)

from aios.services.persistence_impl import (
    PostgreSQLProvider,
    PersistenceServiceImpl,
    PersistenceHealthMonitor,
    PersistenceDiagnostics,
    PersistenceValidator,
    PersistenceReportGenerator,
    WorkspaceRepositoryImpl,
    WorkspaceSessionRepositoryImpl,
    ProjectRepositoryImpl,
    EngineeringProfileRepositoryImpl,
    ConfigurationRepositoryImpl,
    WorkspacePersistenceValidator,
    WorkspacePersistenceTelemetry,
    WorkspacePersistenceStatistics,
    WorkspacePersistenceServiceImpl,
    WorkspacePersistenceReportGenerator,
    PersistenceBootstrapper,
)

from aios.services.engineering_profile_impl import LocalEngineeringProfileService
from aios.services.engineering_profile import (
    ProjectProfile,
    EngineeringProfile,
    CodingProfile,
    TestingProfile,
    ExecutionProfile,
    DocumentationProfile,
    GitHubProfile,
    ReleaseProfile,
    AutomationProfile,
    WorkspaceProfile,
)

from tests.test_persistence import SQLiteTransportForTests


@pytest.fixture
def persistence_setup():
    config = PersistenceConfigurationService()
    registry = PersistenceRegistry()
    registry.register_provider("postgresql", PostgreSQLProvider)
    repos = RepositoryRegistry()

    # Use SQLite transport in memory for the tests
    transport = SQLiteTransportForTests(config)
    provider = PostgreSQLProvider(transport=transport)

    service = PersistenceServiceImpl(config, registry, repos)
    service.active_provider = provider
    provider.initialize(config)
    provider.connect()

    # Bootstrap schemas
    bootstrapper = PersistenceBootstrapper(service)
    bootstrapper.initialize()
    bootstrapper.start()

    # Repositories
    workspace_repo = WorkspaceRepositoryImpl(service)
    session_repo = WorkspaceSessionRepositoryImpl(service)
    project_repo = ProjectRepositoryImpl(service)
    profile_repo = EngineeringProfileRepositoryImpl(service)
    config_repo = ConfigurationRepositoryImpl(service)

    # Register in registry
    repos.register_repository("workspaces", workspace_repo)
    repos.register_repository("workspace_sessions", session_repo)
    repos.register_repository("projects", project_repo)
    repos.register_repository("engineering_profiles", profile_repo)
    repos.register_repository("configuration_profiles", config_repo)

    # Workspace service
    wp_validator = WorkspacePersistenceValidator()
    wp_telemetry = WorkspacePersistenceTelemetry()
    wp_stats = WorkspacePersistenceStatistics(workspace_repo, session_repo)
    wp_service = WorkspacePersistenceServiceImpl(
        workspace_repo,
        session_repo,
        project_repo,
        profile_repo,
        config_repo,
        wp_validator,
        wp_telemetry,
        wp_stats,
    )

    yield {
        "service": service,
        "workspace_repo": workspace_repo,
        "session_repo": session_repo,
        "project_repo": project_repo,
        "profile_repo": profile_repo,
        "config_repo": config_repo,
        "wp_service": wp_service,
        "wp_telemetry": wp_telemetry,
        "wp_stats": wp_stats,
        "repos": repos,
    }

    provider.disconnect()


def test_workspace_lifecycle(persistence_setup):
    setup = persistence_setup
    wp_repo: WorkspaceRepository = setup["workspace_repo"]

    ws = {
        "id": "ws-1",
        "name": "Test Workspace",
        "metadata": {"key": "val"},
        "state": "active",
        "created_at": time.time(),
        "last_accessed": time.time(),
        "version": "1.0",
        "status": "healthy",
        "health": "green",
    }

    wp_repo.save(ws)

    loaded = wp_repo.get("ws-1")
    assert loaded is not None
    assert loaded["name"] == "Test Workspace"
    assert loaded["metadata"] == {"key": "val"}

    all_ws = wp_repo.list_all()
    assert len(all_ws) == 1

    wp_repo.delete("ws-1")
    assert wp_repo.get("ws-1") is None


def test_session_lifecycle(persistence_setup):
    setup = persistence_setup
    sess_repo: WorkspaceSessionRepository = setup["session_repo"]

    session = {
        "id": "session-1",
        "workspace_id": "ws-1",
        "start_time": time.time(),
        "end_time": time.time() + 3600,
        "state": "active",
        "current_task": "test-sprint",
        "current_branch": "main",
        "current_agent": "dev-agent",
        "current_provider": "local",
        "metrics": {"duration": 120},
        "health": "ok",
        "checkpoints": {"step_1": "done"},
        "resume_metadata": {"last_step": 1},
    }

    sess_repo.save(session)

    loaded = sess_repo.get("session-1")
    assert loaded is not None
    assert loaded["current_task"] == "test-sprint"
    assert loaded["metrics"] == {"duration": 120}

    sess_repo.delete("session-1")
    assert sess_repo.get("session-1") is None


def test_project_repository(persistence_setup):
    setup = persistence_setup
    proj_repo: ProjectRepository = setup["project_repo"]

    project = {
        "id": "proj-1",
        "workspace_id": "ws-1",
        "name": "AI OS Subsystem",
        "version": "1.2.3",
        "description": "Integration layer",
    }

    proj_repo.save(project)
    loaded = proj_repo.get("proj-1")
    assert loaded is not None
    assert loaded["version"] == "1.2.3"

    proj_repo.delete("proj-1")
    assert proj_repo.get("proj-1") is None


def test_engineering_profile_persistence_and_versioning(persistence_setup):
    setup = persistence_setup
    profile_repo: EngineeringProfileRepository = setup["profile_repo"]

    profile_dict = {
        "id": "prof-1",
        "workspace_id": "ws-1",
        "project_name": "Test Project",
        "project_version": "1.0",
        "project_description": "First version",
        "language": "python",
        "coding_standards": ["PEP8"],
        "naming_conventions": {"class": "PascalCase"},
        "testing_framework": "pytest",
        "min_statement_coverage": 80.0,
        "min_branch_coverage": 75.0,
        "max_timeout_seconds": 300,
        "sandbox_enabled": True,
        "documentation_format": "markdown",
        "generate_api_docs": True,
        "release_formatting_rules": {},
        "markdown_preferences": {},
        "section_ordering": [],
        "doc_naming_conventions": {},
        "doc_versioning_preferences": {},
        "github_org": "MyOrg",
        "github_repo": "MyRepo",
        "github_default_branch": "main",
        "auto_release": True,
        "versioning_scheme": "semver",
        "cron_expression": "*/5 * * * *",
        "max_retries": 3,
        "workspace_root": "/tmp/test",
        "exclude_patterns": [],
        "timestamp": time.time(),
    }

    profile_repo.save(profile_dict)

    # 1. Retrieve first version
    first_ver = profile_repo.get("prof-1")
    assert first_ver is not None
    assert first_ver["version"] == 1

    # 2. Update and check version bump & history
    profile_dict["project_description"] = "Second version"
    profile_repo.save(profile_dict)

    updated = profile_repo.get("prof-1")
    assert updated["version"] == 2
    assert updated["project_description"] == "Second version"

    history = profile_repo.get_history("prof-1")
    assert len(history) == 1
    assert history[0]["project_description"] == "First version"


def test_configuration_persistence(persistence_setup):
    setup = persistence_setup
    config_repo: ConfigurationRepository = setup["config_repo"]

    config = {
        "id": "config-1",
        "workspace_id": "ws-1",
        "env_profile": {"profile": "prod"},
        "workspace_settings": {"theme": "dark"},
        "provider_preferences": {"openai": "gpt-4"},
        "git_preferences": {"sign_commits": True},
        "automation_preferences": {"retries": 5},
        "documentation_preferences": {"include_timestamp": True},
        "testing_preferences": {"coverage": 90.0},
        "approval_preferences": {"min_approvals": 2},
    }

    config_repo.save(config)
    loaded = config_repo.get("config-1")
    assert loaded is not None
    assert loaded["env_profile"] == {"profile": "prod"}
    assert loaded["approval_preferences"] == {"min_approvals": 2}

    config_repo.delete("config-1")
    assert config_repo.get("config-1") is None


def test_transaction_rollback_via_savepoints(persistence_setup):
    setup = persistence_setup
    service: PersistenceService = setup["service"]
    wp_repo: WorkspaceRepository = setup["workspace_repo"]

    ws = {
        "id": "ws-rollback-test",
        "name": "Rollback Test",
        "metadata": {},
        "state": "active",
        "created_at": time.time(),
        "last_accessed": time.time(),
        "version": "1.0",
        "status": "healthy",
        "health": "green",
    }

    # Outer transaction
    service.begin_transaction()
    wp_repo.save(ws)

    # Nested savepoint transaction
    service.begin_transaction()
    ws["name"] = "Modified Name"
    wp_repo.save(ws)

    # Rollback nested transaction
    service.rollback_transaction()

    # Commit outer transaction
    service.commit_transaction()

    # Verify state: name should be the outer name "Rollback Test"
    loaded = wp_repo.get("ws-rollback-test")
    assert loaded is not None
    assert loaded["name"] == "Rollback Test"


def test_health_monitor_and_diagnostics(persistence_setup):
    setup = persistence_setup
    service = setup["service"]
    telemetry = setup["wp_telemetry"]
    stats = setup["wp_stats"]
    repos = setup["repos"]

    # Generate telemetry events
    telemetry.record_latency(15.0)
    telemetry.record_latency(20.0)
    telemetry.record_rollback()
    telemetry.record_failure("workspaces")

    t_data = telemetry.get_telemetry()
    assert t_data["transaction_rollbacks"] == 1
    assert t_data["average_query_latency_ms"] == 17.5
    assert t_data["p95_query_latency_ms"] == 20.0

    # Diagnostics scan
    diag = PersistenceDiagnostics(service.config, service)
    res = diag.run_diagnostics()
    assert res["status"] == "ok"

    # Report Generator
    report_gen = WorkspacePersistenceReportGenerator(
        "/tmp", setup["wp_service"], diag, telemetry, stats, repos
    )
    report_gen.generate_reports()

    assert os.path.exists("/tmp/docs/persistence/WORKSPACE_PERSISTENCE_STATUS.md")
    assert os.path.exists("/tmp/docs/persistence/WORKSPACE_HEALTH.md")
    assert os.path.exists("/tmp/docs/persistence/WORKSPACE_STATISTICS.md")
    assert os.path.exists("/tmp/docs/persistence/WORKSPACE_DIAGNOSTICS.md")
    assert os.path.exists("/tmp/docs/persistence/REPOSITORY_REGISTRY.md")
