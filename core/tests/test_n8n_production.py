import os
import time
import httpx
import pytest
from unittest.mock import MagicMock, patch

from aios.n8n import (
    N8NConfigurationService,
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


def test_n8n_production_auth():
    cfg = N8NConfigurationService()
    cfg.auth_method = "bearer_token"
    cfg.bearer_token = "test-token"
    
    auth = N8NAuthenticationManager(cfg)
    headers = auth.get_auth_headers()
    assert headers["Authorization"] == "Bearer test-token"
    
    diag = auth.validate_credentials()
    assert diag["valid"] is True


@patch("httpx.Client.request")
def test_n8n_production_client_request(mock_request):
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "ok"}
    mock_request.return_value = mock_resp

    cfg = N8NConfigurationService()
    auth = N8NAuthenticationManager(cfg)
    conn = N8NConnectionManager(cfg, auth)
    client = N8NClient(conn)

    res = client.request("GET", "/healthz")
    assert res.json()["status"] == "ok"
    mock_request.assert_called_once_with("GET", "/healthz")


@patch("httpx.Client.request")
def test_n8n_production_client_retry(mock_request):
    # First request fails, second succeeds
    mock_fail = MagicMock(spec=httpx.Response)
    mock_fail.status_code = 500
    mock_fail.raise_for_status.side_effect = httpx.HTTPStatusError("Server Error", request=MagicMock(), response=mock_fail)

    mock_ok = MagicMock(spec=httpx.Response)
    mock_ok.status_code = 200
    mock_ok.json.return_value = {"status": "ok"}

    mock_request.side_effect = [mock_fail, mock_ok]

    cfg = N8NConfigurationService()
    cfg.max_retries = 2
    auth = N8NAuthenticationManager(cfg)
    conn = N8NConnectionManager(cfg, auth)
    client = N8NClient(conn)

    res = client.request("GET", "/healthz")
    assert res.json()["status"] == "ok"
    assert mock_request.call_count == 2


@patch("httpx.Client.request")
def test_n8n_production_workflow_crud(mock_request):
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": "wf_123", "name": "Sync Job"}
    mock_request.return_value = mock_resp

    cfg = N8NConfigurationService()
    auth = N8NAuthenticationManager(cfg)
    conn = N8NConnectionManager(cfg, auth)
    client = N8NClient(conn)
    workflow_mgr = N8NWorkflowManager(client)

    res = workflow_mgr.upload_workflow("Sync Job", [], {})
    assert res["id"] == "wf_123"
    assert res["name"] == "Sync Job"


@patch("httpx.Client.request")
def test_n8n_production_execution_polling(mock_request):
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": [{"id": "exec_456", "status": "success"}]}
    mock_request.return_value = mock_resp

    cfg = N8NConfigurationService()
    auth = N8NAuthenticationManager(cfg)
    conn = N8NConnectionManager(cfg, auth)
    client = N8NClient(conn)
    exec_mgr = N8NExecutionManager(client)

    executions = exec_mgr.list_executions("wf_123")
    assert len(executions) == 1
    assert executions[0]["id"] == "exec_456"


@patch("httpx.Client.request")
def test_n8n_production_health_monitor(mock_request):
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "ok", "version": "1.25.0", "data": []}
    mock_request.return_value = mock_resp

    cfg = N8NConfigurationService()
    auth = N8NAuthenticationManager(cfg)
    conn = N8NConnectionManager(cfg, auth)
    client = N8NClient(conn)
    workflow_mgr = N8NWorkflowManager(client)
    health = N8NHealthMonitor(client, auth, workflow_mgr)

    res = health.check_health()
    assert res["status"] == "online"
    assert res["workflows_count"] == 0


def test_n8n_production_version_capability():
    cap_mgr = N8NCapabilityManager()
    caps = cap_mgr.get_capabilities()
    assert "webhooks" in caps
    assert "oauth2" in caps


def test_n8n_production_diagnostics():
    cfg = N8NConfigurationService()
    auth = N8NAuthenticationManager(cfg)
    diag = N8NDiagnostics(auth)
    res = diag.run_diagnostics()
    assert "diagnostics_status" in res


def test_n8n_production_report_generation(tmp_path):
    ws_root = str(tmp_path)
    mock_health = MagicMock(spec=N8NHealthMonitor)
    reporter = N8NReportGenerator(ws_root, mock_health)
    reporter.generate_reports()

    assert os.path.exists(os.path.join(ws_root, "docs", "n8n", "N8N_STATUS.md"))
    assert os.path.exists(os.path.join(ws_root, "docs", "n8n", "N8N_HEALTH.md"))
    assert os.path.exists(os.path.join(ws_root, "docs", "n8n", "N8N_CONFIGURATION.md"))
    assert os.path.exists(os.path.join(ws_root, "docs", "n8n", "N8N_WORKFLOW_REPORT.md"))
    assert os.path.exists(os.path.join(ws_root, "docs", "n8n", "N8N_EXECUTION_REPORT.md"))
    assert os.path.exists(os.path.join(ws_root, "docs", "n8n", "N8N_DIAGNOSTICS.md"))
