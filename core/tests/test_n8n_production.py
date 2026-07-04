import os
import time
import httpx
import pytest
from unittest.mock import MagicMock, patch

from aios.n8n import (
    N8NConfigurationService,
    N8NSessionManager,
    N8NAuthenticationManager,
    N8NConnectionManager,
    N8NClient,
    N8NWorkflowManager,
    N8NExecutionManager,
    N8NCredentialManager,
    N8NWorkspaceManager,
    N8NHealthMonitor,
    N8NVersionManager,
    N8NCapabilityManager,
    N8NTelemetryCollector,
    N8NEventMonitor,
    N8NValidator,
    N8NDiagnostics,
    N8NReportGenerator,
)


def test_n8n_production_auth_with_session():
    cfg = N8NConfigurationService()
    cfg.email = "admin@example.com"
    cfg.password = "secret"
    
    session = N8NSessionManager(cfg)
    auth = N8NAuthenticationManager(cfg, session)
    
    assert session.is_session_expired() is True
    diag = auth.validate_credentials()
    assert diag["valid"] is True

    with patch("httpx.Client.post") as mock_post:
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.cookies = {"n8n-auth": "auth_cookie_token_123"}
        mock_post.return_value = mock_resp

        assert session.login() is True
        assert session.session_cookie == "auth_cookie_token_123"
        assert session.is_session_expired() is False

        headers = auth.get_auth_headers()
        assert headers["Cookie"] == "n8n-auth=auth_cookie_token_123"


@patch("httpx.Client.request")
def test_n8n_production_client_request(mock_request):
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "ok"}
    mock_request.return_value = mock_resp

    cfg = N8NConfigurationService()
    session = N8NSessionManager(cfg)
    auth = N8NAuthenticationManager(cfg, session)
    conn = N8NConnectionManager(cfg, auth)
    client = N8NClient(conn, session)

    res = client.request("GET", "/healthz")
    assert res.json()["status"] == "ok"
    mock_request.assert_called_once()


@patch("httpx.Client.request")
def test_n8n_production_client_retry(mock_request):
    mock_fail = MagicMock(spec=httpx.Response)
    mock_fail.status_code = 500
    mock_fail.raise_for_status.side_effect = httpx.HTTPStatusError("Server Error", request=MagicMock(), response=mock_fail)

    mock_ok = MagicMock(spec=httpx.Response)
    mock_ok.status_code = 200
    mock_ok.json.return_value = {"status": "ok"}

    mock_request.side_effect = [mock_fail, mock_ok]

    cfg = N8NConfigurationService()
    cfg.max_retries = 2
    session = N8NSessionManager(cfg)
    auth = N8NAuthenticationManager(cfg, session)
    conn = N8NConnectionManager(cfg, auth)
    client = N8NClient(conn, session)

    res = client.request("GET", "/healthz")
    assert res.json()["status"] == "ok"
    assert mock_request.call_count == 2


@patch("httpx.Client.request")
def test_n8n_production_workflow_crud(mock_request):
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": "wf_123", "name": "Production Job"}
    mock_request.return_value = mock_resp

    cfg = N8NConfigurationService()
    session = N8NSessionManager(cfg)
    auth = N8NAuthenticationManager(cfg, session)
    conn = N8NConnectionManager(cfg, auth)
    client = N8NClient(conn, session)
    workflow_mgr = N8NWorkflowManager(client)

    res = workflow_mgr.upload_workflow("Production Job", [], {})
    assert res["id"] == "wf_123"
    assert res["name"] == "Production Job"

    # Test export / import wrappers
    exported = workflow_mgr.export_workflow("wf_123")
    assert exported["id"] == "wf_123"

    imported = workflow_mgr.import_workflow({"name": "Imported PR", "nodes": [], "connections": {}})
    assert imported["id"] == "wf_123"


