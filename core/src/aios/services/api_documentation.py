import abc
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from aios.services.base import ServiceLifecycle


@dataclass
class APIParameter:
    """A query or path parameter detail."""
    __test__ = False
    name: str
    param_type: str
    required: bool
    description: str


@dataclass
class APISchema:
    """Data object definition for requests and responses."""
    __test__ = False
    schema_name: str
    fields: Dict[str, str]
    description: str


@dataclass
class APIExample:
    """Mock example request and response payload JSONs."""
    __test__ = False
    example_id: str
    request_body: str
    response_body: str


@dataclass
class APIResponse:
    """An HTTP response specification."""
    __test__ = False
    status_code: int
    schema: Optional[APISchema]
    description: str
    examples: List[APIExample] = field(default_factory=list)


@dataclass
class APIEndpoint:
    """A single REST/GraphQL/RPC API endpoint."""
    __test__ = False
    path: str
    method: str
    summary: str
    parameters: List[APIParameter] = field(default_factory=list)
    request_body_schema: Optional[APISchema] = None
    responses: List[APIResponse] = field(default_factory=list)
    deprecated: bool = False


@dataclass
class APIDocumentArtifact:
    """Constructed API documentation output."""
    __test__ = False
    artifact_id: str
    workspace_id: str
    content: str
    endpoints: List[APIEndpoint]
    timestamp: float


@dataclass
class APIReport:
    """Discrepancy report detailing gaps in current API docs."""
    __test__ = False
    report_id: str
    workspace_id: str
    undocumented_endpoints: List[str]
    missing_parameters: List[str]
    outdated_schemas: List[str]
    missing_examples: List[str]
    recommendations: List[str]
    timestamp: float


class APIAnalyzer(abc.ABC):
    """Parses AST structures to discover endpoints and compare current documentation."""
    __test__ = False

    @abc.abstractmethod
    def analyze_api(self, code_structure: Dict[str, Any], existing_docs: str) -> APIReport:
        """Flags missing parameters or outdated schemas."""
        pass


class APIDocumentationPlanner(abc.ABC):
    """Plans layout structure matching target formatting style rules."""
    __test__ = False

    @abc.abstractmethod
    def plan_api_documentation(self, report: APIReport) -> List[APIEndpoint]:
        """Assembles list of endpoints requiring documentation additions."""
        pass


class APIDocumentValidator(abc.ABC):
    """Validates markdown formatting and OpenAPI compatibility of generated specs."""
    __test__ = False

    @abc.abstractmethod
    def validate_api_document(self, artifact: APIDocumentArtifact) -> List[str]:
        """Returns validation error list."""
        pass


class APIRegistry:
    """Thread-safe registry caching discovered endpoint specifications."""
    __test__ = False

    def __init__(self) -> None:
        self._endpoints: Dict[str, APIEndpoint] = {}
        self._schemas: Dict[str, APISchema] = {}

    def register_endpoint(self, endpoint: APIEndpoint) -> None:
        key = f"{endpoint.method}:{endpoint.path}"
        self._endpoints[key] = endpoint

    def get_endpoint(self, method: str, path: str) -> Optional[APIEndpoint]:
        return self._endpoints.get(f"{method}:{path}")

    def list_endpoints(self) -> List[APIEndpoint]:
        return list(self._endpoints.values())


class APIDocumentationService(ServiceLifecycle, abc.ABC):
    """Coordinating service executing discovers, validates, and syncs summaries."""
    __test__ = False

    @abc.abstractmethod
    def generate_api_documentation(
        self,
        workspace_id: str,
        code_structure: Dict[str, Any],
        existing_docs: str
    ) -> APIDocumentArtifact:
        """Runs discovery and formats API schemas."""
        pass

    @abc.abstractmethod
    def store_api_summary(self, artifact: APIDocumentArtifact) -> None:
        """Stores API summaries in Memory."""
        pass

    @abc.abstractmethod
    def publish_api_report(self, report: APIReport) -> None:
        """Syncs API reports with Knowledge Hub."""
        pass
