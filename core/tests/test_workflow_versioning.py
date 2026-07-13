import json
import os
import time
from unittest.mock import MagicMock

import pytest
from aios.services.ai_workspace import AIWorkspaceService, WorkspaceMetadata
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.workflow_versioning import (
    WorkflowVersion,
    WorkflowVersionMetadata,
    WorkflowVersionReport,
)
from aios.services.workflow_versioning_impl import (
    LocalWorkflowCompatibilityAnalyzer,
    LocalWorkflowMigrationPlanner,
    LocalWorkflowVersionRegistry,
    LocalWorkflowVersionService,
    LocalWorkflowVersionValidator,
)


@pytest.fixture
def mock_memory_service():
    service = MagicMock(spec=MemoryService)
    return service


@pytest.fixture
def mock_workspace_service():
    service = MagicMock(spec=AIWorkspaceService)
    return service


def test_version_registry():
    registry = LocalWorkflowVersionRegistry()
    meta = WorkflowVersionMetadata("Alice", "tag1", "1.0.0", "Init", "active")
    v = WorkflowVersion(
        "v_1", "wf_1", "ir1", "tr1", "op1", "ap1", "tl1", time.time(), meta, "compatible", "notes"
    )

    registry.register_version(v)
    assert registry.get_version("v_1") == v
    assert registry.get_graph("wf_1").versions["v_1"] == v


def test_compatibility_analyzer():
    compat = LocalWorkflowCompatibilityAnalyzer()

    m1 = WorkflowVersionMetadata("Alice", "tag1", "1.0.0", "Init", "active")
    v1 = WorkflowVersion(
        "v_1", "wf_1", "ir1", "tr1", "op1", "ap1", "tl1", time.time(), m1, "compatible", "notes"
    )

    m2 = WorkflowVersionMetadata("Alice", "tag2", "1.1.0", "Upgrade minor", "active")
    v2 = WorkflowVersion(
        "v_2", "wf_1", "ir2", "tr2", "op2", "ap2", "tl2", time.time(), m2, "compatible", "notes"
    )

    res_minor = compat.analyze_compatibility(v1, v2)
    assert res_minor["status"] == "compatible"

    m3 = WorkflowVersionMetadata("Alice", "tag3", "2.0.0", "Upgrade major", "active")
    v3 = WorkflowVersion(
        "v_3", "wf_1", "ir3", "tr3", "op3", "ap3", "tl3", time.time(), m3, "compatible", "notes"
    )

    res_major = compat.analyze_compatibility(v1, v3)
    assert res_major["status"] == "breaking"
    assert len(res_major["breaking_changes"]) > 0


def test_migration_planner():
    planner = LocalWorkflowMigrationPlanner()

    m1 = WorkflowVersionMetadata("Alice", "tag1", "1.0.0", "Init", "active")
    v1 = WorkflowVersion(
        "v_1", "wf_1", "ir1", "tr1", "op1", "ap1", "tl1", time.time(), m1, "compatible", "notes"
    )
    m2 = WorkflowVersionMetadata("Alice", "tag2", "2.0.0", "Upgrade breaking", "active")
    v2 = WorkflowVersion(
        "v_2", "wf_1", "ir2", "tr2", "op2", "ap2", "tl2", time.time(), m2, "compatible", "notes"
    )

    plan = planner.create_migration_plan(v1, v2)
    assert plan.compatibility_status == "breaking"
    assert len(plan.steps) > 0

    rollback = planner.create_rollback_plan(v2, v1)
    assert rollback.risk == "medium"
    assert len(rollback.migration_steps) > 0
    assert len(rollback.validation_checklist) > 0


def test_version_validator():
    validator = LocalWorkflowVersionValidator()

    m_valid = WorkflowVersionMetadata("Alice", "tag1", "1.0.0", "Init", "active")
    v_valid = WorkflowVersion(
        "v_1",
        "wf_1",
        "ir1",
        "tr1",
        "op1",
        "ap1",
        "tl1",
        time.time(),
        m_valid,
        "compatible",
        "notes",
    )
    assert len(validator.validate_version(v_valid)) == 0

    # Invalid semver
    m_invalid = WorkflowVersionMetadata("Alice", "tag1", "1.a.0", "Init", "active")
    v_invalid = WorkflowVersion(
        "v_1",
        "wf_1",
        "ir1",
        "tr1",
        "op1",
        "ap1",
        "tl1",
        time.time(),
        m_invalid,
        "compatible",
        "notes",
    )
    errors = validator.validate_version(v_invalid)
    assert len(errors) > 0
    assert any("semantic version" in e.lower() for e in errors)


