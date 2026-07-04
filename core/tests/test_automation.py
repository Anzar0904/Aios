import os
import time
import pytest
from unittest.mock import MagicMock

from aios.services.memory import MemoryService, MemoryType
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.model import ModelService, LLMResponse
from aios.services.ai_workspace import AIWorkspaceService, WorkspaceMetadata
from aios.services.automation import (
    WorkflowNode,
    WorkflowEdge,
    WorkflowGraph,
    WorkflowTrigger,
    WorkflowAction,
    WorkflowCondition,
    WorkflowVariable,
    WorkflowCredentialReference,
    WorkflowExecutionPolicy,
    WorkflowMetadata as WFMetadata,
    WorkflowDefinition,
    AutomationSession,
    AutomationResult,
    AutomationReport,
    AutomationProvider,
)
from aios.services.automation_impl import (
    LocalAutomationValidator,
    LocalAutomationRegistry,
    LocalAutomationService,
)


@pytest.fixture
def mock_memory_service():
    service = MagicMock(spec=MemoryService)
    return service


@pytest.fixture
def mock_workspace_service():
    service = MagicMock(spec=AIWorkspaceService)
    return service


@pytest.fixture
def mock_model_service():
    service = MagicMock(spec=ModelService)
    response = MagicMock(spec=LLMResponse)
    response.content = "LLM Refined Workflow Execution overview."
    service.execute_request.return_value = response
    return service


@pytest.fixture
def dummy_workflow():
    n_trigger = WorkflowNode("n_trig", "Webhook Trigger", "trigger")
    n_action = WorkflowNode("n_act", "HTTP Post", "action")
    edge = WorkflowEdge("e1", "n_trig", "n_act")
    
    graph = WorkflowGraph([n_trigger, n_action], [edge])
    cred = WorkflowCredentialReference("cred_n8n_key", "n8n", "n8n_api_key")
    policy = WorkflowExecutionPolicy(max_retries=3, retry_delay_seconds=5, timeout_seconds=120, concurrency_limit=1)

    return WorkflowDefinition(
        workflow_id="wf_deploy",
        name="Deploy Backend",
        graph=graph,
        triggers=[WorkflowTrigger("t1", "webhook")],
        actions=[WorkflowAction("a1", "http_request")],
        credentials=[cred],
        policy=policy,
        metadata=WFMetadata(["deploy", "backend"])
    )


def test_graph_validation_pass(dummy_workflow):
    validator = LocalAutomationValidator()
    errors = validator.validate_workflow(dummy_workflow)
    assert len(errors) == 0


def test_graph_validation_disconnected_nodes(dummy_workflow):
    validator = LocalAutomationValidator()
    # Add a disconnected node
    n_unconnected = WorkflowNode("n_isolated", "isolated script", "action")
    dummy_workflow.graph.nodes.append(n_unconnected)

    errors = validator.validate_workflow(dummy_workflow)
    assert len(errors) > 0
    assert any("disconnected node" in e.lower() for e in errors)


def test_graph_validation_cycles(dummy_workflow):
    validator = LocalAutomationValidator()
    # Create cycle
    edge_back = WorkflowEdge("e_cycle", "n_act", "n_trig")
    dummy_workflow.graph.edges.append(edge_back)

    errors = validator.validate_workflow(dummy_workflow)
    assert len(errors) > 0
    assert any("circular execution" in e.lower() for e in errors)


def test_graph_validation_duplicates(dummy_workflow):
    validator = LocalAutomationValidator()
    # Add duplicate ID
    dummy_workflow.graph.nodes.append(WorkflowNode("n_act", "Duplicate action", "action"))

    errors = validator.validate_workflow(dummy_workflow)
    assert len(errors) > 0
    assert any("duplicate identifier" in e.lower() for e in errors)


def test_registry_and_providers_operations(mock_memory_service, dummy_workflow):
    service = LocalAutomationService(memory_service=mock_memory_service)
    service.initialize()

    # Register workflow
    service._workflow_registry.register_workflow(dummy_workflow)
    retrieved = service._workflow_registry.get_workflow("wf_deploy")
    assert retrieved is not None
    assert retrieved.name == "Deploy Backend"

    # Verify default registered providers list
    providers = service._providers.list_providers()
    assert "n8n" in providers
    assert "github_actions" in providers
    assert "temporal" in providers


def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service, dummy_workflow):
    ws_id = "ws_test_auto"
    ws_root = str(tmp_path / ws_id)
    os.makedirs(ws_root, exist_ok=True)

    meta = WorkspaceMetadata(ws_id, 0.0, "/src", ws_root, "active")
    mock_workspace_service._workspaces = {ws_id: meta}

    registry = MagicMock()
    registry.get.side_effect = lambda t: mock_workspace_service if t == AIWorkspaceService else None

    service = LocalAutomationService(
        memory_service=mock_memory_service,
        registry=registry
    )
    service.initialize()

    # Register workflow
    service._workflow_registry.register_workflow(dummy_workflow)
    
    session = service.run_automation("wf_deploy", ws_id, "n8n")
    expected_file = os.path.join(ws_root, "docs", "automations", f"AUTOMATION_REPORT_{session.session_id}.md")

    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        content = f.read()
    assert "# Quality Automation Execution Report" in content
    assert session.status == "success"


def test_memory_integration(mock_memory_service, dummy_workflow):
    service = LocalAutomationService(
        memory_service=mock_memory_service
    )
    service.initialize()
    service._workflow_registry.register_workflow(dummy_workflow)

    session = service.run_automation("wf_deploy", "ws_1", "n8n")
    service.store_automation_summary(session.session_id)

    mock_memory_service.add_memory.assert_called_once()
    args, kwargs = mock_memory_service.add_memory.call_args
    content = kwargs.get("content", args[0] if args else "")
    tags = kwargs.get("tags", [])

    # Ensure credentials not stored
    assert "credentials" not in content.lower()
    assert "n8n_api_key" not in content.lower()
    assert "Automation Execution Logged" in content
    assert "automation_execution" in tags


def test_knowledge_hub_integration(mock_memory_service):
    mock_kh = MagicMock(spec=KnowledgeHubService)
    service = LocalAutomationService(
        memory_service=mock_memory_service,
        knowledge_hub=mock_kh
    )
    service.initialize()

    report = AutomationReport(
        report_id="rep_aut_sess_1",
        workspace_id="ws_1",
        session_id="sess_1",
        workflow_name="Deploy Module",
        status="success",
        timestamp=time.time()
    )
    service.publish_automation_report(report)

    mock_kh.sync_document.assert_called_once()
    args, kwargs = mock_kh.sync_document.call_args
    doc = args[0]
    assert doc.title == "Automation Run - rep_aut_sess_1"
    assert "Notion Sync" in doc.content


def test_backward_compatibility():
    class CustomProvider(AutomationProvider):
        @property
        def provider_id(self) -> str:
            return "custom_runner"

        def validate_definition(self, definition):
            return []

        def execute_workflow(self, definition, session):
            return AutomationResult(session.session_id, True)

    provider = CustomProvider()
    assert provider.provider_id == "custom_runner"
    res = provider.execute_workflow(None, AutomationSession("sess_1", "wf_1", "ws_1", "pending", 0.0))
    assert res.success is True
