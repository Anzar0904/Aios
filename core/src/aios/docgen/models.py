"""
docgen/models.py — Data models for the documentation generator.

All domain objects used by discoverers and renderers are defined here
to keep the rest of the system free of circular imports.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class GenerationStatus(str, Enum):
    """Overall outcome of a documentation generation run."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class ComponentKind(str, Enum):
    """Category of a discovered component."""

    SERVICE = "service"
    REPOSITORY = "repository"
    SKILL = "skill"
    PROVIDER = "provider"
    RUNTIME = "runtime"
    DB_MODEL = "db_model"
    DI_BINDING = "di_binding"


# ---------------------------------------------------------------------------
# Discovery models
# ---------------------------------------------------------------------------


@dataclass
class ServiceEntry:
    """Represents a discovered service interface and its concrete implementation."""

    name: str
    module: str
    file_path: str
    docstring: Optional[str]
    base_classes: List[str] = field(default_factory=list)
    implementation: Optional[str] = None
    impl_module: Optional[str] = None
    impl_file: Optional[str] = None
    methods: List[str] = field(default_factory=list)
    line_number: int = 0


@dataclass
class RepositoryEntry:
    """Represents a discovered repository class (abstract or concrete)."""

    name: str
    module: str
    file_path: str
    docstring: Optional[str]
    base_classes: List[str] = field(default_factory=list)
    entity: Optional[str] = None          # e.g. "Workspace" from WorkspaceRepository
    implementation: Optional[str] = None
    impl_file: Optional[str] = None
    methods: List[str] = field(default_factory=list)
    line_number: int = 0


@dataclass
class SkillEntry:
    """Represents a discovered skill loaded from skill.toml."""

    skill_id: str
    name: str
    version: str
    author: str
    description: str
    category: str
    commands: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    required_models: List[str] = field(default_factory=list)
    required_memory: List[str] = field(default_factory=list)
    prompt_directory: str = "prompts"
    toml_path: str = ""
    has_commands_py: bool = False


@dataclass
class ProviderEntry:
    """Represents a discovered AI provider."""

    name: str
    version: str
    status: str
    context_window: int
    cost_per_million_input: float
    cost_per_million_output: float
    auth_type: str
    is_local: bool
    supported_models: List[str] = field(default_factory=list)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1


@dataclass
class RuntimeComponentEntry:
    """Represents a discovered runtime component (concrete class registered in bootstrap)."""

    name: str
    module: str
    file_path: str
    docstring: Optional[str]
    interface: Optional[str] = None
    base_classes: List[str] = field(default_factory=list)
    line_number: int = 0


@dataclass
class DbModelEntry:
    """Represents a data model / dataclass / enum discovered in source code."""

    name: str
    module: str
    file_path: str
    docstring: Optional[str]
    kind: str = "dataclass"   # "dataclass" | "enum" | "class"
    fields: List[str] = field(default_factory=list)
    line_number: int = 0


@dataclass
class DIBinding:
    """A single DI registration: interface → concrete class."""

    interface: str
    concrete: str
    module: str
    line_number: int = 0


# ---------------------------------------------------------------------------
# Generation result
# ---------------------------------------------------------------------------


@dataclass
class GeneratedFile:
    """Metadata about one generated documentation file."""

    path: str
    title: str
    entry_count: int
    size_bytes: int = 0
    generated_at: float = field(default_factory=time.time)


@dataclass
class GenerationResult:
    """Summary of a complete documentation generation run."""

    status: GenerationStatus
    files: List[GeneratedFile] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    generated_at: float = field(default_factory=time.time)

    # Discovery counts (populated after discovery phase)
    services_count: int = 0
    repositories_count: int = 0
    skills_count: int = 0
    providers_count: int = 0
    runtime_count: int = 0
    db_models_count: int = 0
    di_bindings_count: int = 0

    @property
    def total_files(self) -> int:
        return len(self.files)

    @property
    def success(self) -> bool:
        return self.status == GenerationStatus.SUCCESS
