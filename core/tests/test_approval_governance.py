import shutil
from unittest.mock import MagicMock, patch

import pytest
from aios.services.approval import ApprovalEngineService
from aios.services.approval_impl import ApprovalMiddleware, LocalApprovalEngineService


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture for temporary directory for approval stores and reports."""
    test_dir = tmp_path / "approval_test"
    test_dir.mkdir()
    yield test_dir
    if test_dir.exists():
        shutil.rmtree(test_dir)


def test_approval_middleware_routing(temp_dir):
    """Test middleware risk classification, policies resolution and queueing."""
    # Setup mock dependencies
    mock_memory = MagicMock()
    service = LocalApprovalEngineService(memory_service=mock_memory)
    service.base_dir = temp_dir
    service.initialize()
    service.start()

    middleware = ApprovalMiddleware(service)

    # 1. Test LOW risk auto-approve
    res_low = middleware.process_action(
        action="read_log",
        project="proj_1",
        client="c1",
        provider="github",
        details={"files": ["f1.log"], "changes": "read", "rollback": True},
    )
    assert res_low["status"] == "executed"
    assert res_low["token"].startswith("tok_")

    # 2. Test CRITICAL risk rejection (default policy critical level rejected)
    res_crit = middleware.process_action(
        action="storage_delete",
        project="proj_1",
        client="c1",
        provider="supabase",
        details={"files": [], "changes": "delete storage bucket", "rollback": False},
    )
    assert res_crit["status"] == "rejected"

    # 3. Test MEDIUM risk manual queued
    res_med = middleware.process_action(
        action="workflow_deploy",
        project="proj_1",
        client="c1",
        provider="n8n",
        details={"files": ["wf.json"], "changes": "deploy new wf", "rollback": True},
    )
    assert res_med["status"] == "queued"
    assert res_med["request_id"].startswith("req_")


def test_approval_service_extended_apis(temp_dir):
    """Test extended APIs for queue management, audit logging, and policy resolution."""
    mock_memory = MagicMock()
    service = LocalApprovalEngineService(memory_service=mock_memory)
    service.base_dir = temp_dir
    service.initialize()
    service.start()

    middleware = ApprovalMiddleware(service)
    res = middleware.process_action(
        action="production_deploy",
        project="proj_2",
        client="c2",
        provider="vercel",
        details={"changes": "deploy to prod", "rollback": True},
    )
    req_id = res["request_id"]

    # Verify queue list
    queue = service.list_queue()
    assert len(queue) == 1
    assert queue[0]["request_id"] == req_id
    assert queue[0]["status"] == "pending"

    # Verify pending list
    pending = service.list_pending()
    assert len(pending) == 1

    # Update policy
    service.update_policy("project:proj_2", "always_approve")
    assert service.resolve_policy("production_deploy", "proj_2", "c2") == "always_approve"

    # Generate preview
    preview = service.get_preview(req_id)
    assert preview["estimated_impact"] == "high"

    # Approve request
    assert service.approve_request(req_id) is True
    assert service.list_pending() == []

    # Execute request
    exec_res = service.execute_request(req_id)
    assert exec_res["status"] == "executed"

    # Audit log
    audit = service.list_audit_trail()
    assert len(audit) > 0


def test_approval_report_generation(temp_dir):
    """Test report compile outputting 5 markdown reports under docs/approval/."""
    mock_memory = MagicMock()
    service = LocalApprovalEngineService(memory_service=mock_memory)
    service.base_dir = temp_dir
    service.initialize()
    service.start()

    reports_dir = temp_dir / "reports"
    res = service.generate_reports(output_dir=reports_dir)

    assert res["reports_written"] == 5
    assert (reports_dir / "approval_report.md").is_file()
    assert (reports_dir / "audit_report.md").is_file()
    assert (reports_dir / "policy_report.md").is_file()
    assert (reports_dir / "risk_report.md").is_file()
    assert (reports_dir / "rollback_report.md").is_file()


def test_approval_cli_commands(temp_dir):
    """Test execute_builtin_cli_command routing for all 9 subcommands."""
    from aios.cli import execute_builtin_cli_command
    from aios.registry import ServiceRegistry

    mock_memory = MagicMock()
    service = LocalApprovalEngineService(memory_service=mock_memory)
    service.base_dir = temp_dir
    service.initialize()
    service.start()

    middleware = ApprovalMiddleware(service)
    res = middleware.process_action(
        action="production_deploy",
        project="proj_2",
        client="c2",
        provider="vercel",
        details={"changes": "deploy to prod", "rollback": True},
    )
    req_id = res["request_id"]

    registry = ServiceRegistry()
    registry.register(ApprovalEngineService, service)

    with patch("aios.registry.ServiceRegistry._global_registry", registry):
        assert execute_builtin_cli_command(["approval"], exit_on_complete=False)
        assert execute_builtin_cli_command(["approval", "queue"], exit_on_complete=False)
        assert execute_builtin_cli_command(["approval", "pending"], exit_on_complete=False)
        assert execute_builtin_cli_command(["approval", "policies"], exit_on_complete=False)
        assert execute_builtin_cli_command(["approval", "history"], exit_on_complete=False)
        assert execute_builtin_cli_command(["approval", "preview", req_id], exit_on_complete=False)
        assert execute_builtin_cli_command(["approval", "status", req_id], exit_on_complete=False)
        assert execute_builtin_cli_command(["approval", "approve", req_id], exit_on_complete=False)
        assert execute_builtin_cli_command(["approval", "reject", req_id], exit_on_complete=False)
        assert execute_builtin_cli_command(["approval", "cancel", req_id], exit_on_complete=False)
