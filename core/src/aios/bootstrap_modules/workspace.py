"""
bootstrap_modules/workspace.py

Constructs and registers workspace repositories, workspace persistence,
and workspace intelligence services.
"""

from __future__ import annotations

import logging
import os

from aios.services.ai_workspace import AIWorkspaceService
from aios.services.ai_workspace_impl import LocalAIWorkspaceService
from aios.services.developer_workspace import DeveloperWorkspaceService
from aios.services.developer_workspace_impl import LocalDeveloperWorkspace
from aios.services.engineering_intelligence import EngineeringIntelligenceService
from aios.services.engineering_intelligence_impl import LocalEngineeringIntelligenceService

# Interface imports
from aios.services.persistence import (
    ConfigurationRepository,
    EngineeringProfileRepository,
    ProjectRepository,
    WorkspacePersistenceService,
    WorkspaceRepository,
    WorkspaceSessionRepository,
)

# Implementation imports
from aios.services.persistence_impl import (
    ConfigurationRepositoryImpl,
    EngineeringProfileRepositoryImpl,
    ProjectRepositoryImpl,
    WorkspaceRepositoryImpl,
    WorkspaceSessionRepositoryImpl,
)
from aios.services.persistence_impl import (
    WorkspacePersistenceReportGenerator as WPReportGenerator,
)
from aios.services.persistence_impl import (
    WorkspacePersistenceServiceImpl as WPServiceImpl,
)
from aios.services.persistence_impl import (
    WorkspacePersistenceStatistics as WPStats,
)
from aios.services.persistence_impl import (
    WorkspacePersistenceTelemetry as WPTelemetry,
)
from aios.services.persistence_impl import (
    WorkspacePersistenceValidator as WPValidator,
)
from aios.services.workspace_intelligence import (
    CodeIntelligenceService,
    WorkspaceIntelligenceService,
)
from aios.services.workspace_intelligence_impl import (
    LocalCodeIntelligenceService,
    LocalWorkspaceIntelligenceService,
)

logger = logging.getLogger(__name__)


def bootstrap_workspace_repos_and_persistence(registry, infra_ctx: dict) -> dict:  # noqa: ANN001
    """Constructs, initializes, and registers SQL workspace repositories and persistence service."""
    p_service = infra_ctx["p_service"]
    p_repos = infra_ctx["p_repos"]
    p_diagnostics = infra_ctx["p_diagnostics"]

    # Instantiate repositories
    workspace_repo = WorkspaceRepositoryImpl(p_service)
    session_repo = WorkspaceSessionRepositoryImpl(p_service)
    project_repo = ProjectRepositoryImpl(p_service)
    profile_repo = EngineeringProfileRepositoryImpl(p_service)
    config_repo = ConfigurationRepositoryImpl(p_service)

    # Register in RepositoryRegistry
    p_repos.register_repository("workspaces", workspace_repo)
    p_repos.register_repository("workspace_sessions", session_repo)
    p_repos.register_repository("projects", project_repo)
    p_repos.register_repository("engineering_profiles", profile_repo)
    p_repos.register_repository("configuration_profiles", config_repo)

    # Instantiate workspace persistence services
    wp_validator = WPValidator()
    wp_telemetry = WPTelemetry()
    wp_stats = WPStats(workspace_repo, session_repo)
    wp_service = WPServiceImpl(
        workspace_repo,
        session_repo,
        project_repo,
        profile_repo,
        config_repo,
        wp_validator,
        wp_telemetry,
        wp_stats,
    )
    wp_report = WPReportGenerator(
        os.getcwd(), wp_service, p_diagnostics, wp_telemetry, wp_stats, p_repos
    )

    # Initialize all workspace persistence services
    wp_validator.initialize()
    wp_telemetry.initialize()
    wp_stats.initialize()
    wp_service.initialize()
    wp_report.initialize()

    # Register in registry
    registry.register(WorkspaceRepository, workspace_repo)
    registry.register(WorkspaceSessionRepository, session_repo)
    registry.register(ProjectRepository, project_repo)
    registry.register(EngineeringProfileRepository, profile_repo)
    registry.register(ConfigurationRepository, config_repo)
    registry.register(WorkspacePersistenceService, wp_service)
    registry.register(WPReportGenerator, wp_report)

    return {
        "workspace_repo": workspace_repo,
        "session_repo": session_repo,
        "project_repo": project_repo,
        "profile_repo": profile_repo,
        "config_repo": config_repo,
        "wp_service": wp_service,
        "wp_report": wp_report,
    }


def bootstrap_workspace_intelligence_services(
    registry,  # noqa: ANN001
    project_intelligence,  # noqa: ANN001
    memory_service,  # noqa: ANN001
    knowledge_hub,  # noqa: ANN001
    model_service,  # noqa: ANN001
) -> dict:
    """Wires and registers higher-level workspace intelligence services."""
    developer_workspace = LocalDeveloperWorkspace()

    workspace_intel = LocalWorkspaceIntelligenceService(
        project_intel=project_intelligence,
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    workspace_intel.initialize()

    code_intel = LocalCodeIntelligenceService(
        project_intel=project_intelligence,
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    code_intel.initialize()

    eng_intel = LocalEngineeringIntelligenceService(
        code_intel=code_intel,
        workspace_intel=workspace_intel,
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    eng_intel.initialize()

    workspace_service = LocalAIWorkspaceService(
        memory_service=memory_service, knowledge_hub=knowledge_hub, registry=registry
    )
    workspace_service.initialize()

    registry.register(DeveloperWorkspaceService, developer_workspace)
    registry.register(WorkspaceIntelligenceService, workspace_intel)
    registry.register(CodeIntelligenceService, code_intel)
    registry.register(EngineeringIntelligenceService, eng_intel)
    registry.register(AIWorkspaceService, workspace_service)

    return {
        "developer_workspace": developer_workspace,
        "workspace_intel": workspace_intel,
        "code_intel": code_intel,
        "eng_intel": eng_intel,
        "workspace_service": workspace_service,
    }
