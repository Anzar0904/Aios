import tempfile
from unittest.mock import MagicMock

from aios.services.model import LLMResponse
from aios.services.n8n import (
    InternalConnection,
    InternalNode,
    InternalWorkflow,
)
from aios.services.n8n_impl import LocalN8NService


def test_workflow_translation_and_serialization():
    model_service = MagicMock()
    service = LocalN8NService(model_service)

    # Construct workflow
    wf = InternalWorkflow(
        id="wf-123",
        name="Test Sync",
        nodes=[
            InternalNode("1", "Trigger", "n8n-nodes-base.cron", {}, [100, 200]),
            InternalNode(
                "2", "HTTP", "n8n-nodes-base.httpRequest", {"url": "https://api.test"}, [300, 200]
            ),
        ],
        connections=[InternalConnection("Trigger", "HTTP")],
    )

    # Translate to n8n format
    n8n_data = service.internal_to_n8n(wf)
    assert n8n_data["name"] == "Test Sync"
    assert len(n8n_data["nodes"]) == 2
    assert "Trigger" in n8n_data["connections"]

    # Translate back to internal
    imported = service.n8n_to_internal(n8n_data)
    assert imported.name == "Test Sync"
    assert len(imported.nodes) == 2
    assert imported.connections[0].from_node == "Trigger"
    assert imported.connections[0].to_node == "HTTP"


def test_workflow_graph_validator():
    model_service = MagicMock()
    service = LocalN8NService(model_service)

    # 1. Valid acyclic connected workflow
    wf_valid = InternalWorkflow(
        id=None,
        name="Valid Graph",
        nodes=[
            InternalNode("1", "Start", "n8n-nodes-base.start"),
            InternalNode("2", "Action", "n8n-nodes-base.httpRequest"),
        ],
        connections=[InternalConnection("Start", "Action")],
    )
    res_valid = service.validate_workflow(wf_valid)
    assert res_valid["valid"] is True
    assert len(res_valid["errors"]) == 0

    # 2. Graph containing circular references (loops)
    wf_cycle = InternalWorkflow(
        id=None,
        name="Cycle Graph",
        nodes=[InternalNode("1", "Node A", "type"), InternalNode("2", "Node B", "type")],
        connections=[
            InternalConnection("Node A", "Node B"),
            InternalConnection("Node B", "Node A"),
        ],
    )
    res_cycle = service.validate_workflow(wf_cycle)
    assert res_cycle["valid"] is False
    assert any("Circular dependency" in e for e in res_cycle["errors"])

    # 3. Graph containing unreachable nodes
    wf_unreachable = InternalWorkflow(
        id=None,
        name="Unreachable Graph",
        nodes=[
            InternalNode("1", "Start", "n8n-nodes-base.start"),
            InternalNode("2", "HTTP", "n8n-nodes-base.httpRequest"),
            InternalNode("3", "Isolated Node", "n8n-nodes-base.httpRequest"),
        ],
        connections=[InternalConnection("Start", "HTTP")],
    )
    res_unreachable = service.validate_workflow(wf_unreachable)
    assert res_unreachable["valid"] is False
    assert any("Unreachable nodes" in e for e in res_unreachable["errors"])


def test_natural_language_workflow_generator():
    model_service = MagicMock()
    mock_llm_json = """
{
  "name": "NL Workflow",
  "nodes": [
    {"id": "n1", "name": "Start", "type": "n8n-nodes-base.start", "position": [100, 100]},
    {"id": "n2", "name": "Notify", "type": "n8n-nodes-base.email", "position": [300, 100]}
  ],
  "connections": [
    {"from_node": "Start", "to_node": "Notify", "to_input": 0}
  ]
}
"""
    model_service.execute_request.return_value = LLMResponse(
        content=mock_llm_json, model_name="claude-3-5-sonnet", provider_name="claude"
    )

    service = LocalN8NService(model_service)
    wf = service.generate_workflow_from_natural_language(
        "Send email notifications on start trigger"
    )

    assert wf.name == "NL Workflow"
    assert len(wf.nodes) == 2
    assert wf.connections[0].from_node == "Start"
    assert wf.connections[0].to_node == "Notify"


def test_workflow_lifecycle_and_health():
    model_service = MagicMock()
    with tempfile.TemporaryDirectory() as tmpdir:
        service = LocalN8NService(
            model_service, cache_filename="workflows.json", workspace_root=tmpdir
        )
        service.initialize()

        # Create
        wf = InternalWorkflow(
            id=None,
            name="Lifecycle Test",
            nodes=[InternalNode("1", "Start", "n8n-nodes-base.start")],
        )
        created = service.create_workflow(wf)
        assert created.id is not None
        assert len(service.list_workflows()) == 1

        # Read
        retrieved = service.get_workflow(created.id)
        assert retrieved.name == "Lifecycle Test"

        # Update
        retrieved.name = "Updated Test Name"
        service.update_workflow(created.id, retrieved)
        assert service.get_workflow(created.id).name == "Updated Test Name"

        # Health
        health = service.check_health()
        assert health.online is True

        # Execution & Metrics
        assert service.execute_workflow(created.id) is True
        metrics = service.get_execution_metrics(created.id)
        assert metrics.status == "success"
        assert len(metrics.logs) > 0

        # Delete
        assert service.delete_workflow(created.id) is True
        assert len(service.list_workflows()) == 0
