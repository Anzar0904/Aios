import json
from unittest.mock import MagicMock, patch

from aios.cli import execute_builtin_cli_command
from aios.n8n.runtime import N8NWorkflowRuntimeManager


def _make_runtime(tmp_path, workflow_mgr=None, exec_mgr=None):
    """Build a runtime manager with mocked client, wiring managers directly."""
    with (
        patch("aios.n8n.runtime.N8NLiveConnectionManager") as mock_conn,
        patch("aios.n8n.runtime.N8NWorkflowRuntimeManager._init_client", return_value=MagicMock()),
    ):
        mock_conn_inst = MagicMock()
        mock_conn_inst.load_state.return_value = {
            "connected": True,
            "url": "http://localhost:5678",
        }
        mock_conn.return_value = mock_conn_inst

        mgr = N8NWorkflowRuntimeManager()

    # Override managers and history file after construction
    mgr.workflow_mgr = workflow_mgr
    mgr.exec_mgr = exec_mgr
    mgr.history_file = tmp_path / "deployment_history.json"
    mgr.history = {}
    return mgr


# ── Deploy ──────────────────────────────────────────────────────────────────


def test_n8n_runtime_deploy(tmp_path):
    """New workflow is created and persisted to history."""
    mock_wf = MagicMock()
    mock_wf.list_workflows.return_value = []
    mock_wf.upload_workflow.return_value = {
        "id": "wf_deploy_123",
        "name": "Production Job",
        "nodes": [],
        "connections": {},
    }

    mgr = _make_runtime(tmp_path, workflow_mgr=mock_wf)

    with patch.object(mgr, "generate_runtime_reports"):
        wf = {"name": "Production Job", "nodes": [], "connections": {}}
        res = mgr.deploy(wf)

    assert res["success"] is True
    assert res["workflow_id"] == "wf_deploy_123"
    assert "wf_deploy_123" in mgr.history
    assert len(mgr.history["wf_deploy_123"]) == 1


def test_n8n_runtime_deploy_update_existing(tmp_path):
    """Existing workflow is updated when force=True."""
    mock_wf = MagicMock()
    mock_wf.list_workflows.return_value = [{"id": "wf_existing", "name": "Same Job"}]
    mock_wf.update_workflow.return_value = {
        "id": "wf_existing",
        "name": "Same Job",
        "nodes": [],
        "connections": {},
    }

    mgr = _make_runtime(tmp_path, workflow_mgr=mock_wf)

    with patch.object(mgr, "generate_runtime_reports"):
        wf = {"name": "Same Job", "nodes": [], "connections": {}}
        res = mgr.deploy(wf, force=True)

    assert res["success"] is True
    assert res["workflow_id"] == "wf_existing"


def test_n8n_runtime_deploy_blocked_without_force(tmp_path):
    """Deployment is blocked when workflow exists and force=False."""
    mock_wf = MagicMock()
    mock_wf.list_workflows.return_value = [{"id": "wf_block", "name": "Block Job"}]

    mgr = _make_runtime(tmp_path, workflow_mgr=mock_wf)

    with patch.object(mgr, "generate_runtime_reports"):
        wf = {"name": "Block Job", "nodes": [], "connections": {}}
        res = mgr.deploy(wf, force=False)

    assert res["success"] is False
    assert "already exists" in res["message"]


# ── Execute ─────────────────────────────────────────────────────────────────


def test_n8n_runtime_execute(tmp_path):
    """Execution triggers exec manager and returns success."""
    mock_exec = MagicMock()
    mock_exec.execute_workflow.return_value = {"id": "exec_999", "status": "success"}

    mgr = _make_runtime(tmp_path, exec_mgr=mock_exec)

    with patch.object(mgr, "generate_runtime_reports"):
        res = mgr.execute("wf_deploy_123", {"query": "hello"})

    assert res["success"] is True
    assert res["execution"]["id"] == "exec_999"


def test_n8n_runtime_execute_not_connected(tmp_path):
    """Execution returns error when server is not connected."""
    mgr = _make_runtime(tmp_path)
    mgr.exec_mgr = None

    res = mgr.execute("wf_no_conn")
    assert res["success"] is False
    assert "not connected" in res["message"]


# ── Lifecycle ────────────────────────────────────────────────────────────────


def test_n8n_runtime_lifecycle(tmp_path):
    """activate / deactivate / delete delegate to workflow manager."""
    mock_wf = MagicMock()
    mock_wf.activate_workflow.return_value = True
    mock_wf.deactivate_workflow.return_value = True
    mock_wf.delete_workflow.return_value = True

    mgr = _make_runtime(tmp_path, workflow_mgr=mock_wf)

    assert mgr.activate("wf_123") is True
    assert mgr.deactivate("wf_123") is True
    assert mgr.delete("wf_123") is True


