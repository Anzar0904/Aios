import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class WorkflowNode:
    """Graph node representing an operation or decision element."""

    node_id: str
    name: str
    node_type: str  # "trigger", "action", "condition", "loop", "branch"
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEdge:
    """Directed graph edge representing execution transitions routes."""

    edge_id: str
    source_node_id: str
    target_node_id: str
    condition: Optional[str] = None


@dataclass
class WorkflowGraph:
    """Directed graph container organizing nodes and edge links."""

    nodes: List[WorkflowNode] = field(default_factory=list)
    edges: List[WorkflowEdge] = field(default_factory=list)


@dataclass
class WorkflowTrigger:
    """Trigger conditions prompting execution flow runs."""

    trigger_id: str
    trigger_type: str  # "webhook", "schedule", "event"
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowAction:
    """Concrete workflow action executing system operations."""

    action_id: str
    action_type: str  # "http_request", "script", "notify"
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowCondition:
    """Conditional evaluation expression."""

    condition_id: str
    expression: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowVariable:
    """Variable container declaring schema types and defaults."""

    name: str
    value_type: str  # "string", "int", "boolean", "object"
    default_value: Any = None


@dataclass
class WorkflowCredentialReference:
    """Credential metadata index referencing system vaults securely."""

    reference_id: str
    provider_type: str  # "github", "n8n", "temporal"
    credential_name: str


@dataclass
class WorkflowExecutionPolicy:
    """Configurable execution constraints matching runtime policies."""

    max_retries: int
    retry_delay_seconds: int
    timeout_seconds: int
    concurrency_limit: int


@dataclass
class WorkflowMetadata:
    """Metadata tag indicators detailing descriptions and dependencies."""

    tags: List[str] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    dependencies: List[str] = field(default_factory=list)


@dataclass
class WorkflowArtifact:
    """Output artifacts resulting from workflow execution loops."""

    artifact_id: str
    name: str
    file_path: str
    content_type: str


@dataclass
class WorkflowDefinition:
    """Unified container representing a platform-independent workflow graph."""

    workflow_id: str
    name: str
    graph: WorkflowGraph
    triggers: List[WorkflowTrigger] = field(default_factory=list)
    actions: List[WorkflowAction] = field(default_factory=list)
    conditions: List[WorkflowCondition] = field(default_factory=list)
    variables: List[WorkflowVariable] = field(default_factory=list)
    credentials: List[WorkflowCredentialReference] = field(default_factory=list)
    policy: Optional[WorkflowExecutionPolicy] = None
    metadata: Optional[WorkflowMetadata] = None


@dataclass
class AutomationSession:
    """Lifecycle tracking for an active execution flow session."""

    session_id: str
    workflow_id: str
    workspace_id: str
    status: str  # "pending", "running", "success", "failed"
    created_at: float
    closed_at: Optional[float] = None


@dataclass
class AutomationResult:
    """Consolidated outcome metrics from workflow executions."""

    session_id: str
    success: bool
    output_data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0


@dataclass
class AutomationReport:
    """Report compiled for external Knowledge Hub updates."""

    report_id: str
    workspace_id: str
    session_id: str
    workflow_name: str
    status: str
    error_summary: Optional[str] = None
    timestamp: float = 0.0


class AutomationProvider(abc.ABC):
    """Abstract interface for execution providers."""

    @property
    @abc.abstractmethod
    def provider_id(self) -> str:
        """Returns unique identifier for provider."""
        pass

    @abc.abstractmethod
    def validate_definition(self, definition: WorkflowDefinition) -> List[str]:
        """Validates if provider supports the workflow structures."""
        pass

    @abc.abstractmethod
    def execute_workflow(
        self, definition: WorkflowDefinition, session: AutomationSession
    ) -> AutomationResult:
        """Runs the workflow using provider execution engines."""
        pass


class N8NProvider(AutomationProvider, abc.ABC):
    """Abstract provider structure for n8n platform integration."""

    pass


class GitHubActionsProvider(AutomationProvider, abc.ABC):
    """Abstract provider structure for GitHub Actions integration."""

    pass


class TemporalProvider(AutomationProvider, abc.ABC):
    """Abstract provider structure for Temporal orchestrators integration."""

    pass


class AutomationProviderRegistry:
    """Container registry holding registered automation providers."""

    def __init__(self) -> None:
        self._providers: Dict[str, AutomationProvider] = {}

    def register(self, provider: AutomationProvider) -> None:
        self._providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> Optional[AutomationProvider]:
        return self._providers.get(provider_id)

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())


class AutomationRegistry(abc.ABC):
    """Workflow catalog manager saving platform-independent workflow definitions."""

    @abc.abstractmethod
    def register_workflow(self, definition: WorkflowDefinition) -> None:
        """Registers definition template."""
        pass

    @abc.abstractmethod
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Retrieves definition template by ID."""
        pass


class AutomationValidator(abc.ABC):
    """Enforces graph structures completeness, loop preventions, and credential checks."""

    @abc.abstractmethod
    def validate_workflow(self, definition: WorkflowDefinition) -> List[str]:
        """Validates graph connectivity and variables consistency."""
        pass


class AutomationManager(abc.ABC):
    """Orchestrates session creation and runner hand-offs."""

    @abc.abstractmethod
    def create_session(self, workflow_id: str, workspace_id: str) -> AutomationSession:
        """Instantiates session for run."""
        pass

    @abc.abstractmethod
    def execute_session(self, session: AutomationSession, provider_id: str) -> AutomationResult:
        """Delegates execution loop to targeted provider."""
        pass


class AutomationService(ServiceLifecycle, abc.ABC):
    """Conductor service managing runs, providers, history logs, and Notion reporting."""

    @abc.abstractmethod
    def register_provider(self, provider: AutomationProvider) -> None:
        """Registers third-party executor runner."""
        pass

    @abc.abstractmethod
    def run_automation(
        self, workflow_id: str, workspace_id: str, provider_id: str
    ) -> AutomationSession:
        """Submits task, validation checks, and triggers runner loops."""
        pass

    @abc.abstractmethod
    def get_session(self, session_id: str) -> Optional[AutomationSession]:
        """Retrieves current session tracking details."""
        pass

    @abc.abstractmethod
    def get_history(self, workspace_id: str) -> List[AutomationReport]:
        """Retrieves completed history logs for workspace."""
        pass

    @abc.abstractmethod
    def store_automation_summary(self, session_id: str) -> None:
        """Caches summary metrics in Memory. Never saves source code/credentials."""
        pass

    @abc.abstractmethod
    def publish_automation_report(self, report: AutomationReport) -> None:
        """Synchronizes report page to Notion."""
        pass
