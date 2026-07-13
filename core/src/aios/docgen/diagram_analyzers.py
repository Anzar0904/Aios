"""
diagram_analyzers.py — Analyzers for extracting architectural information.

Static analyzers that extract service dependencies, DI bindings, bootstrap sequence,
lifecycle phases, and other architectural information from source code.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Optional

from aios.docgen.diagram_models import (
    ArchitecturalComponent,
    BootstrapStep,
    LifecyclePhase,
    PersistenceLayer,
    ServiceNode,
)
from aios.docgen.discoverers import (
    ServiceDiscoverer,
    _parse_module,
    _python_files,
)


class ServiceDependencyAnalyzer:
    """Analyzes service dependencies for dependency graph generation."""

    def __init__(self, services_root: Path, src_root: Path):
        self._services_root = services_root
        self._src_root = src_root

    def analyze(self) -> List[ServiceNode]:
        """Extract service nodes with their dependencies."""
        # Use existing ServiceDiscoverer to get basic service info
        discoverer = ServiceDiscoverer(self._services_root, self._src_root)
        services = discoverer.discover()

        nodes = []
        for service in services:
            # Extract dependencies from constructor parameters
            dependencies = self._extract_dependencies(service.file_path)

            node = ServiceNode(
                name=service.name,
                module=service.module,
                dependencies=dependencies,
                is_interface=service.implementation is None,
                implementation=service.implementation,
            )
            nodes.append(node)

        return nodes

    def _extract_dependencies(self, file_path: str) -> List[str]:
        """Extract service dependencies from __init__ parameters."""
        module = _parse_module(Path(file_path))
        if module is None:
            return []

        dependencies = []
        for node in ast.walk(module):
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                for arg in node.args.args:
                    if arg.arg in ("self", "cls"):
                        continue
                    # Extract service names from type annotations
                    if arg.annotation:
                        dep_type = self._extract_type_name(arg.annotation)
                        if dep_type and (
                            dep_type.endswith("Service")
                            or dep_type.endswith("Engine")
                            or dep_type.endswith("Registry")
                            or dep_type.endswith("Manager")
                        ):
                            dependencies.append(dep_type)

        return dependencies

    @staticmethod
    def _extract_type_name(annotation: ast.expr) -> Optional[str]:
        """Extract type name from annotation."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return annotation.attr
        elif isinstance(annotation, ast.Subscript):
            # Handle Optional[ServiceType]
            return ServiceDependencyAnalyzer._extract_type_name(annotation.value)
        return None


class BootstrapSequenceAnalyzer:
    """Analyzes bootstrap sequence from bootstrap.py."""

    def __init__(self, bootstrap_file: Path):
        self._bootstrap_file = bootstrap_file

    def analyze(self) -> List[BootstrapStep]:
        """Extract bootstrap initialization sequence."""
        if not self._bootstrap_file.exists():
            return []

        module = _parse_module(self._bootstrap_file)
        if module is None:
            return []

        steps = []
        order = 0

        # Look for initialization calls in bootstrap functions
        for node in ast.walk(module):
            if isinstance(node, ast.FunctionDef):
                if "bootstrap" in node.name.lower() or "initialize" in node.name.lower():
                    steps.extend(self._extract_init_calls(node, order))
                    order += 1

        return sorted(steps, key=lambda s: s.order)

    def _extract_init_calls(
        self, func_node: ast.FunctionDef, base_order: int
    ) -> List[BootstrapStep]:
        """Extract initialization calls from a function."""
        steps = []
        order = base_order * 100  # Leave room for sub-steps

        for i, stmt in enumerate(func_node.body):
            if isinstance(stmt, ast.Assign):
                # Look for service instantiations
                if isinstance(stmt.value, ast.Call):
                    service_name = self._get_call_name(stmt.value)
                    if service_name:
                        step = BootstrapStep(
                            order=order + i,
                            name=f"Initialize {service_name}",
                            description=f"Create and configure {service_name} instance",
                            initializes=[service_name],
                        )
                        steps.append(step)

        return steps

    @staticmethod
    def _get_call_name(call_node: ast.Call) -> Optional[str]:
        """Extract the name from a call node."""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return None