@patch("httpx.Client.request")
def test_n8n_production_execution_polling(mock_request):
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": [{"id": "exec_456", "status": "success"}]}
    mock_request.return_value = mock_resp

    cfg = N8NConfigurationService()
    session = N8NSessionManager(cfg)
    auth = N8NAuthenticationManager(cfg, session)
    conn = N8NConnectionManager(cfg, auth)
    client = N8NClient(conn, session)
    exec_mgr = N8NExecutionManager(client)

    executions = exec_mgr.list_executions("wf_123")
    assert len(executions) == 1
    assert executions[0]["id"] == "exec_456"

    # Test retry/cancel execution
    mock_resp.json.return_value = {"status": "retrying"}
    res_retry = exec_mgr.retry_execution("exec_456")
    assert res_retry["status"] == "retrying"

    mock_resp.status_code = 200
    assert exec_mgr.cancel_execution("exec_456") is True


@patch("httpx.Client.request")
def test_n8n_production_health_monitor(mock_request):
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "ok", "version": "1.25.0", "data": []}
    mock_request.return_value = mock_resp

    cfg = N8NConfigurationService()
    session = N8NSessionManager(cfg)
    auth = N8NAuthenticationManager(cfg, session)
    conn = N8NConnectionManager(cfg, auth)
    client = N8NClient(conn, session)
    workflow_mgr = N8NWorkflowManager(client)
    exec_mgr = N8NExecutionManager(client)
    version = N8NVersionManager(client)
    caps = N8NCapabilityManager(client)
    health = N8NHealthMonitor(client, auth, workflow_mgr, exec_mgr, version, caps)

    res = health.check_health()
    assert res["status"] == "online"
    assert res["workflows_count"] == 0


def test_n8n_production_version_capability():
    cfg = N8NConfigurationService()
    session = N8NSessionManager(cfg)
    auth = N8NAuthenticationManager(cfg, session)
    conn = N8NConnectionManager(cfg, auth)
    client = N8NClient(conn, session)
    
    cap_mgr = N8NCapabilityManager(client)
    caps = cap_mgr.get_capabilities()
    assert "webhooks" in caps
    assert "oauth2" in caps


def test_n8n_production_diagnostics():
    cfg = N8NConfigurationService()
    session = N8NSessionManager(cfg)
    auth = N8NAuthenticationManager(cfg, session)
    diag = N8NDiagnostics(cfg, auth, session)
    res = diag.run_diagnostics()
    assert "diagnostics_status" in res or "status" in res


def test_n8n_production_report_generation(tmp_path):
    ws_root = str(tmp_path)
    mock_health = MagicMock()
    mock_health.client.connection_manager.config_service.server_url = "http://localhost:5678"
    mock_health.check_health.return_value = {
        "status": "online",
        "server_reachable": True,
        "authentication_successful": True,
        "server_version": "1.25.0",
        "workflows_count": 5,
        "executions_count": 10,
        "supported_capabilities": ["webhooks", "variables"],
        "latency_ms": 10.0,
        "average_response_time_ms": 12.0,
        "failure_rate": 0.0,
        "retry_statistics": {"total_retries": 0, "total_calls": 10}
    }
    
    mock_diag = MagicMock()
    mock_diag.run_diagnostics.return_value = {
        "status": "ok",
        "credentials_configured": True,
        "issues": []
    }
    
    reporter = N8NReportGenerator(ws_root, mock_health, mock_diag)
    reporter.generate_reports()

    assert os.path.exists(os.path.join(ws_root, "docs", "n8n", "N8N_RUNTIME_STATUS.md"))
    assert os.path.exists(os.path.join(ws_root, "docs", "n8n", "N8N_HEALTH.md"))
    assert os.path.exists(os.path.join(ws_root, "docs", "n8n", "N8N_SERVER_INFO.md"))
    assert os.path.exists(os.path.join(ws_root, "docs", "n8n", "N8N_EXECUTION_REPORT.md"))
    assert os.path.exists(os.path.join(ws_root, "docs", "n8n", "N8N_DIAGNOSTICS.md"))
