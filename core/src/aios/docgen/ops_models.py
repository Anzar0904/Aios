"""
ops_models.py — Data models for operations guide generation.

Domain models for deployment, configuration, and operational documentation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ServiceDeployment:
    """Represents deployment requirements for a service."""

    name: str
    type: str  # internal, external (PostgreSQL, Redis, Qdrant)
    port: Optional[int] = None
    required: bool = True
    config_keys: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ConfigurationItem:
    """Represents a configuration parameter."""

    key: str
    description: str
    default: Optional[str] = None
    required: bool = True
    env_var: Optional[str] = None
    example: Optional[str] = None
    section: str = "core"  # core, postgres, redis, qdrant, n8n, omniroute


@dataclass
class StartupStep:
    """Represents a step in the startup sequence."""

    order: int
    service: str
    command: str
    description: str
    wait_for: List[str] = field(default_factory=list)
    healthcheck: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class OmniRouteProvider:
    """Represents an OmniRoute AI provider."""

    name: str
    env_key: str
    base_url: str
    default_model: str
    description: str
    required: bool = False


@dataclass
class BackupTarget:
    """Represents a backup target."""

    name: str
    type: str  # database, files, configuration
    location: str
    frequency: str  # daily, weekly, on-demand
    retention: str
    tool: str = ""
    notes: str = ""


@dataclass
class MonitoringMetric:
    """Represents a monitoring metric."""

    name: str
    description: str
    source: str  # service, database, system
    alert_threshold: Optional[str] = None


@dataclass
class TroubleshootingEntry:
    """Represents a troubleshooting scenario."""

    symptom: str
    cause: str
    solution: str
    related_logs: List[str] = field(default_factory=list)
    cross_refs: List[str] = field(default_factory=list)


@dataclass
class OperationsGenerationResult:
    """Result of operations guide generation."""

    status: str = "pending"  # pending, success, partial, failed
    elapsed: float = 0.0
    guides_generated: int = 0
    files_written: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
