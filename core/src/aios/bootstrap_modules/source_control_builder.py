"""
bootstrap_modules/source_control_builder.py

Constructs and registers the Source Control Intelligence platform:
  - Source Control registry and discovery
  - Git executors, repository/branch/commit/tag/merge managers
  - Pull Request, Issue, Release, Workflow, Webhook managers
  - Source Control telemetry, statistics, diagnostics, and reports
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def build_source_control_platform(registry, config):  # noqa: ANN001
    """Wire and register the Source Control components into *registry*."""
    from aios.source_control import (
        BranchManager,
        CommitManager,
        DiffManager,
        IssueManager,
        LocalGitExecutor,
        MergeManager,
        ProviderConfigurationService,
        ProviderDiagnostics,
        ProviderDiscovery,
        ProviderHealthMonitor,
        ProviderValidator,
        PullRequestManager,
        ReleaseManager,
        RepositoryManager,
        SourceControlRegistry,
        SourceControlReportGenerator,
        SourceControlService,
        SourceControlStatistics,
        SourceControlTelemetry,
        TagManager,
        WebhookManager,
        WorkflowManager,
        WorkspaceRepositoryManager,
    )

    sc_registry = SourceControlRegistry()
    sc_discovery = ProviderDiscovery(sc_registry)
    sc_discovery.discover_and_register()

    sc_config = ProviderConfigurationService()
    sc_health = ProviderHealthMonitor(sc_registry)
    sc_diagnostics = ProviderDiagnostics()
    sc_validator = ProviderValidator()

    source_control_service = SourceControlService(
        registry=sc_registry,
        config_service=sc_config,
        health_monitor=sc_health,
        diagnostics=sc_diagnostics,
        validator=sc_validator,
    )

    local_git = LocalGitExecutor()
    repo_mgr = RepositoryManager(source_control_service)
    branch_mgr = BranchManager(local_git)
    commit_mgr = CommitManager(local_git)
    tag_mgr = TagManager(local_git)
    merge_mgr = MergeManager(local_git)
    diff_mgr = DiffManager(local_git)
    workspace_repo_mgr = WorkspaceRepositoryManager(local_git)
    pr_mgr = PullRequestManager(source_control_service)
    issue_mgr = IssueManager(source_control_service)
    release_mgr = ReleaseManager(source_control_service)
    workflow_mgr = WorkflowManager(source_control_service)
    webhook_mgr = WebhookManager(source_control_service)

    sc_telemetry = SourceControlTelemetry()
    sc_statistics = SourceControlStatistics()
    sc_report = SourceControlReportGenerator(
        workspace_root=os.getcwd(),
        diagnostics=sc_diagnostics,
        health_monitor=sc_health,
        statistics=sc_statistics,
    )

    for svc in (
        sc_registry,
        sc_discovery,
        sc_config,
        sc_health,
        sc_diagnostics,
        sc_validator,
        source_control_service,
        local_git,
        repo_mgr,
        branch_mgr,
        commit_mgr,
        tag_mgr,
        merge_mgr,
        diff_mgr,
        workspace_repo_mgr,
        pr_mgr,
        issue_mgr,
        release_mgr,
        workflow_mgr,
        webhook_mgr,
        sc_telemetry,
        sc_statistics,
        sc_report,
    ):
        svc.initialize()

    registry.register(SourceControlRegistry, sc_registry)
    registry.register(ProviderDiscovery, sc_discovery)
    registry.register(ProviderConfigurationService, sc_config)
    registry.register(ProviderHealthMonitor, sc_health)
    registry.register(ProviderDiagnostics, sc_diagnostics)
    registry.register(ProviderValidator, sc_validator)
    registry.register(SourceControlService, source_control_service)
    registry.register(LocalGitExecutor, local_git)
    registry.register(RepositoryManager, repo_mgr)
    registry.register(BranchManager, branch_mgr)
    registry.register(CommitManager, commit_mgr)
    registry.register(TagManager, tag_mgr)
    registry.register(MergeManager, merge_mgr)
    registry.register(DiffManager, diff_mgr)
    registry.register(WorkspaceRepositoryManager, workspace_repo_mgr)
    registry.register(PullRequestManager, pr_mgr)
    registry.register(IssueManager, issue_mgr)
    registry.register(ReleaseManager, release_mgr)
    registry.register(WorkflowManager, workflow_mgr)
    registry.register(WebhookManager, webhook_mgr)
    registry.register(SourceControlTelemetry, sc_telemetry)
    registry.register(SourceControlStatistics, sc_statistics)
    registry.register(SourceControlReportGenerator, sc_report)
