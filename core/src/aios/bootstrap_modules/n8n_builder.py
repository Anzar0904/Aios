"""
bootstrap_modules/n8n_builder.py

Constructs and registers the self-hosted n8n platform:
  - Configuration, sessions, authentication, connections, client
  - Workflow, execution, credential, workspace, version, capability managers
  - Health monitoring, diagnostics, telemetries, validators, reports
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def build_n8n_platform(registry, n8n_integration_service):  # noqa: ANN001
    """Wire and register the self-hosted n8n components into *registry*."""
    from aios.n8n import (
        N8NAuthenticationManager,
        N8NCapabilityManager,
        N8NClient,
        N8NConfigurationService,
        N8NConnectionManager,
        N8NCredentialManager,
        N8NDiagnostics,
        N8NEventMonitor,
        N8NExecutionManager,
        N8NHealthMonitor,
        N8NReportGenerator,
        N8NSessionManager,
        N8NTelemetryCollector,
        N8NValidator,
        N8NVersionManager,
        N8NWorkflowManager,
        N8NWorkspaceManager,
    )

    n8n_config = N8NConfigurationService()
    n8n_session = N8NSessionManager(n8n_config)
    n8n_auth = N8NAuthenticationManager(n8n_config, n8n_session)
    n8n_conn = N8NConnectionManager(n8n_config, n8n_auth)
    n8n_client = N8NClient(n8n_conn, n8n_session)
    n8n_workflow = N8NWorkflowManager(n8n_client)
    n8n_execution = N8NExecutionManager(n8n_client)
    n8n_credential = N8NCredentialManager(n8n_client)
    n8n_workspace = N8NWorkspaceManager()
    n8n_version = N8NVersionManager(n8n_client)
    n8n_capability = N8NCapabilityManager(n8n_client)
    n8n_health = N8NHealthMonitor(
        n8n_client, n8n_auth, n8n_workflow, n8n_execution, n8n_version, n8n_capability
    )
    n8n_telemetry = N8NTelemetryCollector(n8n_health)
    n8n_event = N8NEventMonitor()
    n8n_validator = N8NValidator()
    n8n_diagnostics = N8NDiagnostics(n8n_config, n8n_auth, n8n_session)
    n8n_report = N8NReportGenerator(os.getcwd(), n8n_health, n8n_diagnostics)

    for svc in (
        n8n_config,
        n8n_session,
        n8n_auth,
        n8n_conn,
        n8n_client,
        n8n_workflow,
        n8n_execution,
        n8n_credential,
        n8n_workspace,
        n8n_health,
        n8n_version,
        n8n_capability,
        n8n_telemetry,
        n8n_event,
        n8n_validator,
        n8n_diagnostics,
        n8n_report,
    ):
        svc.initialize()

    registry.register(N8NConfigurationService, n8n_config)
    registry.register(N8NSessionManager, n8n_session)
    registry.register(N8NAuthenticationManager, n8n_auth)
    registry.register(N8NConnectionManager, n8n_conn)
    registry.register(N8NClient, n8n_client)
    registry.register(N8NWorkflowManager, n8n_workflow)
    registry.register(N8NExecutionManager, n8n_execution)
    registry.register(N8NCredentialManager, n8n_credential)
    registry.register(N8NWorkspaceManager, n8n_workspace)
    registry.register(N8NHealthMonitor, n8n_health)
    registry.register(N8NVersionManager, n8n_version)
    registry.register(N8NCapabilityManager, n8n_capability)
    registry.register(N8NTelemetryCollector, n8n_telemetry)
    registry.register(N8NEventMonitor, n8n_event)
    registry.register(N8NValidator, n8n_validator)
    registry.register(N8NDiagnostics, n8n_diagnostics)
    registry.register(N8NReportGenerator, n8n_report)

    # Wire to n8n integration health monitor
    n8n_integration_service._health_monitor._prod_health = n8n_health
