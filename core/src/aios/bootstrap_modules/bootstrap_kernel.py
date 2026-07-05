"""
bootstrap_modules/bootstrap_kernel.py

The main bootstrap entrypoint function for constructing the composition root.
"""

from __future__ import annotations

import logging
from pathlib import Path

from aios.bootstrap_modules.n8n_builder import build_n8n_platform
from aios.bootstrap_modules.persistence_builder import build_persistence_platform
from aios.bootstrap_modules.qdrant_builder import build_qdrant_platform
from aios.bootstrap_modules.redis_builder import build_redis_platform
from aios.bootstrap_modules.runtime_builder import build_runtime_services
from aios.bootstrap_modules.source_control_builder import build_source_control_platform
from aios.config import load_config
from aios.kernel import Kernel
from aios.registry import ServiceRegistry
from aios.services.event_bus_impl import LocalEventBus

logger = logging.getLogger(__name__)


def bootstrap_kernel(config_path: Path) -> Kernel:
    """
    Composition Root for Personal AI OS.
    Constructs, wires, and registers all concrete services.
    Returns a configured Kernel instance.
    """
    logger.info("Bootstrapping AI OS system (Composition Root)...")

    # 1. Initialize Registry & Config
    registry = ServiceRegistry()
    config = load_config(Path(config_path))

    # 2. Wire the Event Bus
    event_bus = LocalEventBus()

    # 3. Wire SQL Persistence & Runtime Intelligence Platform
    p_res = build_persistence_platform(registry, config_path)

    # 4. Wire Redis Platform
    r_res = build_redis_platform(registry, p_res["p_service"], p_res["ri_telem"])

    # 5. Wire Qdrant/Vector Memory Platform
    build_qdrant_platform(
        registry, config_path, p_res["p_repos"], p_res["ri_service"], r_res["redis_provider"]
    )

    # 6. Wire Runtime Services & Agents
    rt_res = build_runtime_services(registry, config_path, config, event_bus, p_res["profile_repo"])

    # 7. Wire Source Control Platform
    build_source_control_platform(registry, config)

    # 8. Wire self-hosted n8n components
    build_n8n_platform(registry, rt_res["n8n_integration_service"])

    # 9. Instantiate Kernel with the registry
    kernel = Kernel(config_path=config_path, registry=registry)
    rt_res["runtime_service"]._kernel = kernel

    return kernel
