from unittest.mock import MagicMock

import pytest
from aios.services.api_documentation import (
    APIDocumentArtifact,
    APIEndpoint,
    APIRegistry,
    APIReport,
    APIResponse,
)
from aios.services.api_documentation_impl import (
    LocalAPIAnalyzer,
    LocalAPIDocumentationPlanner,
    LocalAPIDocumentationService,
    LocalAPIDocumentValidator,
)
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.model import LLMResponse, ModelService


@pytest.fixture
def sample_code_structure():
    return {
        "workspace_id": "ws_1",
        "routes": [
            {"path": "/api/v1/agent", "method": "POST", "parameters": [{"name": "agent_id"}]},
            {"path": "/api/v1/memory", "method": "GET", "parameters": []},
        ],
    }


def test_api_analyzer(sample_code_structure):
    analyzer = LocalAPIAnalyzer()
    existing = "/api/v1/memory"  # memory route is documented, agent is missing

    report = analyzer.analyze_api(sample_code_structure, existing)
    assert len(report.undocumented_endpoints) == 1
    assert "POST /api/v1/agent" in report.undocumented_endpoints


def test_api_planner():
    planner = LocalAPIDocumentationPlanner()
    report = APIReport(
        report_id="r1",
        workspace_id="ws_1",
        undocumented_endpoints=["GET /api/v1/profile"],
        missing_parameters=[],
        outdated_schemas=[],
        missing_examples=[],
        recommendations=[],
        timestamp=0.0,
    )

    endpoints = planner.plan_api_documentation(report)
    assert len(endpoints) == 1
    assert endpoints[0].path == "/api/v1/profile"
    assert endpoints[0].method == "GET"


def test_api_validator():
    validator = LocalAPIDocumentValidator()

    # 1. Valid endpoint
    ep1 = APIEndpoint("/path", "GET", "summary", [], None, [APIResponse(200, None, "ok")])
    artifact = APIDocumentArtifact("a1", "ws_1", "content", [ep1], 0.0)
    errors = validator.validate_api_document(artifact)
    assert len(errors) == 0

    # 2. Duplicate endpoint path
    artifact.endpoints.append(ep1)
    errors_dup = validator.validate_api_document(artifact)
    assert len(errors_dup) == 1
    assert "Duplicate route" in errors_dup[0]


def test_api_registry():
    registry = APIRegistry()
    ep = APIEndpoint("/path", "GET", "summary")

    registry.register_endpoint(ep)
    assert registry.get_endpoint("GET", "/path") == ep
    assert len(registry.list_endpoints()) == 1


def test_service_evaluation_flow(sample_code_structure):
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    mock_model = MagicMock(spec=ModelService)

    # Mock LLM Response
    mock_response = MagicMock(spec=LLMResponse)
    mock_response.content = "## POST /api/v1/agent\nLLM Refined specs."
    mock_model.execute_request.return_value = mock_response

    service = LocalAPIDocumentationService(
        memory_service=mock_memory, knowledge_hub=mock_kh, model_service=mock_model
    )
    service.initialize()

    artifact = service.generate_api_documentation("ws_1", sample_code_structure, "")
    assert artifact.content == "## POST /api/v1/agent\nLLM Refined specs."

    # Store
    service.store_api_summary(artifact)
    mock_memory.add_memory.assert_called_once()

    # Publish
    report = MagicMock()
    service.publish_api_report(report)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomValidator(LocalAPIDocumentValidator):
        def validate_api_document(self, artifact):
            errors = super().validate_api_document(artifact)
            errors.append("custom_error")
            return errors

    validator = CustomValidator()
    errors = validator.validate_api_document(APIDocumentArtifact("a1", "ws_1", "", [], 0.0))
    assert "custom_error" in errors
