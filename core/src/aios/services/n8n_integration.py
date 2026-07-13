import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class N8NServerInformation:
    """Carries version numbers, instance ID mappings and capability lists."""

    version: str
    instance_id: str
    capabilities: List[str] = field(default_factory=list)


@dataclass
class N8NConnectionProfile:
    """Connection profile containing target URL, auth types and timeouts."""

    url: str
    auth_type: str  # "api_key", "bearer_token"
    timeout_seconds: int = 30


@dataclass
class N8NIntegrationReport:
    """Report compiled for external Knowledge Hub Notion syncing."""

    report_id: str
    workspace_id: str
    server_version: str
    connectivity_status: str  # "online", "offline"
    latency_ms: float
    uploaded_workflows_count: int
    timestamp: float


class N8NAuthenticationProvider(abc.ABC):
    """Abstract authentication header generator."""

    @abc.abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """Returns auth header parameters."""
        pass


class APIKeyAuthenticationProvider(N8NAuthenticationProvider):
    """API Key authentications helper."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def get_auth_headers(self) -> Dict[str, str]:
        return {"X-N8N-API-KEY": self._api_key}


class BearerTokenAuthenticationProvider(N8NAuthenticationProvider):
    """Bearer Token authentications helper."""

    def __init__(self, token: str) -> None:
        self._token = token

    def get_auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}


class N8NConnectionManager:
    """Manages active connection headers."""

    def __init__(
        self, profile: N8NConnectionProfile, auth_provider: N8NAuthenticationProvider
    ) -> None:
        self.profile = profile
        self.auth_provider = auth_provider

    def get_headers(self) -> Dict[str, str]:
        return self.auth_provider.get_auth_headers()


class N8NClient(abc.ABC):
    """Abstract HTTP client executing API calls."""

    @abc.abstractmethod
    def upload_workflow(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        """Uploads workflow JSON."""
        pass

    @abc.abstractmethod
    def update_workflow(self, workflow_id: str, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        """Updates workflow JSON."""
        pass

    @abc.abstractmethod
    def delete_workflow(self, workflow_id: str) -> bool:
        """Deletes workflow."""
        pass

    @abc.abstractmethod
    def list_workflows(self) -> List[Dict[str, Any]]:
        """Lists uploaded workflows."""
        pass

    @abc.abstractmethod
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Retrieves workflow by ID."""
        pass

    @abc.abstractmethod
    def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Triggers execution."""
        pass

    @abc.abstractmethod
    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """Retrieves execution status logs."""
        pass

    @abc.abstractmethod
    def list_executions(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Lists executions logs."""
        pass

    @abc.abstractmethod
    def activate_workflow(self, workflow_id: str) -> bool:
        """Activates workflow triggers."""
        pass

    @abc.abstractmethod
    def deactivate_workflow(self, workflow_id: str) -> bool:
        """Deactivates workflow triggers."""
        pass


class N8NWorkflowRepository(abc.ABC):
    """Metadata repository saving mappings for local workflows."""

    @abc.abstractmethod
    def save_workflow_metadata(self, workflow_id: str, metadata: Dict[str, Any]) -> None:
        """Saves metadata map."""
        pass

    @abc.abstractmethod
    def get_workflow_metadata(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves metadata map."""
        pass


class N8NExecutionRepository(abc.ABC):
    """Metadata repository saving executions summaries."""

    @abc.abstractmethod
    def save_execution_metadata(self, execution_id: str, metadata: Dict[str, Any]) -> None:
        """Saves metadata map."""
        pass


class N8NCredentialRepository(abc.ABC):
    """Associates credential vault pointers."""

    @abc.abstractmethod
    def register_credential_reference(self, name: str, value: str) -> None:
        """Saves reference to credential lookup."""
        pass


class N8NHealthMonitor(abc.ABC):
    """Executes server status, version and connectivity latency checks."""

    @abc.abstractmethod
    def check_health(self) -> Dict[str, Any]:
        """Returns health diagnostics metrics."""
        pass


class N8NWorkspaceMapper(abc.ABC):
    """Maps workflows ownership to specific workspace sessions."""

    @abc.abstractmethod
    def map_workflow_to_workspace(self, workflow_id: str, workspace_id: str) -> None:
        """Registers workspace mapping."""
        pass

    @abc.abstractmethod
    def get_workspace_for_workflow(self, workflow_id: str) -> Optional[str]:
        """Retrieves mapping value."""
        pass


class N8NValidator(abc.ABC):
    """Validates configuration parameters and connection profile endpoints."""

    @abc.abstractmethod
    def validate_server_config(self, profile: N8NConnectionProfile) -> List[str]:
        """Validates configuration settings."""
        pass


class N8NIntegrationService(ServiceLifecycle, abc.ABC):
    """Central conductor interface managing health checks, workflows uploads, and executions."""

    @abc.abstractmethod
    def upload_workflow_json(self, workspace_id: str, workflow_json: Dict[str, Any]) -> str:
        """Uploads workflow JSON."""
        pass

    @abc.abstractmethod
    def trigger_workflow(self, workflow_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Executes active workflow."""
        pass

    @abc.abstractmethod
    def get_health_status(self) -> N8NIntegrationReport:
        """Returns current integration diagnostics report."""
        pass

    @abc.abstractmethod
    def get_history(self, workspace_id: str) -> List[N8NIntegrationReport]:
        """Retrieves history runs reports."""
        pass

    @abc.abstractmethod
    def store_integration_summary(self, report_id: str) -> None:
        """Saves metadata statistics inside memory. Never stores source code/credentials."""
        pass

    @abc.abstractmethod
    def publish_integration_report(self, report: N8NIntegrationReport) -> None:
        """Synchronizes report page details to Notion on-demand."""
        pass
