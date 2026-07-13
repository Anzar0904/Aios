import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class ArchitectureComponent:
    """A distinct structural part of the system (e.g. Service, Controller)."""

    __test__ = False
    name: str
    component_type: str
    description: str


@dataclass
class ArchitectureLayer:
    """An architectural division containing components (e.g., Kernel Layer)."""

    __test__ = False
    name: str
    level: int
    components: List[ArchitectureComponent] = field(default_factory=list)


@dataclass
class ArchitectureRelationship:
    """System dependency coupling between two components."""

    __test__ = False
    source_component: str
    target_component: str
    relationship_type: str


@dataclass
class ArchitectureDiagram:
    """Mermaid diagram output code string."""

    __test__ = False
    diagram_id: str
    diagram_type: str
    content: str


@dataclass
class ArchitectureDecision:
    """An Architecture Decision Record (ADR) reference."""

    __test__ = False
    decision_id: str
    title: str
    status: str
    context: str


@dataclass
class ArchitectureSummary:
    """Summary metrics of components and active layers counts."""

    __test__ = False
    summary_id: str
    layers_count: int
    components_count: int
    relationships_count: int
    timestamp: float


@dataclass
class ArchitectureReport:
    """Architecture health audit detailing layers violations or unused parts."""

    __test__ = False
    report_id: str
    workspace_id: str
    violations: List[str]
    circular_dependencies: List[str]
    unused_services: List[str]
    timestamp: float


class ArchitectureAnalyzer(abc.ABC):
    """Compares codebase layouts to find circular dependencies or structural violations."""

    __test__ = False

    @abc.abstractmethod
    def analyze_architecture(
        self, code_structure: Dict[str, Any], existing_docs: str
    ) -> ArchitectureReport:
        """Finds violations and logs metrics."""
        pass


class ArchitectureDocumentPlanner(abc.ABC):
    """Plans structure layout matching formatting rules."""

    __test__ = False

    @abc.abstractmethod
    def plan_architecture_documentation(
        self, report: ArchitectureReport
    ) -> List[ArchitectureComponent]:
        """Assembles list of components requiring documentation."""
        pass


class ArchitectureValidator(abc.ABC):
    """Checks Mermaid diagram consistency or broken references."""

    __test__ = False

    @abc.abstractmethod
    def validate_architecture_document(
        self, diagram: ArchitectureDiagram, registry: "ArchitectureRegistry"
    ) -> List[str]:
        """Returns validation errors list."""
        pass


class ArchitectureRegistry:
    """Thread-safe index cataloging components and decisions."""

    __test__ = False

    def __init__(self) -> None:
        self._components: Dict[str, ArchitectureComponent] = {}
        self._layers: Dict[str, ArchitectureLayer] = {}
        self._relationships: List[ArchitectureRelationship] = []
        self._decisions: Dict[str, ArchitectureDecision] = {}

    def register_component(self, component: ArchitectureComponent) -> None:
        self._components[component.name] = component

    def get_component(self, name: str) -> Optional[ArchitectureComponent]:
        return self._components.get(name)

    def register_layer(self, layer: ArchitectureLayer) -> None:
        self._layers[layer.name] = layer

    def get_layer(self, name: str) -> Optional[ArchitectureLayer]:
        return self._layers.get(name)

    def add_relationship(self, rel: ArchitectureRelationship) -> None:
        self._relationships.append(rel)

    def list_relationships(self) -> List[ArchitectureRelationship]:
        return self._relationships

    def register_decision(self, decision: ArchitectureDecision) -> None:
        self._decisions[decision.decision_id] = decision

    def get_decision(self, decision_id: str) -> Optional[ArchitectureDecision]:
        return self._decisions.get(decision_id)


class ArchitectureDocumentationService(ServiceLifecycle, abc.ABC):
    """Coordinating service generating architecture structures, diagram layouts, and memory logs."""

    __test__ = False

    @abc.abstractmethod
    def generate_architecture_documentation(
        self, workspace_id: str, code_structure: Dict[str, Any], existing_docs: str
    ) -> ArchitectureDiagram:
        """Assembles Mermaid diagram layouts."""
        pass

    @abc.abstractmethod
    def store_architecture_summary(self, summary: ArchitectureSummary) -> None:
        """Logs summaries records in Memory."""
        pass

    @abc.abstractmethod
    def publish_architecture_report(self, report: ArchitectureReport) -> None:
        """Pushes reports updates to Knowledge Hub."""
        pass
