"""
aios/bootstrap.py

Thin Composition Root orchestrator for Personal AI OS.
"""

from __future__ import annotations

import logging
from pathlib import Path

from aios.bootstrap_modules import (
    bootstrap_agents,
    bootstrap_cli,
    bootstrap_events,
    bootstrap_infrastructure,
    bootstrap_kernel_instance,
    bootstrap_memory,
    bootstrap_services,
    bootstrap_workspace_intelligence_services,
    bootstrap_workspace_repos_and_persistence,
)
from aios.config import load_config
from aios.kernel import Kernel
from aios.registry import ServiceRegistry

logger = logging.getLogger(__name__)


def bootstrap_kernel(config_path: Path) -> Kernel:
    """
    Composition Root for Personal AI OS.
    Constructs, wires, and registers all concrete services.
    Returns a configured Kernel instance.
    """
    logger.info("Bootstrapping AI OS system (Composition Root)...")

    # 1. Initialize Service Registry and Load Configuration
    registry = ServiceRegistry()
    config = load_config(Path(config_path))

    # 2. Events (Event bus setup)
    event_bus = bootstrap_events(registry)

    # 3. Infrastructure (SQL connection, Redis connection, Qdrant connection)
    infra_ctx = bootstrap_infrastructure(registry, config_path)

    # 4. Workspace database repositories and WorkspacePersistenceService
    workspace_repo_ctx = bootstrap_workspace_repos_and_persistence(registry, infra_ctx)

    # 5. Memory (SQL memory databases, Vector memory, Embeddings, Hybrid retrieval)
    memory_ctx = bootstrap_memory(registry, config_path, infra_ctx, event_bus)

    # 6. CLI (Command Registry)
    command_registry = bootstrap_cli(registry)

    # 7. Services (Core, testing, documentation, approval/review, automation, n8n)
    services_ctx = bootstrap_services(
        registry,
        config_path,
        config,
        event_bus,
        infra_ctx,
        workspace_repo_ctx,
        memory_ctx,
        command_registry,
    )

    # 8. Workspace Intelligence Services
    workspace_intel_ctx = bootstrap_workspace_intelligence_services(
        registry,
        services_ctx["project_intelligence"],
        memory_ctx["memory_service"],
        services_ctx["knowledge_hub"],
        services_ctx["model_service"],
    )

    # Link the newly created developer workspace to github_service
    services_ctx["github_service"].dev_workspace = workspace_intel_ctx["developer_workspace"]

    # 9. Agents (Agent runtime, registry, manager, career/dev/mock agents, mission engine)
    bootstrap_agents(
        registry=registry,
        event_bus=event_bus,
        memory_service=memory_ctx["memory_service"],
        context_service=services_ctx["context_service"],
        tool_service=services_ctx["tool_service"],
        model_service=services_ctx["model_service"],
        github_service=services_ctx["github_service"],
        career_os=services_ctx["career_os"],
        daily_os=services_ctx["daily_os"],
        orchestrator_service=services_ctx["orchestrator_service"],
    )

    # 10. Instantiate Kernel with the registry and link runtime_service
    kernel = bootstrap_kernel_instance(config_path, registry, services_ctx["runtime_service"])

    return kernel
