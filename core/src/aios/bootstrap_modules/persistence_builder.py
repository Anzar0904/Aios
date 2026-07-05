"""
bootstrap_modules/persistence_builder.py

Constructs and registers the SQL persistence platform:
  - Core persistence (PostgreSQL + migrations)
  - Workspace repositories
  - Engineering memory repositories
  - Automation persistence repositories
  - AI memory persistence repositories
  - Runtime Intelligence platform
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def build_persistence_platform(registry, config_path):  # noqa: ANN001
    """Wire and register the full persistence platform into *registry*."""
    from aios.services.persistence import (
        AIMemoryPersistenceService,
        AIMemoryRepository,
        AIProviderRepository,
        AIUsageStatisticsRepository,
        ApprovalRepository,
        AutomationPersistenceService,
        AutomationStatisticsRepository,
        AutomationTelemetryRepository,
        ConfigurationRepository,
        DocumentationMetadataRepository,
        EngineeringMemoryService,
        EngineeringProfileRepository,
        EngineeringTaskRepository,
        PersistenceConfigurationService,
        PersistenceRegistry,
        PersistenceService,
        PlanningRepository,
        ProjectRepository,
        ProviderCapabilityRepository,
        ProviderCheckpointRepository,
        ProviderFailoverRepository,
        ProviderHealthRepository,
        ProviderQuotaRepository,
        ProviderRoutingRepository,
        ProviderSessionRepository,
        ProviderStatisticsRepository,
        ProviderTelemetryRepository,
        RepositoryRegistry,
        ReviewRepository,
        RuntimeIntelligenceService,
        TestResultRepository,
        TestSessionRepository,
        WorkflowExecutionRepository,
        WorkflowIntegrationRepository,
        WorkflowMonitoringRepository,
        WorkflowOptimizationRepository,
        WorkflowRepository,
        WorkflowTranslationRepository,
        WorkflowVersionRepository,
        WorkspacePersistenceService,
        WorkspaceRepository,
        WorkspaceSessionRepository,
    )
    from aios.services.persistence_impl import (
        AIMemoryHealthMonitor,
        AIMemoryPersistenceServiceImpl,
        AIMemoryReportGenerator,
        AIMemoryRepositoryImpl,
        AIMemoryStatistics,
        AIMemoryTelemetry,
        AIMemoryValidator,
        AIProviderRepositoryImpl,
        AIUsageStatisticsRepositoryImpl,
        ApprovalRepositoryImpl,
        AutomationPersistenceHealthMonitor,
        AutomationPersistenceReportGenerator,
        AutomationPersistenceServiceImpl,
        AutomationPersistenceStatistics,
        AutomationPersistenceTelemetry,
        AutomationPersistenceValidator,
        AutomationStatisticsRepositoryImpl,
        AutomationTelemetryRepositoryImpl,
        ConfigurationRepositoryImpl,
        DocumentationMetadataRepositoryImpl,
        EngineeringMemoryHealthMonitor,
        EngineeringMemoryReportGenerator,
        EngineeringMemoryServiceImpl,
        EngineeringMemoryStatistics,
        EngineeringMemoryTelemetry,
        EngineeringMemoryValidator,
        EngineeringProfileRepositoryImpl,
        EngineeringTaskRepositoryImpl,
        PersistenceBootstrapper,
        PersistenceDiagnostics,
        PersistenceHealthMonitor,
        PersistenceReportGenerator,
        PersistenceServiceImpl,
        PersistenceValidator,
        PlanningRepositoryImpl,
        PostgreSQLProvider,
        ProjectRepositoryImpl,
        ProviderCapabilityRepositoryImpl,
        ProviderCheckpointRepositoryImpl,
        ProviderFailoverRepositoryImpl,
        ProviderHealthRepositoryImpl,
        ProviderQuotaRepositoryImpl,
        ProviderRoutingRepositoryImpl,
        ProviderSessionRepositoryImpl,
        ProviderStatisticsRepositoryImpl,
        ProviderTelemetryRepositoryImpl,
        ReviewRepositoryImpl,
        RuntimeCapacityAnalyzer,
        RuntimeDiagnosticsEngine,
        RuntimeHealthMonitor,
        RuntimeIntelligenceServiceImpl,
        RuntimeLifecycleMonitor,
        RuntimePerformanceAnalyzer,
        RuntimeQueryProfiler,
        RuntimeRecommendationEngine,
        RuntimeReportGenerator,
        RuntimeRepositoryProfiler,
        RuntimeStatisticsEngine,
        RuntimeTelemetryCollector,
        RuntimeTransactionProfiler,
        TestResultRepositoryImpl,
        TestSessionRepositoryImpl,
        WorkflowExecutionRepositoryImpl,
        WorkflowIntegrationRepositoryImpl,
        WorkflowMonitoringRepositoryImpl,
        WorkflowOptimizationRepositoryImpl,
        WorkflowRepositoryImpl,
        WorkflowTranslationRepositoryImpl,
        WorkflowVersionRepositoryImpl,
        WorkspaceRepositoryImpl,
        WorkspaceSessionRepositoryImpl,
    )
    from aios.services.persistence_impl import (
        WorkspacePersistenceReportGenerator as WPReportGenerator,
    )
    from aios.services.persistence_impl import (
        WorkspacePersistenceServiceImpl as WPServiceImpl,
    )
    from aios.services.persistence_impl import (
        WorkspacePersistenceStatistics as WPStats,
    )
    from aios.services.persistence_impl import (
        WorkspacePersistenceTelemetry as WPTelemetry,
    )
    from aios.services.persistence_impl import (
        WorkspacePersistenceValidator as WPValidator,
    )

    # ── Core persistence ────────────────────────────────────────────────────
    p_config = PersistenceConfigurationService()
    p_registry = PersistenceRegistry()
    p_repos = RepositoryRegistry()
    p_registry.register_provider("postgresql", PostgreSQLProvider)
    p_service = PersistenceServiceImpl(p_config, p_registry, p_repos)
    p_health = PersistenceHealthMonitor(p_service)
    p_diagnostics = PersistenceDiagnostics(p_config, p_service)
    p_validator = PersistenceValidator()
    p_report = PersistenceReportGenerator(os.getcwd(), p_health, p_diagnostics)

    p_config.initialize()
    p_registry.initialize()
    p_repos.initialize()
    p_service.initialize()
    p_health.initialize()
    p_diagnostics.initialize()
    p_validator.initialize()
    p_report.initialize()

    p_service.on_ready()

    bootstrapper = PersistenceBootstrapper(p_service)
    bootstrapper.initialize()
    bootstrapper.on_ready()

    # ── Workspace repositories ───────────────────────────────────────────────
    workspace_repo = WorkspaceRepositoryImpl(p_service)
    session_repo = WorkspaceSessionRepositoryImpl(p_service)
    project_repo = ProjectRepositoryImpl(p_service)
    profile_repo = EngineeringProfileRepositoryImpl(p_service)
    config_repo = ConfigurationRepositoryImpl(p_service)

    p_repos.register_repository("workspaces", workspace_repo)
    p_repos.register_repository("workspace_sessions", session_repo)
    p_repos.register_repository("projects", project_repo)
    p_repos.register_repository("engineering_profiles", profile_repo)
    p_repos.register_repository("configuration_profiles", config_repo)

    wp_validator = WPValidator()
    wp_telemetry = WPTelemetry()
    wp_stats = WPStats(workspace_repo, session_repo)
    wp_service = WPServiceImpl(
        workspace_repo,
        session_repo,
        project_repo,
        profile_repo,
        config_repo,
        wp_validator,
        wp_telemetry,
        wp_stats,
    )
    wp_report = WPReportGenerator(
        os.getcwd(), wp_service, p_diagnostics, wp_telemetry, wp_stats, p_repos
    )
    wp_validator.initialize()
    wp_telemetry.initialize()
    wp_stats.initialize()
    wp_service.initialize()
    wp_report.initialize()

    registry.register(PersistenceConfigurationService, p_config)
    registry.register(PersistenceRegistry, p_registry)
    registry.register(RepositoryRegistry, p_repos)
    registry.register(PersistenceService, p_service)
    registry.register(PersistenceHealthMonitor, p_health)
    registry.register(PersistenceDiagnostics, p_diagnostics)
    registry.register(PersistenceValidator, p_validator)
    registry.register(PersistenceReportGenerator, p_report)
    registry.register(WorkspaceRepository, workspace_repo)
    registry.register(WorkspaceSessionRepository, session_repo)
    registry.register(ProjectRepository, project_repo)
    registry.register(EngineeringProfileRepository, profile_repo)
    registry.register(ConfigurationRepository, config_repo)
    registry.register(WorkspacePersistenceService, wp_service)
    registry.register(WPReportGenerator, wp_report)

    # ── Engineering memory repositories ────────────────────────────────────
    task_repo = EngineeringTaskRepositoryImpl(p_service)
    planning_repo = PlanningRepositoryImpl(p_service)
    approval_repo = ApprovalRepositoryImpl(p_service)
    review_repo = ReviewRepositoryImpl(p_service)
    doc_repo = DocumentationMetadataRepositoryImpl(p_service)
    test_session_repo = TestSessionRepositoryImpl(p_service)
    test_result_repo = TestResultRepositoryImpl(p_service)

    p_repos.register_repository("engineering_tasks", task_repo)
    p_repos.register_repository("planning_sessions", planning_repo)
    p_repos.register_repository("approval_sessions", approval_repo)
    p_repos.register_repository("review_sessions", review_repo)
    p_repos.register_repository("documentation_metadata", doc_repo)
    p_repos.register_repository("test_sessions", test_session_repo)
    p_repos.register_repository("test_results", test_result_repo)

    eng_validator = EngineeringMemoryValidator()
    eng_telemetry = EngineeringMemoryTelemetry()
    eng_stats = EngineeringMemoryStatistics(p_service)
    eng_health = EngineeringMemoryHealthMonitor(p_service, eng_telemetry, eng_stats)
    eng_report = EngineeringMemoryReportGenerator(os.getcwd(), eng_health)
    eng_memory_service = EngineeringMemoryServiceImpl(
        p_service,
        task_repo,
        planning_repo,
        approval_repo,
        review_repo,
        doc_repo,
        test_session_repo,
        test_result_repo,
        eng_validator,
        eng_telemetry,
        eng_stats,
        eng_health,
        eng_report,
    )

    for svc in (
        task_repo,
        planning_repo,
        approval_repo,
        review_repo,
        doc_repo,
        test_session_repo,
        test_result_repo,
        eng_validator,
        eng_telemetry,
        eng_stats,
        eng_health,
        eng_report,
        eng_memory_service,
    ):
        svc.initialize()

    registry.register(EngineeringTaskRepository, task_repo)
    registry.register(PlanningRepository, planning_repo)
    registry.register(ApprovalRepository, approval_repo)
    registry.register(ReviewRepository, review_repo)
    registry.register(DocumentationMetadataRepository, doc_repo)
    registry.register(TestSessionRepository, test_session_repo)
    registry.register(TestResultRepository, test_result_repo)
    registry.register(EngineeringMemoryValidator, eng_validator)
    registry.register(EngineeringMemoryTelemetry, eng_telemetry)
    registry.register(EngineeringMemoryStatistics, eng_stats)
    registry.register(EngineeringMemoryHealthMonitor, eng_health)
    registry.register(EngineeringMemoryReportGenerator, eng_report)
    registry.register(EngineeringMemoryService, eng_memory_service)

    # ── Automation persistence repositories ───────────────────────────────
    workflow_repo = WorkflowRepositoryImpl(p_service)
    execution_repo = WorkflowExecutionRepositoryImpl(p_service)
    monitor_repo = WorkflowMonitoringRepositoryImpl(p_service)
    optimization_repo = WorkflowOptimizationRepositoryImpl(p_service)
    version_repo = WorkflowVersionRepositoryImpl(p_service)
    translation_repo = WorkflowTranslationRepositoryImpl(p_service)
    integration_repo = WorkflowIntegrationRepositoryImpl(p_service)
    telemetry_repo = AutomationTelemetryRepositoryImpl(p_service)
    stats_repo = AutomationStatisticsRepositoryImpl(p_service)

    p_repos.register_repository("automation_workflows", workflow_repo)
    p_repos.register_repository("workflow_executions", execution_repo)
    p_repos.register_repository("workflow_monitoring", monitor_repo)
    p_repos.register_repository("workflow_optimizations", optimization_repo)
    p_repos.register_repository("workflow_versions", version_repo)
    p_repos.register_repository("workflow_translations", translation_repo)
    p_repos.register_repository("workflow_integrations", integration_repo)
    p_repos.register_repository("automation_statistics", stats_repo)

    aut_validator = AutomationPersistenceValidator()
    aut_telemetry = AutomationPersistenceTelemetry()
    aut_stats = AutomationPersistenceStatistics(p_service)
    aut_health = AutomationPersistenceHealthMonitor(p_service, aut_telemetry, aut_stats)
    aut_report = AutomationPersistenceReportGenerator(os.getcwd(), aut_health)
    aut_persistence_service = AutomationPersistenceServiceImpl(
        p_service,
        workflow_repo,
        execution_repo,
        monitor_repo,
        optimization_repo,
        version_repo,
        translation_repo,
        integration_repo,
        telemetry_repo,
        stats_repo,
        aut_validator,
        aut_telemetry,
        aut_stats,
        aut_health,
        aut_report,
    )

    for svc in (
        workflow_repo,
        execution_repo,
        monitor_repo,
        optimization_repo,
        version_repo,
        translation_repo,
        integration_repo,
        telemetry_repo,
        stats_repo,
        aut_validator,
        aut_telemetry,
        aut_stats,
        aut_health,
        aut_report,
        aut_persistence_service,
    ):
        svc.initialize()

    registry.register(WorkflowRepository, workflow_repo)
    registry.register(WorkflowExecutionRepository, execution_repo)
    registry.register(WorkflowMonitoringRepository, monitor_repo)
    registry.register(WorkflowOptimizationRepository, optimization_repo)
    registry.register(WorkflowVersionRepository, version_repo)
    registry.register(WorkflowTranslationRepository, translation_repo)
    registry.register(WorkflowIntegrationRepository, integration_repo)
    registry.register(AutomationTelemetryRepository, telemetry_repo)
    registry.register(AutomationStatisticsRepository, stats_repo)
    registry.register(AutomationPersistenceValidator, aut_validator)
    registry.register(AutomationPersistenceTelemetry, aut_telemetry)
    registry.register(AutomationPersistenceStatistics, aut_stats)
    registry.register(AutomationPersistenceHealthMonitor, aut_health)
    registry.register(AutomationPersistenceReportGenerator, aut_report)
    registry.register(AutomationPersistenceService, aut_persistence_service)

    # ── AI memory persistence repositories ────────────────────────────────
    ai_provider_repo = AIProviderRepositoryImpl(p_service)
    ai_cap_repo = ProviderCapabilityRepositoryImpl(p_service)
    ai_health_repo = ProviderHealthRepositoryImpl(p_service)
    ai_telem_repo = ProviderTelemetryRepositoryImpl(p_service)
    ai_stats_repo = ProviderStatisticsRepositoryImpl(p_service)
    ai_quota_repo = ProviderQuotaRepositoryImpl(p_service)
    ai_routing_repo = ProviderRoutingRepositoryImpl(p_service)
    ai_session_repo = ProviderSessionRepositoryImpl(p_service)
    ai_chk_repo = ProviderCheckpointRepositoryImpl(p_service)
    ai_failover_repo = ProviderFailoverRepositoryImpl(p_service)
    ai_usage_repo = AIUsageStatisticsRepositoryImpl(p_service)
    ai_mem_repo = AIMemoryRepositoryImpl(p_service)

    p_repos.register_repository("ai_providers", ai_provider_repo)
    p_repos.register_repository("provider_capabilities", ai_cap_repo)
    p_repos.register_repository("provider_health", ai_health_repo)
    p_repos.register_repository("provider_telemetry", ai_telem_repo)
    p_repos.register_repository("provider_statistics", ai_stats_repo)
    p_repos.register_repository("provider_quotas", ai_quota_repo)
    p_repos.register_repository("provider_routing", ai_routing_repo)
    p_repos.register_repository("provider_sessions", ai_session_repo)
    p_repos.register_repository("provider_checkpoints", ai_chk_repo)
    p_repos.register_repository("provider_failovers", ai_failover_repo)
    p_repos.register_repository("ai_usage_statistics", ai_usage_repo)
    p_repos.register_repository("ai_memory", ai_mem_repo)

    ai_validator = AIMemoryValidator()
    ai_telemetry = AIMemoryTelemetry()
    ai_stats_compiler = AIMemoryStatistics(p_service)
    ai_health_monitor = AIMemoryHealthMonitor(p_service, ai_telemetry, ai_stats_compiler)
    ai_report_generator = AIMemoryReportGenerator(os.getcwd(), ai_health_monitor)
    ai_persistence_service = AIMemoryPersistenceServiceImpl(
        p_service,
        ai_provider_repo,
        ai_cap_repo,
        ai_health_repo,
        ai_telem_repo,
        ai_stats_repo,
        ai_quota_repo,
        ai_routing_repo,
        ai_session_repo,
        ai_chk_repo,
        ai_failover_repo,
        ai_usage_repo,
        ai_mem_repo,
        ai_validator,
        ai_telemetry,
        ai_stats_compiler,
        ai_health_monitor,
        ai_report_generator,
    )

    for svc in (
        ai_provider_repo,
        ai_cap_repo,
        ai_health_repo,
        ai_telem_repo,
        ai_stats_repo,
        ai_quota_repo,
        ai_routing_repo,
        ai_session_repo,
        ai_chk_repo,
        ai_failover_repo,
        ai_usage_repo,
        ai_mem_repo,
        ai_validator,
        ai_telemetry,
        ai_stats_compiler,
        ai_health_monitor,
        ai_report_generator,
        ai_persistence_service,
    ):
        svc.initialize()

    registry.register(AIProviderRepository, ai_provider_repo)
    registry.register(ProviderCapabilityRepository, ai_cap_repo)
    registry.register(ProviderHealthRepository, ai_health_repo)
    registry.register(ProviderTelemetryRepository, ai_telem_repo)
    registry.register(ProviderStatisticsRepository, ai_stats_repo)
    registry.register(ProviderQuotaRepository, ai_quota_repo)
    registry.register(ProviderRoutingRepository, ai_routing_repo)
    registry.register(ProviderSessionRepository, ai_session_repo)
    registry.register(ProviderCheckpointRepository, ai_chk_repo)
    registry.register(ProviderFailoverRepository, ai_failover_repo)
    registry.register(AIUsageStatisticsRepository, ai_usage_repo)
    registry.register(AIMemoryRepository, ai_mem_repo)
    registry.register(AIMemoryValidator, ai_validator)
    registry.register(AIMemoryTelemetry, ai_telemetry)
    registry.register(AIMemoryStatistics, ai_stats_compiler)
    registry.register(AIMemoryHealthMonitor, ai_health_monitor)
    registry.register(AIMemoryReportGenerator, ai_report_generator)
    registry.register(AIMemoryPersistenceService, ai_persistence_service)

    # ── Runtime Intelligence platform ──────────────────────────────────────
    ri_telem = RuntimeTelemetryCollector()
    ri_perf = RuntimePerformanceAnalyzer(ri_telem)
    ri_capacity = RuntimeCapacityAnalyzer(ri_telem)
    ri_query_prof = RuntimeQueryProfiler()
    ri_tx_prof = RuntimeTransactionProfiler()
    ri_repo_prof = RuntimeRepositoryProfiler()
    ri_lifecycle = RuntimeLifecycleMonitor()
    ri_stats = RuntimeStatisticsEngine(p_service)
    ri_diag = RuntimeDiagnosticsEngine()
    ri_recommend = RuntimeRecommendationEngine(
        ri_telem, ri_perf, ri_capacity, ri_query_prof, ri_tx_prof, ri_repo_prof
    )
    ri_health = RuntimeHealthMonitor(p_service, ri_telem)
    ri_report = RuntimeReportGenerator(os.getcwd(), None)

    ri_service = RuntimeIntelligenceServiceImpl(
        ri_health,
        ri_telem,
        ri_stats,
        ri_diag,
        ri_capacity,
        ri_recommend,
        ri_perf,
        ri_query_prof,
        ri_tx_prof,
        ri_repo_prof,
        ri_lifecycle,
        ri_report,
    )
    ri_report.intelligence = ri_service
    p_service.ri_service = ri_service

    for svc in (
        ri_telem,
        ri_perf,
        ri_capacity,
        ri_query_prof,
        ri_tx_prof,
        ri_repo_prof,
        ri_lifecycle,
        ri_stats,
        ri_diag,
        ri_recommend,
        ri_health,
        ri_report,
        ri_service,
    ):
        svc.initialize()

    registry.register(RuntimeTelemetryCollector, ri_telem)
    registry.register(RuntimePerformanceAnalyzer, ri_perf)
    registry.register(RuntimeCapacityAnalyzer, ri_capacity)
    registry.register(RuntimeQueryProfiler, ri_query_prof)
    registry.register(RuntimeTransactionProfiler, ri_tx_prof)
    registry.register(RuntimeRepositoryProfiler, ri_repo_prof)
    registry.register(RuntimeLifecycleMonitor, ri_lifecycle)
    registry.register(RuntimeStatisticsEngine, ri_stats)
    registry.register(RuntimeDiagnosticsEngine, ri_diag)
    registry.register(RuntimeRecommendationEngine, ri_recommend)
    registry.register(RuntimeHealthMonitor, ri_health)
    registry.register(RuntimeReportGenerator, ri_report)
    registry.register(RuntimeIntelligenceService, ri_service)

    # Return key objects needed downstream
    return {
        "p_config": p_config,
        "p_repos": p_repos,
        "p_service": p_service,
        "p_diagnostics": p_diagnostics,
        "profile_repo": profile_repo,
        "ri_service": ri_service,
        "ri_telem": ri_telem,
    }
