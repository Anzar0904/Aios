"""Phase 7: n8n Automation Intelligence — Production Test Suite.

Tests cover:
- Workflow Registry CRUD
- Workflow Generator (generate from template)
- Deployment Engine (validate raw json, nodes check)
- Workflow Monitor (executions logger, health calculation)
- Workflow Debugger & Diagnostics (diagnose, auto-repair webhooks/credentials)
- Versioning & Rollback (restore target versions, changelogs)
- Knowledge Graph integration assertions
- CLI command dispatcher smoke runs
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from aios.services.workflows import (
    Deployment,
    ExecutionStatus,
    Workflow,
    WorkflowExecution,
    new_id,
)
from aios.services.workflows_impl import WorkflowRegistryServiceImpl

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path / "test_workflows.db")


@pytest.fixture
def reg(tmp_db):
    from aios.local import workflow_commands

    workflow_commands._DB_PATH = tmp_db
    svc = WorkflowRegistryServiceImpl(db_path=tmp_db)
    svc.initialize()
    svc.start()
    yield svc
    svc.shutdown()
    workflow_commands._DB_PATH = None


# ---------------------------------------------------------------------------
# Workflow Registry CRUD
# ---------------------------------------------------------------------------


class TestWorkflowRegistry:
    def test_register_and_get_workflow(self, reg):
        wid = new_id()
        wf = Workflow(
            workflow_id=wid,
            name="Alpha Automation",
            description="Testing CRUD",
            nodes=[{"name": "HTTP", "type": "n8n-nodes-base.httpRequest"}],
        )
        reg.register_workflow(wf)
        fetched = reg.get_workflow(wid)
        assert fetched is not None
        assert fetched.name == "Alpha Automation"
        assert len(fetched.nodes) == 1

    def test_list_workflows(self, reg):
        wid = new_id()
        wf = Workflow(workflow_id=wid, name="Beta Automation")
        reg.register_workflow(wf)
        wfs = reg.list_workflows()
        assert any(w.workflow_id == wid for w in wfs)

    def test_delete_workflow(self, reg):
        wid = new_id()
        wf = Workflow(workflow_id=wid, name="Delete Automation")
        reg.register_workflow(wf)
        assert reg.delete_workflow(wid) is True
        assert reg.get_workflow(wid) is None


# ---------------------------------------------------------------------------
# Workflow Generator
# ---------------------------------------------------------------------------


class TestWorkflowGenerator:
    def test_generate_from_template(self, reg):
        wf = reg.generate_workflow_from_template("My Lead Gen", "Lead Generation System")
        assert wf is not None
        assert wf.name == "My Lead Gen"
        assert len(wf.nodes) >= 2
        assert "Notion Database" in [n["name"] for n in wf.nodes]

    def test_generate_invalid_template_raises(self, reg):
        with pytest.raises(ValueError):
            reg.generate_workflow_from_template("Bad", "NonExistentTemplateXYZ")


# ---------------------------------------------------------------------------
# Deployment Engine
# ---------------------------------------------------------------------------


class TestDeploymentEngine:
    def test_deploy_valid_json(self, reg):
        workflow_json = """
        {
            "nodes": [
                {"name": "Trigger", "type": "n8n-nodes-base.cron"},
                {"name": "Action", "type": "n8n-nodes-base.gmail"}
            ],
            "connections": {}
        }
        """
        wf = reg.deploy_workflow_json("JSON Deploy", workflow_json)
        assert wf is not None
        assert wf.name == "JSON Deploy"
        assert len(wf.nodes) == 2

        # Check deployment record
        deps = reg.get_deployments(wf.workflow_id)
        assert len(deps) == 1
        assert deps[0].nodes_count == 2
        assert deps[0].triggers_count == 1

    def test_deploy_invalid_json_raises(self, reg):
        bad_json = "{invalid-json"
        with pytest.raises(ValueError):
            reg.deploy_workflow_json("Bad JSON", bad_json)

    def test_deploy_empty_nodes_raises(self, reg):
        empty_nodes = '{"nodes": []}'
        with pytest.raises(ValueError):
            reg.deploy_workflow_json("Empty Nodes", empty_nodes)


# ---------------------------------------------------------------------------
# Workflow Monitor
# ---------------------------------------------------------------------------


class TestWorkflowMonitor:
    def test_record_execution_updates_health_score(self, reg):
        wid = new_id()
        wf = Workflow(workflow_id=wid, name="Monitor Automation")
        reg.register_workflow(wf)

        # Success execution
        exec1 = WorkflowExecution(
            execution_id=new_id(),
            workflow_id=wid,
            status=ExecutionStatus.SUCCESS,
            latency_ms=150,
        )
        reg.record_execution(exec1)
        wf_fetched = reg.get_workflow(wid)
        assert wf_fetched.health_score == 100

        # Failed execution
        exec2 = WorkflowExecution(
            execution_id=new_id(),
            workflow_id=wid,
            status=ExecutionStatus.FAILED,
            latency_ms=300,
            failed_node="Action Node",
        )
        reg.record_execution(exec2)
        wf_fetched = reg.get_workflow(wid)
        # 1 success + 1 failure = 50% health
        assert wf_fetched.health_score == 50


# ---------------------------------------------------------------------------
# Workflow Debugger
# ---------------------------------------------------------------------------


class TestWorkflowDebugger:
    def test_diagnose_missing_webhook_url(self, reg):
        wid = new_id()
        wf = Workflow(
            workflow_id=wid,
            name="Diag Webhook",
            nodes=[{"name": "Webhook Node", "type": "n8n-nodes-base.webhook"}],
            webhook_url="",
        )
        reg.register_workflow(wf)
        diag = reg.diagnose_workflow(wid)
        assert diag["status"] == "issues_found"
        issues = diag["issues"]
        assert any(i["code"] == "MISSING_WEBHOOK_URL" for i in issues)

    def test_diagnose_empty_credentials(self, reg):
        wid = new_id()
        wf = Workflow(
            workflow_id=wid,
            name="Diag Creds",
            nodes=[
                {
                    "name": "Notion Sync",
                    "type": "n8n-nodes-base.notion",
                    "parameters": {"credentials": ""},
                }
            ],
        )
        reg.register_workflow(wf)
        diag = reg.diagnose_workflow(wid)
        issues = diag["issues"]
        assert any(i["code"] == "EMPTY_CREDENTIALS" for i in issues)

    def test_repair_workflow(self, reg):
        wid = new_id()
        wf = Workflow(
            workflow_id=wid,
            name="Repair Automation",
            nodes=[
                {"name": "Webhook Node", "type": "n8n-nodes-base.webhook"},
                {
                    "name": "Notion Sync",
                    "type": "n8n-nodes-base.notion",
                    "parameters": {"credentials": ""},
                },
            ],
            webhook_url="",
        )
        reg.register_workflow(wf)

        rep = reg.repair_workflow(wid)
        assert rep["status"] == "fixed"
        assert len(rep["repairs_performed"]) == 2

        # Verify repairs persisted
        wf_repaired = reg.get_workflow(wid)
        assert wf_repaired.webhook_url != ""
        assert wf_repaired.nodes[1]["parameters"]["credentials"] == "dev-key-temp-aios"


# ---------------------------------------------------------------------------
# Versioning and Rollback
# ---------------------------------------------------------------------------


class TestWorkflowVersioning:
    def test_rollback_workflow_version(self, reg):
        # Deploys version 1
        workflow_json_v1 = """
        {
            "nodes": [{"name": "Trigger V1", "type": "n8n-nodes-base.cron"}],
            "connections": {}
        }
        """
        wf = reg.deploy_workflow_json("Versioning Auto", workflow_json_v1)
        assert wf.version == 1

        # Save manual deployment version 2 configuration
        workflow_json_v2 = """
        {
            "nodes": [{"name": "Trigger V2", "type": "n8n-nodes-base.cron"}],
            "connections": {}
        }
        """
        reg.record_deployment(
            Deployment(
                deployment_id=new_id(),
                workflow_id=wf.workflow_id,
                version=2,
                changelog="Manual v2 push",
                raw_json=workflow_json_v2,
            )
        )

        # Rollback versioning target
        # Rollback to V1
        success = reg.rollback_workflow(wf.workflow_id, 1)
        assert success is True

        wf_rolled = reg.get_workflow(wf.workflow_id)
        assert wf_rolled.version == 1
        assert wf_rolled.nodes[0]["name"] == "Trigger V1"


# ---------------------------------------------------------------------------
# Knowledge Graph Integration
# ---------------------------------------------------------------------------


class TestWorkflowsGraphBridge:
    def test_sync_workflow_node(self):
        from aios.services.workflows_graph_bridge import WorkflowsGraphBridge

        mock_engine = MagicMock()
        mock_entity = MagicMock()
        mock_entity.entity_id = "mock-wf-node-id"
        mock_engine.ensure_entity.return_value = mock_entity

        bridge = WorkflowsGraphBridge(mock_engine)
        wf = Workflow(workflow_id="wf-123", name="My Workflow")
        entity_id = bridge.sync_workflow(wf)
        assert entity_id == "mock-wf-node-id"

    def test_sync_deployment(self):
        from aios.services.workflows_graph_bridge import WorkflowsGraphBridge

        mock_engine = MagicMock()
        bridge = WorkflowsGraphBridge(mock_engine)
        d = Deployment(deployment_id="d-123", workflow_id="wf-123", version=2)
        bridge.sync_deployment(d)
        assert mock_engine.ensure_entity.call_count >= 2


# ---------------------------------------------------------------------------
# CLI Command Dispatcher Smoke Tests
# ---------------------------------------------------------------------------


class TestWorkflowCLIDispatch:
    def test_cli_dashboard_smoke(self, reg):
        from aios.local.workflow_commands import cmd_workflow_dashboard

        cmd_workflow_dashboard([])

    def test_cli_generate_smoke(self, reg):
        from aios.local.workflow_commands import cmd_workflow_generate

        cmd_workflow_generate(["TestGen", "Lead Generation System"])

    def test_cli_deploy_smoke(self, reg):
        from aios.local.workflow_commands import cmd_workflow_deploy

        workflow_json = '{"nodes": [{"name": "Cron Trigger", "type": "n8n-nodes-base.cron"}]}'
        cmd_workflow_deploy(["TestDeploy", workflow_json])