def test_version_service_creation_and_diff(mock_memory_service):
    service = LocalWorkflowVersionService(memory_service=mock_memory_service)
    service.initialize()

    ir1 = {"nodes": {"n1": {"type": "Webhook"}, "n2": {"type": "Script"}}}
    ir2 = {"nodes": {"n1": {"type": "Webhook"}, "n3": {"type": "Slack"}}}

    v1 = service.create_version("wf_1", "Alice", "1.0.0", "First", json.dumps(ir1))
    v2 = service.create_version("wf_1", "Alice", "1.1.0", "Second", json.dumps(ir2))

    history = service.get_history("wf_1")
    assert len(history.history_timeline) == 2

    diff = service.diff_versions(v1.version_id, v2.version_id)
    assert "n3" in diff.added_nodes
    assert "n2" in diff.removed_nodes


def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service):
    ws_id = "ws_test_ver"
    ws_root = str(tmp_path / ws_id)
    os.makedirs(ws_root, exist_ok=True)

    meta = WorkspaceMetadata(ws_id, 0.0, "/src", ws_root, "active")
    mock_workspace_service._workspaces = {ws_id: meta}

    registry = MagicMock()
    registry.get.side_effect = lambda t: mock_workspace_service if t == AIWorkspaceService else None

    service = LocalWorkflowVersionService(memory_service=mock_memory_service, registry=registry)
    service.initialize()

    service.create_version("wf_1", "Alice", "1.0.0", "Init", "{}")
    service.generate_version_report(ws_id)

    expected_file = os.path.join(ws_root, "docs", "monitors", f"VERSION_REPORT_{ws_id}.md")
    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        content = f.read()
    assert "# Workflow Versioning & Evolution Report" in content


def test_memory_integration(mock_memory_service):
    service = LocalWorkflowVersionService(memory_service=mock_memory_service)
    service.initialize()

    service.create_version("wf_1", "Alice", "1.0.0", "Init", "{}")
    service.generate_version_report("ws_1")
    service.store_version_summary("ws_1")

    mock_memory_service.add_memory.assert_called_once()
    args, kwargs = mock_memory_service.add_memory.call_args
    content = kwargs.get("content", args[0] if args else "")
    tags = kwargs.get("tags", [])

    assert "source code" not in content.lower()
    assert "Workflow Evolution Tracked" in content
    assert "workflow_versioning" in tags


def test_knowledge_hub_integration(mock_memory_service):
    mock_kh = MagicMock(spec=KnowledgeHubService)
    service = LocalWorkflowVersionService(memory_service=mock_memory_service, knowledge_hub=mock_kh)
    service.initialize()

    report = WorkflowVersionReport(
        report_id="rep_ver_123",
        workspace_id="ws_1",
        timeline_summaries={},
        difs_count=1,
        timestamp=time.time(),
    )
    service.publish_version_report(report)

    mock_kh.sync_document.assert_called_once()
    args, kwargs = mock_kh.sync_document.call_args
    doc = args[0]
    assert doc.title == "Workflow Versioning - rep_ver_123"
    assert "Notion Sync" in doc.content


def test_backward_compatibility():
    class CustomVersionValidator(LocalWorkflowVersionValidator):
        def validate_version(self, version):
            errors = super().validate_version(version)
            errors.append("Custom validation check run.")
            return errors

    val = CustomVersionValidator()
    m = WorkflowVersionMetadata("Alice", "tag1", "1.0.0", "Init", "active")
    v = WorkflowVersion(
        "v_1", "wf_1", "ir1", "tr1", "op1", "ap1", "tl1", time.time(), m, "compatible", "notes"
    )
    errors = val.validate_version(v)
    assert "Custom validation check run." in errors
