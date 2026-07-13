import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class InternalNode:
    id: str
    name: str
    type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    position: List[int] = field(default_factory=lambda: [0, 0])


@dataclass
class InternalConnection:
    from_node: str
    to_node: str
    from_output: int = 0
    to_input: int = 0


@dataclass
class InternalWorkflow:
    id: Optional[str]
    name: str
    nodes: List[InternalNode] = field(default_factory=list)
    connections: List[InternalConnection] = field(default_factory=list)
    active: bool = True
    version: int = 1


@dataclass
class ExecutionMetrics:
    workflow_id: str
    status: str  # success, failed, running
    success_rate: float
    total_runs: int
    failures: int
    last_run: float = 0.0
    next_run: Optional[float] = None
    logs: List[str] = field(default_factory=list)


@dataclass
class ConnectionHealth:
    online: bool
    api_version: str
    latency_ms: float
    error_message: Optional[str] = None


class N8NService(ServiceLifecycle, abc.ABC):
    @abc.abstractmethod
    def create_workflow(self, workflow: InternalWorkflow) -> InternalWorkflow:
        """Saves/deploys the internal workflow representation."""
        pass

    @abc.abstractmethod
    def update_workflow(self, workflow_id: str, workflow: InternalWorkflow) -> InternalWorkflow:
        """Updates an existing workflow."""
        pass

    @abc.abstractmethod
    def delete_workflow(self, workflow_id: str) -> bool:
        """Deletes an existing workflow by its identifier."""
        pass

    @abc.abstractmethod
    def get_workflow(self, workflow_id: str) -> Optional[InternalWorkflow]:
        """Retrieves a workflow by its identifier."""
        pass

    @abc.abstractmethod
    def list_workflows(self) -> List[InternalWorkflow]:
        """Lists all deployed workflows."""
        pass

    @abc.abstractmethod
    def validate_workflow(self, workflow: InternalWorkflow) -> Dict[str, Any]:
        """Runs graph diagnostics: detects loops, unreachable nodes, missing credentials."""
        pass

    @abc.abstractmethod
    def generate_workflow_from_natural_language(self, description: str) -> InternalWorkflow:
        """Uses ModelService to plan and construct a valid InternalWorkflow from plain text."""
        pass

    @abc.abstractmethod
    def execute_workflow(self, workflow_id: str) -> bool:
        """Starts/triggers execution of a workflow."""
        pass

    @abc.abstractmethod
    def stop_workflow(self, workflow_id: str) -> bool:
        """Halts running execution of a workflow."""
        pass

    @abc.abstractmethod
    def get_execution_metrics(self, workflow_id: str) -> Optional[ExecutionMetrics]:
        """Retrieves running metrics and log streams."""
        pass

    @abc.abstractmethod
    def check_health(self) -> ConnectionHealth:
        """Checks API connectivity to the local/remote n8n engine."""
        pass