def test_n8n_runtime_lifecycle_not_connected(tmp_path):
    """Returns False gracefully when workflow manager is None."""
    mgr = _make_runtime(tmp_path)
    mgr.workflow_mgr = None

    assert mgr.activate("wf_x") is False
    assert mgr.deactivate("wf_x") is False
    assert mgr.delete("wf_x") is False


# ── Rollback ─────────────────────────────────────────────────────────────────


def test_n8n_runtime_rollback_success(tmp_path):
    """Rollback restores an earlier version from history and appends a new entry."""
    mock_wf = MagicMock()
    mock_wf.update_workflow.return_value = {
        "id": "wf_123",
        "name": "Rollback Job",
        "nodes": [],
        "connections": {},
    }

    mgr = _make_runtime(tmp_path, workflow_mgr=mock_wf)
    mgr.history["wf_123"] = [
        {"version": 1, "timestamp": 10.0, "workflow": {"id": "wf_123", "name": "V1"}},
        {"version": 2, "timestamp": 20.0, "workflow": {"id": "wf_123", "name": "V2"}},
    ]

    with patch.object(mgr, "generate_runtime_reports"):
        res = mgr.rollback("wf_123", 1)

    assert res["success"] is True
    assert len(mgr.history["wf_123"]) == 3  # original 2 + new rollback entry


def test_n8n_runtime_rollback_missing_history(tmp_path):
    """Rollback fails when workflow has no deployment history."""
    mgr = _make_runtime(tmp_path)

    res = mgr.rollback("wf_unknown", 1)
    assert res["success"] is False
    assert "No deployment history" in res["message"]


def test_n8n_runtime_rollback_invalid_version(tmp_path):
    """Rollback fails when target version number does not exist."""
    mock_wf = MagicMock()
    mgr = _make_runtime(tmp_path, workflow_mgr=mock_wf)
    mgr.history["wf_123"] = [
        {"version": 1, "timestamp": 10.0, "workflow": {"id": "wf_123"}},
    ]

    res = mgr.rollback("wf_123", 99)
    assert res["success"] is False
    assert "Version 99 not found" in res["message"]


# ── Sync ─────────────────────────────────────────────────────────────────────


def test_n8n_runtime_sync_synchronized(tmp_path):
    """No drift when local and deployed nodes match."""
    mock_wf = MagicMock()
    mock_wf.list_workflows.return_value = [{"id": "wf_sync", "name": "Sync Job"}]
    mock_wf.get_workflow.return_value = {
        "id": "wf_sync",
        "nodes": [{"name": "A"}, {"name": "B"}],
    }

    mgr = _make_runtime(tmp_path, workflow_mgr=mock_wf)

    local_wf = {"name": "Sync Job", "nodes": [{"name": "A"}, {"name": "B"}]}
    res = mgr.sync(local_wf)

    assert res["drifted"] is False


def test_n8n_runtime_sync_drift(tmp_path):
    """Drift detected when node sets differ."""
    mock_wf = MagicMock()
    mock_wf.list_workflows.return_value = [{"id": "wf_sync", "name": "Sync Job"}]
    mock_wf.get_workflow.return_value = {
        "id": "wf_sync",
        "nodes": [{"name": "A"}, {"name": "B"}, {"name": "C"}],
    }

    mgr = _make_runtime(tmp_path, workflow_mgr=mock_wf)

    local_wf = {"name": "Sync Job", "nodes": [{"name": "A"}]}
    res = mgr.sync(local_wf)

    assert res["drifted"] is True
    assert "mismatch" in res["reason"]


def test_n8n_runtime_sync_not_deployed(tmp_path):
    """Drift reported when workflow not found on server."""
    mock_wf = MagicMock()
    mock_wf.list_workflows.return_value = []

    mgr = _make_runtime(tmp_path, workflow_mgr=mock_wf)

    res = mgr.sync({"name": "Ghost Job", "nodes": []})

    assert res["drifted"] is True


# ── Analytics ────────────────────────────────────────────────────────────────


def test_n8n_runtime_analytics(tmp_path):
    """Analytics derives success rate from executions list."""
    mock_exec = MagicMock()
    mock_exec.list_executions.return_value = [
        {"status": "success"},
        {"status": "success"},
        {"status": "failed"},
        {"status": "success"},
    ]

    mgr = _make_runtime(tmp_path, exec_mgr=mock_exec)
    analytics = mgr.get_analytics()

    assert analytics["total_executions"] == 4
    assert analytics["success_executions"] == 3
    assert analytics["failed_executions"] == 1
    assert abs(analytics["success_rate"] - 0.75) < 0.01


def test_n8n_runtime_analytics_no_connection(tmp_path):
    """Returns safe defaults when exec manager is None."""
    mgr = _make_runtime(tmp_path)
    mgr.exec_mgr = None

    analytics = mgr.get_analytics()
    assert analytics["total_executions"] == 0
    assert analytics["success_rate"] == 0.0


