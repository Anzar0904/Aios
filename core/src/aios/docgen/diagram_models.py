"""
diagram_models.py — Data models for architecture diagram generation.

Domain models for extracting and representing architectural information
that will be rendered as Mermaid diagrams.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ServiceNode:
    """Represents a service node in the dependency graph."""

    name: str
    module: str
    dependencies: List[str] = field(default_factory=list)
    is_interface: bool = False
    implementation: Optional[str] = None


@dataclass
class DIBinding:
    """Represents a dependency injection binding."""

    interface: str
    concrete: str
    module: str
    lifecycle: str = "singleton"  # singleton, transient, scoped


@dataclass
class BootstrapStep:
    """Represents a step in the bootstrap sequence."""

    order: int
    name: str
    description: str
    initializes: List[str] = field(default_factory=list)


@dataclass
class LifecyclePhase:
    """Represents a lifecycle phase."""

    name: str  # initialization, runtime, cleanup
    services: List[str] = field(default_factory=list)
    order: int = 0


@dataclass
class PersistenceLayer:
    """Represents a persistence layer (SQLite, PostgreSQL, Redis, Qdrant)."""

    name: str
    type: str  # sql, nosql, vector
    repositories: List[str] = field(default_factory=list)
    purpose: str = ""


@dataclass
class ArchitecturalComponent:
    """Represents a high-level architectural component."""

    name: str
    type: str  # kernel, service, engine, store, interface
    description: str
    dependencies: List[str] = field(default_factory=list)
    subcomponents: List[str] = field(default_factory=list)


@dataclass
class DiagramGenerationResult:
    """Result of diagram generation run."""

    status: str = "pending"  # pending, success, partial, failed
    elapsed: float = 0.0
    diagrams_generated: int = 0
    files_written: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