class LifecycleAnalyzer:
    """Analyzes service lifecycle phases."""

    LIFECYCLE_METHODS = {
        "__init__": ("initialization", 0),
        "init_service": ("initialization", 1),
        "initialize": ("initialization", 1),
        "start": ("runtime", 2),
        "run": ("runtime", 3),
        "cleanup": ("cleanup", 4),
        "shutdown": ("cleanup", 4),
        "stop": ("cleanup", 4),
    }

    def __init__(self, services_root: Path, src_root: Path):
        self._services_root = services_root
        self._src_root = src_root

    def analyze(self) -> List[LifecyclePhase]:
        """Extract lifecycle phases with services."""
        phases_map = {
            "initialization": LifecyclePhase(name="initialization", order=0),
            "runtime": LifecyclePhase(name="runtime", order=1),
            "cleanup": LifecyclePhase(name="cleanup", order=2),
        }

        # Analyze services for lifecycle methods
        for py_file in _python_files(self._services_root):
            module = _parse_module(py_file)
            if module is None:
                continue

            for node in ast.walk(module):
                if isinstance(node, ast.ClassDef):
                    service_name = node.name
                    if not any(service_name.endswith(s) for s in ["Service", "Engine", "Manager"]):
                        continue

                    # Check which lifecycle methods this service has
                    for method_node in node.body:
                        if isinstance(method_node, ast.FunctionDef):
                            method_name = method_node.name
                            if method_name in self.LIFECYCLE_METHODS:
                                phase_name, _ = self.LIFECYCLE_METHODS[method_name]
                                if service_name not in phases_map[phase_name].services:
                                    phases_map[phase_name].services.append(service_name)

        return sorted(phases_map.values(), key=lambda p: p.order)


class PersistenceAnalyzer:
    """Analyzes persistence architecture."""

    def analyze(self, project_root: Path) -> List[PersistenceLayer]:
        """Extract persistence layers."""
        layers = [
            PersistenceLayer(
                name="SQLite",
                type="sql",
                purpose="Local development and lightweight persistence",
                repositories=[],
            ),
            PersistenceLayer(
                name="PostgreSQL",
                type="sql",
                purpose="Production relational data storage",
                repositories=[],
            ),
            PersistenceLayer(
                name="Redis",
                type="nosql",
                purpose="Caching and ephemeral data",
                repositories=[],
            ),
            PersistenceLayer(
                name="Qdrant",
                type="vector",
                purpose="Semantic memory and vector search",
                repositories=[],
            ),
        ]

        # Scan for repository implementations
        repo_root = project_root / "core" / "src" / "aios" / "services"
        if repo_root.exists():
            for py_file in _python_files(repo_root):
                if "repository" in py_file.stem.lower() or "repo" in py_file.stem.lower():
                    content = py_file.read_text()
                    repo_names = self._extract_repository_names(content)

                    # Assign to appropriate layer based on implementation
                    for repo_name in repo_names:
                        if "sqlite" in content.lower() or "sql" in content.lower():
                            layers[0].repositories.append(repo_name)
                            layers[1].repositories.append(repo_name)
                        if "redis" in content.lower():
                            layers[2].repositories.append(repo_name)
                        if "qdrant" in content.lower() or "vector" in content.lower():
                            layers[3].repositories.append(repo_name)

        return layers

    @staticmethod
    def _extract_repository_names(content: str) -> List[str]:
        """Extract repository class names from file content."""
        repos = []
        for line in content.split("\n"):
            if "class " in line and "Repository" in line:
                parts = line.split("class ")[1].split("(")[0].split(":")[0].strip()
                if parts:
                    repos.append(parts)
        return repos


class ArchitectureComponentAnalyzer:
    """Analyzes high-level architectural components."""

    def analyze(self) -> List[ArchitecturalComponent]:
        """Extract high-level architectural components."""
        return [
            ArchitecturalComponent(
                name="CLI",
                type="interface",
                description="Command-line interface and REPL",
                dependencies=["Kernel"],
                subcomponents=["CommandRegistry", "InputParser"],
            ),
            ArchitecturalComponent(
                name="Kernel",
                type="kernel",
                description="Core orchestration engine",
                dependencies=["Brain", "EventBus", "ServiceRegistry"],
                subcomponents=["LifecycleManager", "ServiceCoordinator"],
            ),
            ArchitecturalComponent(
                name="Brain",
                type="engine",
                description="AI reasoning and context assembly",
                dependencies=["ModelService", "MemoryService", "ContextService"],
                subcomponents=["OmniRoute", "PromptBuilder", "ContextAssembler"],
            ),
            ArchitecturalComponent(
                name="EventBus",
                type="service",
                description="Event coordination and pub/sub",
                dependencies=[],
                subcomponents=["EventQueue", "SubscriptionManager"],
            ),
            ArchitecturalComponent(
                name="ServiceRegistry",
                type="service",
                description="Dependency injection container",
                dependencies=[],
                subcomponents=["DIContainer", "ServiceFactory"],
            ),
            ArchitecturalComponent(
                name="MemoryService",
                type="service",
                description="Semantic memory and retrieval",
                dependencies=["PersistenceService"],
                subcomponents=["VectorStore", "EmbeddingCache", "ConversationHistory"],
            ),
            ArchitecturalComponent(
                name="PersistenceService",
                type="service",
                description="Data storage abstraction",
                dependencies=[],
                subcomponents=["RepositoryFactory", "ConnectionPool", "MigrationManager"],
            ),
        ]
