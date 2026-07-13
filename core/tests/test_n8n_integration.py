import json
import os
import time
from unittest.mock import MagicMock

import pytest
from aios.services.ai_workspace import AIWorkspaceService, WorkspaceMetadata
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.n8n_integration import (
    APIKeyAuthenticationProvider,
    BearerTokenAuthenticationProvider,
    N8NConnectionManager,
    N8NConnectionProfile,
    N8NIntegrationReport,
)
from aios.services.n8n_integration_impl import (
    LocalN8NClient,
    LocalN8NHealthMonitor,
    LocalN8NIntegrationService,
    LocalN8NValidator,
)


@pytest.fixture
def mock_memory_service():
    service = MagicMock(spec=MemoryService)
    return service


@pytest.fixture
def mock_workspace_service():
    service = MagicMock(spec=AIWorkspaceService)
    return service


def test_authentication_providers():
    api_provider = APIKeyAuthenticationProvider("test-api-key")
    headers_api = api_provider.get_auth_headers()
    assert headers_api["X-N8N-API-KEY"] == "test-api-key"

    bearer_provider = BearerTokenAuthenticationProvider("test-bearer-token")
    headers_bearer = bearer_provider.get_auth_headers()
    assert headers_bearer["Authorization"] == "Bearer test-bearer-token"


def test_connection_management():
    profile = N8NConnectionProfile("http://localhost:5678", "api_key", 15)
    auth_provider = APIKeyAuthenticationProvider("test-key")
    manager = N8NConnectionManager(profile, auth_provider)

    assert manager.profile.url == "http://localhost:5678"
    assert manager.get_headers()["X-N8N-API-KEY"] == "test-key"


def test_health_monitor():
    monitor = LocalN8NHealthMonitor()
    health = monitor.check_health()

    assert health["status"] == "online"
    assert health["version"] == "1.25.0"
    assert health["latency_ms"] > 0
    assert "webhooks" in health["capabilities"]


def test_validator():
    validator = LocalN8NValidator()
    
    # Valid profile
    profile_valid = N8NConnectionProfile("https://n8n.myorg.com", "bearer_token", 30)
    assert len(validator.validate_server_config(profile_valid)) == 0

    # Invalid profile
    profile_invalid = N8NConnectionProfile("localhost:5678", "api_key", -1)
    errors = validator.validate_server_config(profile_invalid)
    assert len(errors) == 2
    assert any("url" in e.lower() for e in errors)
    assert any("timeout_seconds" in e.lower() for e in errors)


def test_client_upload_and_trigger():
    client = LocalN8NClient()
    wf_json = {"name": "Test Workflow", "nodes": [], "connections": {}}

    # Upload
    upload_res = client.upload_workflow(wf_json)
    workflow_id = upload_res["id"]
    assert workflow_id.startswith("n8n_wf_")
    assert upload_res["name"] == "Test Workflow"

    # Trigger
    exec_res = client.execute_workflow(workflow_id, {"input_param": 10})
    assert exec_res["status"] == "success"
    assert exec_res["workflowId"] == workflow_id
    assert exec_res["data"]["input_param"] == 10

    # List & retrieve
    workflows = client.list_workflows()
    assert len(workflows) == 1
    assert workflows[0]["id"] == workflow_id


def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service):
    ws_id = "ws_test_integration"
    ws_root = str(tmp_path / ws_id)
    os.makedirs(ws_root, exist_ok=True)

    meta = WorkspaceMetadata(ws_id, 0.0, "/src", ws_root, "active")
    mock_workspace_service._workspaces = {ws_id: meta}

    registry = MagicMock()
    registry.get.side_effect = lambda t: mock_workspace_service if t == AIWorkspaceService else None

    service = LocalN8NIntegrationService(
        memory_service=mock_memory_service,
        registry=registry
    )
    service.initialize()

    wf_json = {"name": "Integrate Webhook", "nodes": []}
    wf_id = service.upload_workflow_json(ws_id, wf_json)
    
    expected_file = os.path.join(ws_root, "docs", "automations", f"N8N_METADATA_{wf_id}.json")
    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        meta_data = json.load(f)
    
    assert meta_data["workflow_id"] == wf_id
    assert meta_data["workspace_id"] == ws_id


def test_memory_integration(mock_memory_service):
    service = LocalN8NIntegrationService(
        memory_service=mock_memory_service
    )
    service.initialize()

    report = service.get_health_status()
    service.store_integration_summary(report.report_id)

    mock_memory_service.add_memory.assert_called_once()
    args, kwargs = mock_memory_service.add_memory.call_args
    content = kwargs.get("content", args[0] if args else "")
    tags = kwargs.get("tags", [])

    # Ensure secrets/tokens not stored
    assert "token" not in content.lower()
    assert "secret" not in content.lower()
    assert "n8n Integration Server status compiled" in content
    assert "n8n_integration" in tags


def test_knowledge_hub_integration(mock_memory_service):
    mock_kh = MagicMock(spec=KnowledgeHubService)
    service = LocalN8NIntegrationService(
        memory_service=mock_memory_service,
        knowledge_hub=mock_kh
    )
    service.initialize()

    report = N8NIntegrationReport(
        report_id="rep_int_123",
        workspace_id="ws_1",
        server_version="1.25.0",
        connectivity_status="online",
        latency_ms=10.0,
        uploaded_workflows_count=5,
        timestamp=time.time()
    )
    service.publish_integration_report(report)

    mock_kh.sync_document.assert_called_once()
    args, kwargs = mock_kh.sync_document.call_args
    doc = args[0]
    assert doc.title == "n8n Integration Status - rep_int_123"
    assert "Notion Sync" in doc.content


def test_backward_compatibility():
    class CustomValidator(LocalN8NValidator):
        def validate_server_config(self, profile):
            errors = super().validate_server_config(profile)
            errors.append("Custom validation check run.")
            return errors

    val = CustomValidator()
    errors = val.validate_server_config(N8NConnectionProfile("localhost", "api_key", 10))
    assert "Custom validation check run." in errors
