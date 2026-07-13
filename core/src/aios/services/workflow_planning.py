import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.automation import WorkflowDefinition, WorkflowEdge, WorkflowNode
from aios.services.base import ServiceLifecycle


@dataclass
class WorkflowTemplate:
    """Parameterized workflow template ready for composition instantiation."""

    template_id: str
    name: str
    description: str
    default_nodes: List[WorkflowNode] = field(default_factory=list)
    default_edges: List[WorkflowEdge] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowConstraint:
    """Pre-conditions or post-conditions validation gating rule."""

    constraint_id: str
    name: str
    expression: str
    severity: str  # "info", "warning", "error"


@dataclass
class WorkflowPlanningSession:
    """Lifecycle tracking for an active workflow planning session."""

    session_id: str
    workspace_id: str
    intent: str
    status: str  # "open", "closed"
    created_at: float
    closed_at: Optional[float] = None


@dataclass
class WorkflowPlanningReport:
    """Report compiled for external Knowledge Hub Notion syncing."""

    report_id: str
    session_id: str
    workspace_id: str
    raw_intent: str
    resolved_dependencies: List[str] = field(default_factory=list)
    optimization_recommendations: List[str] = field(default_factory=list)
    suggested_templates: List[str] = field(default_factory=list)
    planned_workflow_id: str = ""
    timestamp: float = 0.0


class WorkflowIntentAnalyzer(abc.ABC):
    """Analyzes intent texts to detect targets, tags, and matching templates."""

    @abc.abstractmethod
    def analyze_intent(self, intent: str) -> Dict[str, Any]:
        """Parses raw text into structural properties dict."""
        pass


class WorkflowTemplateRegistry:
    """Registry holding reusable and parameterized workflow templates."""

    def __init__(self) -> None:
        self._templates: Dict[str, WorkflowTemplate] = {}

    def register_template(self, template: WorkflowTemplate) -> None:
        """Saves template in registry."""
        self._templates[template.template_id] = template

    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Retrieves template by ID."""
        return self._templates.get(template_id)

    def list_templates(self) -> List[str]:
        """Lists registered template IDs."""
        return list(self._templates.keys())


class WorkflowDependencyResolver(abc.ABC):
    """Orders nodes to satisfy execution dependency bounds."""

    @abc.abstractmethod
    def resolve_dependencies(
        self, nodes: List[WorkflowNode], edges: List[WorkflowEdge]
    ) -> List[str]:
        """Returns ordered node IDs conforming to DAG execution routes."""
        pass


class WorkflowOptimizer(abc.ABC):
    """Performs planning-time graph structural optimizations."""

    @abc.abstractmethod
    def optimize_graph(
        self, nodes: List[WorkflowNode], edges: List[WorkflowEdge]
    ) -> tuple[List[WorkflowNode], List[WorkflowEdge], List[str]]:
        """Returns (optimized_nodes, optimized_edges, optimizations_done)."""
        pass


class WorkflowSuggestionEngine(abc.ABC):
    """Suggests relevant template IDs matching analyzed intents."""

    @abc.abstractmethod
    def suggest_templates(self, intent: str, registry: WorkflowTemplateRegistry) -> List[str]:
        """Returns matched template IDs."""
        pass


class WorkflowComposer(abc.ABC):
    """Hydrates templates parameters to compose concrete WorkflowDefinitions."""

    @abc.abstractmethod
    def compose_workflow(
        self, template: WorkflowTemplate, params: Dict[str, Any]
    ) -> WorkflowDefinition:
        """Returns parameterized workflow definition."""
        pass


class WorkflowPlanner(ServiceLifecycle, abc.ABC):
    """Conductor service managing planning sessions, optimizations, registry, and reporting."""

    @abc.abstractmethod
    def create_planning_session(self, workspace_id: str, intent: str) -> WorkflowPlanningSession:
        """Creates session to initiate plan."""
        pass

    @abc.abstractmethod
    def generate_plan(self, session: WorkflowPlanningSession) -> WorkflowPlanningReport:
        """Processes intent, resolves graphs, optimizes structure, and logs report."""
        pass

    @abc.abstractmethod
    def get_session(self, session_id: str) -> Optional[WorkflowPlanningSession]:
        """Retrieves session details."""
        pass

    @abc.abstractmethod
    def get_history(self, workspace_id: str) -> List[WorkflowPlanningReport]:
        """Retrieves past plans for workspace."""
        pass

    @abc.abstractmethod
    def store_planning_summary(self, session_id: str) -> None:
        """Caches stats in Memory. Never saves source code/credentials."""
        pass

    @abc.abstractmethod
    def publish_planning_report(self, report: WorkflowPlanningReport) -> None:
        """Pushes report metadata to Notion."""
        pass