# ── Reports ───────────────────────────────────────────────────────────────────


def test_n8n_runtime_reports(tmp_path):
    """All six runtime report files are generated."""
    mock_exec = MagicMock()
    mock_exec.list_executions.return_value = [
        {"status": "success"},
        {"status": "failed"},
    ]

    report_dir = tmp_path / "docs" / "runtime"
    mgr = _make_runtime(tmp_path, exec_mgr=mock_exec)
    mgr.generate_runtime_reports(output_dir=str(report_dir))

    for fname in [
        "deployment_report.md",
        "execution_report.md",
        "failure_report.md",
        "runtime_analytics.md",
        "version_history.md",
        "synchronization_report.md",
    ]:
        assert (report_dir / fname).is_file(), f"Missing: {fname}"


# ── CLI commands ──────────────────────────────────────────────────────────────


def test_cli_workflow_runtime_commands(tmp_path):
    """All 10 new workflow runtime CLI sub-commands route correctly."""
    wf_payload = {"name": "CLI Job", "nodes": [], "connections": {}}
    local_wf_file = tmp_path / "local_workflow.json"
    local_wf_file.write_text(json.dumps(wf_payload), encoding="utf-8")

    mock_wf = MagicMock()
    mock_wf.list_workflows.return_value = []
    mock_wf.upload_workflow.return_value = {
        "id": "wf_cli_123",
        "name": "CLI Job",
        "nodes": [],
        "connections": {},
    }
    mock_wf.update_workflow.return_value = {
        "id": "wf_cli_123",
        "name": "CLI Job",
        "nodes": [],
        "connections": {},
    }
    mock_wf.activate_workflow.return_value = True
    mock_wf.deactivate_workflow.return_value = True
    mock_wf.delete_workflow.return_value = True

    mock_exec = MagicMock()
    mock_exec.execute_workflow.return_value = {"id": "exec_cli_1", "status": "success"}
    mock_exec.list_executions.return_value = []

    with (
        patch("aios.n8n.runtime.N8NLiveConnectionManager") as mock_conn,
        patch("aios.n8n.runtime.N8NWorkflowRuntimeManager._init_client", return_value=MagicMock()),
        patch("aios.n8n.runtime.N8NWorkflowManager", return_value=mock_wf),
        patch("aios.n8n.runtime.N8NExecutionManager", return_value=mock_exec),
        patch("sys.exit") as mock_exit,
    ):
        mock_conn_inst = MagicMock()
        mock_conn_inst.load_state.return_value = {
            "connected": True,
            "url": "http://localhost:5678",
        }
        mock_conn.return_value = mock_conn_inst

        def _patched_runtime(*args, **kwargs):
            mgr = N8NWorkflowRuntimeManager.__new__(N8NWorkflowRuntimeManager)
            mgr.conn_mgr = mock_conn_inst
            mgr.client = MagicMock()
            mgr.workflow_mgr = mock_wf
            mgr.exec_mgr = mock_exec
            mgr.history_file = tmp_path / "deployment_history.json"
            mgr.history = {}
            return mgr

        with patch("aios.n8n.runtime.N8NWorkflowRuntimeManager", side_effect=_patched_runtime):
            # 1. deploy
            execute_builtin_cli_command(
                ["workflow", "deploy", str(local_wf_file)], exit_on_complete=True
            )
            mock_exit.assert_called_with(0)

            # 2. update
            execute_builtin_cli_command(
                ["workflow", "update", "wf_cli_123", str(local_wf_file)], exit_on_complete=True
            )
            mock_exit.assert_called_with(0)

            # 3. execute
            execute_builtin_cli_command(
                ["workflow", "execute", "wf_cli_123"], exit_on_complete=True
            )
            mock_exit.assert_called_with(0)

            # 4. monitor
            execute_builtin_cli_command(["workflow", "monitor"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

            # 5. logs
            execute_builtin_cli_command(["workflow", "logs"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

            # 6. history — no records, should still exit 0
            execute_builtin_cli_command(
                ["workflow", "history", "wf_cli_123"], exit_on_complete=True
            )
            mock_exit.assert_called_with(0)

            # 7. rollback — no history so will exit 1 (failure path)
            execute_builtin_cli_command(
                ["workflow", "rollback", "wf_cli_123", "1"], exit_on_complete=True
            )

            # 8. enable / activate
            execute_builtin_cli_command(["workflow", "enable", "wf_cli_123"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

            # 9. disable / deactivate
            execute_builtin_cli_command(
                ["workflow", "disable", "wf_cli_123"], exit_on_complete=True
            )
            mock_exit.assert_called_with(0)

            # 10. delete
            execute_builtin_cli_command(["workflow", "delete", "wf_cli_123"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

            # 11. sync
            execute_builtin_cli_command(
                ["workflow", "sync", str(local_wf_file)], exit_on_complete=True
            )
            mock_exit.assert_called_with(0)
