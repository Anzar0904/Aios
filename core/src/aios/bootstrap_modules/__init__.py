"""
bootstrap_modules

Focused bootstrap modules for Personal AI OS.
"""

from __future__ import annotations

from .agents import bootstrap_agents as bootstrap_agents
from .cli import bootstrap_cli as bootstrap_cli
from .events import bootstrap_events as bootstrap_events
from .infrastructure import bootstrap_infrastructure as bootstrap_infrastructure
from .kernel import bootstrap_kernel_instance as bootstrap_kernel_instance
from .memory import bootstrap_memory as bootstrap_memory
from .providers import bootstrap_providers as bootstrap_providers
from .services import bootstrap_services as bootstrap_services
from .workspace import (
    bootstrap_workspace_intelligence_services as bootstrap_workspace_intelligence_services,
)
from .workspace import (
    bootstrap_workspace_repos_and_persistence as bootstrap_workspace_repos_and_persistence,
)
