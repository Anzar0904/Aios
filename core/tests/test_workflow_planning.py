import os
import time
from unittest.mock import MagicMock

import pytest
from aios.services.ai_workspace import AIWorkspaceService, WorkspaceMetadata
from aios.services.automation import WorkflowEdge, WorkflowNode
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.model import LLMResponse, ModelService
from aios.services.workflow_planning import (
    WorkflowPlanningReport,
)
from aios.services.workflow_planning_impl import (
    LocalWorkflowDependencyResolver,
    LocalWorkflowIntentAnalyzer,
    LocalWorkflowOptimizer,
    LocalWorkflowPlanner,
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
    response.content = "LLM Refined Workflow Planning details."
    service.execute_request.return_value = response
    return service


def test_intent_analysis():
    analyzer = LocalWorkflowIntentAnalyzer()
    
    # CD Intent
    res_cd = analyzer.analyze_intent("Release v1.2.0 and deploy application to production")
    assert res_cd["target_template"] == "cd_pipeline"
    assert "cd" in res_cd["tags"]

    # CI Intent
    res_ci = analyzer.analyze_intent("Run pytest test suite for the kernel branch")
    assert res_ci["target_template"] == "testing_pipeline"
    assert "ci" in res_ci["tags"]


def test_dependency_resolution():
    resolver = LocalWorkflowDependencyResolver()
    
    n1 = WorkflowNode("n1", "Start", "trigger")
    n2 = WorkflowNode("n2", "Lint", "action")
    n3 = WorkflowNode("n3", "Test", "action")
    
    edges = [
        WorkflowEdge("e1", "n1", "n2"),
        WorkflowEdge("e2", "n2", "n3")
    ]
    
    ordered = resolver.resolve_dependencies([n1, n2, n3], edges)
    # n1 triggers n2, n2 triggers n3. So topological order must be n1 -> n2 -> n3
    assert ordered == ["n1", "n2", "n3"]


def test_optimizer_merges_and_prunes():
    optimizer = LocalWorkflowOptimizer()
    
    n_trig = WorkflowNode("trig", "Webhook", "trigger")
    n_act1 = WorkflowNode("act_pytest", "Pytest Suite", "action")
    n_act2 = WorkflowNode("act_pytest_dup", "Pytest Suite", "action") # duplicate
    n_isolated = WorkflowNode("act_isolated", "Isolated Script", "action") # unreachable
    
    edges = [
        WorkflowEdge("e1", "trig", "act_pytest"),
        WorkflowEdge("e2", "trig", "act_pytest_dup")
    ]
    
    opt_nodes, opt_edges, opts = optimizer.optimize_graph(
        [n_trig, n_act1, n_act2, n_isolated], edges
    )
    
    # Duplicate action must be merged
    assert len(opt_nodes) == 2  # trig and act_pytest (isolated pruned, duplicate merged)
    assert any("merged duplicate" in o.lower() for o in opts)
    assert any("discarded unreachable" in o.lower() for o in opts)
    
    # Edges should be consolidated to one single edge
    assert len(opt_edges) == 1
    assert opt_edges[0].source_node_id == "trig"
    assert opt_edges[0].target_node_id == "act_pytest"


def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service):
    ws_id = "ws_test_plan"
    ws_root = str(tmp_path / ws_id)
    os.makedirs(ws_root, exist_ok=True)

    meta = WorkspaceMetadata(ws_id, 0.0, "/src", ws_root, "active")
    mock_workspace_service._workspaces = {ws_id: meta}

    registry = MagicMock()
    registry.get.side_effect = lambda t: mock_workspace_service if t == AIWorkspaceService else None

    planner = LocalWorkflowPlanner(
        memory_service=mock_memory_service,
        registry=registry
    )
    planner.initialize()

    session = planner.create_planning_session(ws_id, "Analyze and run security scan checks")
    planner.generate_plan(session)

    expected_file = os.path.join(ws_root, "docs", "planners", f"PLANNING_REPORT_{session.session_id}.md")
    
    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        content = f.read()
    assert "# Workflow Planning Execution Report" in content
    assert session.status == "closed"


def test_memory_integration(mock_memory_service):
    planner = LocalWorkflowPlanner(
        memory_service=mock_memory_service
    )
    planner.initialize()

    session = planner.create_planning_session("ws_1", "Run backups cron daily")
    planner.generate_plan(session)
    planner.store_planning_summary(session.session_id)

    mock_memory_service.add_memory.assert_called_once()
    args, kwargs = mock_memory_service.add_memory.call_args
    content = kwargs.get("content", args[0] if args else "")
    tags = kwargs.get("tags", [])

    assert "source code" not in content.lower()
    assert "Workflow Plan Registered" in content
    assert "workflow_planning" in tags


def test_knowledge_hub_integration(mock_memory_service):
    mock_kh = MagicMock(spec=KnowledgeHubService)
    planner = LocalWorkflowPlanner(
        memory_service=mock_memory_service,
        knowledge_hub=mock_kh
    )
    planner.initialize()

    report = WorkflowPlanningReport(
        report_id="rep_plan_sess_1",
        workspace_id="ws_1",
        session_id="sess_1",
        raw_intent="Deploy website frontend",
        planned_workflow_id="wf_cd_123",
        timestamp=time.time()
    )
    planner.publish_planning_report(report)

    mock_kh.sync_document.assert_called_once()
    args, kwargs = mock_kh.sync_document.call_args
    doc = args[0]
    assert doc.title == "Workflow Plan - rep_plan_sess_1"
    assert "Notion Sync" in doc.content


def test_backward_compatibility(mock_memory_service):
    class CustomWorkflowOptimizer(LocalWorkflowOptimizer):
        def optimize_graph(self, nodes, edges):
            n, e, opts = super().optimize_graph(nodes, edges)
            opts.append("Custom optimizer step run.")
            return n, e, opts

    opt = CustomWorkflowOptimizer()
    n, e, opts = opt.optimize_graph([], [])
    assert "Custom optimizer step run." in opts
