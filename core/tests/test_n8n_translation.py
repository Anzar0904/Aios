import os
import time
from unittest.mock import MagicMock

import pytest
from aios.services.ai_workspace import AIWorkspaceService, WorkspaceMetadata
from aios.services.automation import (
    WorkflowDefinition,
    WorkflowEdge,
    WorkflowExecutionPolicy,
    WorkflowNode,
)
from aios.services.automation import (
    WorkflowMetadata as WFMetadata,
)
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.model import LLMResponse, ModelService
from aios.services.n8n_translation import (
    N8NNodeMapper,
    TranslationContext,
    TranslationReport,
)
from aios.services.n8n_translation_impl import (
    LocalN8NTranslationEngine,
    LocalTranslationValidator,
    LocalWorkflowCompiler,
    LocalWorkflowTranslator,
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
    response.content = "LLM Refined Workflow Translation overview."
    service.execute_request.return_value = response
    return service


@pytest.fixture
def dummy_workflow():
    n_trig = WorkflowNode(
        "n_trig", "Webhook Trigger", "trigger", {"trigger_type": "webhook", "path": "deploy-path"}
    )
    n_act = WorkflowNode(
        "n_act", "HTTP Post", "action", {"action_type": "http_request", "url": "https://deploy.org"}
    )
    edge = WorkflowEdge("e1", "n_trig", "n_act")

    graph = MagicMock()
    graph.nodes = [n_trig, n_act]
    graph.edges = [edge]

    policy = WorkflowExecutionPolicy(
        max_retries=3, retry_delay_seconds=5, timeout_seconds=120, concurrency_limit=1
    )

    return WorkflowDefinition(
        workflow_id="wf_deploy",
        name="Deploy Backend",
        graph=graph,
        triggers=[],
        actions=[],
        credentials=[],
        policy=policy,
        metadata=WFMetadata(["deploy"]),
    )


def test_ir_compilation(dummy_workflow):
    compiler = LocalWorkflowCompiler()
    ir = compiler.compile_definition_to_ir(dummy_workflow)

    assert ir.workflow_id == "wf_deploy"
    assert ir.name == "Deploy Backend"
    assert len(ir.nodes) == 2
    assert ir.nodes[0]["node_id"] == "n_trig"


def test_node_and_connection_mapping(dummy_workflow):
    compiler = LocalWorkflowCompiler()
    ir = compiler.compile_definition_to_ir(dummy_workflow)

    engine = LocalN8NTranslationEngine()
    context = TranslationContext("ws_1", "sess_1")
    n8n_json = engine.translate_ir(ir, context)

    # Verify nodes mapped to n8n types
    nodes = n8n_json["nodes"]
    assert len(nodes) == 2
    webhook_node = next(n for n in nodes if n["id"] == "n_trig")
    assert webhook_node["type"] == "n8n-nodes-base.webhook"
    assert webhook_node["parameters"]["path"] == "deploy-path"

    # Verify connections mapped
    connections = n8n_json["connections"]
    assert "Webhook Trigger" in connections
    assert connections["Webhook Trigger"]["main"][0][0]["node"] == "HTTP Post"


def test_validation_errors(dummy_workflow):
    compiler = LocalWorkflowCompiler()
    ir = compiler.compile_definition_to_ir(dummy_workflow)

    engine = LocalN8NTranslationEngine()
    context = TranslationContext("ws_1", "sess_1")
    n8n_json = engine.translate_ir(ir, context)

    validator = LocalTranslationValidator()
    errors = validator.validate_translation(ir, n8n_json)
    assert len(errors) == 0

    # Introduce duplicate node ID
    n8n_json["nodes"].append(
        {"id": "n_trig", "name": "Duplicate Node", "type": "n8n-nodes-base.manualTrigger"}
    )
    errors = validator.validate_translation(ir, n8n_json)
    assert len(errors) > 0
    assert any("duplicate node id" in e.lower() for e in errors)


def test_workspace_integration(
    tmp_path, mock_memory_service, mock_workspace_service, dummy_workflow
):
    ws_id = "ws_test_trans"
    ws_root = str(tmp_path / ws_id)
    os.makedirs(ws_root, exist_ok=True)

    meta = WorkspaceMetadata(ws_id, 0.0, "/src", ws_root, "active")
    mock_workspace_service._workspaces = {ws_id: meta}

    registry = MagicMock()
    registry.get.side_effect = lambda t: mock_workspace_service if t == AIWorkspaceService else None

    translator = LocalWorkflowTranslator(memory_service=mock_memory_service, registry=registry)
    translator.initialize()

    translator.translate_workflow(dummy_workflow, ws_id)
    expected_report = os.path.join(
        ws_root, "docs", "automations", "TRANSLATION_REPORT_wf_deploy.md"
    )
    expected_json = os.path.join(ws_root, "docs", "automations", "N8N_WORKFLOW_wf_deploy.json")

    assert os.path.exists(expected_report)
    assert os.path.exists(expected_json)

    with open(expected_report, "r") as f:
        content = f.read()
    assert "# n8n Translation Pipeline Execution Report" in content


def test_memory_integration(mock_memory_service, dummy_workflow):
    translator = LocalWorkflowTranslator(memory_service=mock_memory_service)
    translator.initialize()

    report = translator.translate_workflow(dummy_workflow, "ws_1")
    translator.store_translation_summary(report.report_id)

    mock_memory_service.add_memory.assert_called_once()
    args, kwargs = mock_memory_service.add_memory.call_args
    content = kwargs.get("content", args[0] if args else "")
    tags = kwargs.get("tags", [])

    assert "source code" not in content.lower()
    assert "Workflow Compiled to n8n JSON" in content
    assert "n8n_translation" in tags


def test_knowledge_hub_integration(mock_memory_service):
    mock_kh = MagicMock(spec=KnowledgeHubService)
    translator = LocalWorkflowTranslator(memory_service=mock_memory_service, knowledge_hub=mock_kh)
    translator.initialize()

    report = TranslationReport(
        report_id="rep_trans_sess_1",
        session_id="sess_1",
        workspace_id="ws_1",
        node_count=3,
        connection_count=2,
        warnings=[],
        n8n_json_file_path="/workspace/target.json",
        timestamp=time.time(),
    )
    translator.publish_translation_report(report)

    mock_kh.sync_document.assert_called_once()
    args, kwargs = mock_kh.sync_document.call_args
    doc = args[0]
    assert doc.title == "Workflow Translation - rep_trans_sess_1"
    assert "Notion Sync" in doc.content


def test_backward_compatibility():
    class CustomNodeMapper(N8NNodeMapper):
        def map_node(self, node, context):
            return {"id": "custom", "name": "Custom", "type": "n8n-nodes-base.custom"}

    mapper = CustomNodeMapper()
    res = mapper.map_node({}, TranslationContext("ws_1", "sess_1"))
    assert res["id"] == "custom"
