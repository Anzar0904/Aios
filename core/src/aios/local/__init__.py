"""
aios/local/__init__.py

Phase 1: Local Model Intelligence Layer.
Provides Ollama discovery, capability registry, intelligent routing,
dynamic loading, health monitoring, benchmark engine, and memory integration.
"""

from aios.local.capability_registry import (
    LocalCapabilityRegistry,
    ModelCapability,
    ModelRole,
    local_capability_registry,
)
from aios.local.discovery import OllamaDiscovery, OllamaModelMetadata
from aios.local.health_monitor import LocalHealthMonitor, ModelHealthStatus
from aios.local.loader import LocalModelLoader, ModelLoadResult
from aios.local.memory_integration import LocalExecutionRecord, LocalMemoryIntegration
from aios.local.router import LocalModelRouter, RoutingResult

__all__ = [
    "OllamaDiscovery",
    "OllamaModelMetadata",
    "LocalCapabilityRegistry",
    "ModelCapability",
    "ModelRole",
    "local_capability_registry",
    "LocalModelRouter",
    "RoutingResult",
    "LocalModelLoader",
    "ModelLoadResult",
    "LocalHealthMonitor",
    "ModelHealthStatus",
    "LocalExecutionRecord",
    "LocalMemoryIntegration",
]
