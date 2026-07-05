import logging
import os
from pathlib import Path

from aios.kernel import Kernel
from aios.config import load_config

from aios.registry import ServiceRegistry
from aios.services.agent import AgentRuntimeService
from aios.services.agent_impl import CareerAgent, DeveloperAgent, LocalAgentRuntime, MockAgent
from aios.services.context import ContextService
from aios.services.context_impl import LocalContextService

# Interface imports
from aios.services.event_bus import EventBusService
from aios.services.github import GitHubService

# Concrete imports
from aios.services.event_bus_impl import LocalEventBus
from aios.services.github_impl import LocalGitHubService

from aios.services.intent import IntentResolverService
from aios.services.intent_impl import LocalIntentResolver
from aios.services.memory import MemoryService
from aios.services.memory_impl import LocalMemoryService
from aios.services.model import ModelService
from aios.services.model_impl import LocalModelService
from aios.services.session import SessionService
from aios.services.session_impl import LocalSessionService
from aios.services.tool import ToolService
from aios.services.tool_impl import LocalToolManager
from aios.services.project_intelligence import ProjectIntelligenceService
from aios.services.project_intelligence_impl import LocalProjectIntelligence
from aios.services.developer_workspace import DeveloperWorkspaceService
from aios.services.developer_workspace_impl import LocalDeveloperWorkspace
from aios.services.research import ResearchService
from aios.services.research_impl import LocalResearchService
from aios.services.n8n import N8NService
from aios.services.n8n_impl import LocalN8NService
from aios.services.personal import PersonalService
from aios.services.personal_impl import LocalPersonalService
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.knowledge_hub_impl import LocalKnowledgeHub

from aios.services.command import CommandRegistry
from aios.services.orchestrator import OrchestratorService
from aios.services.orchestrator_impl import LocalOrchestratorService
from aios.services.agent import AgentRegistry, LocalAgentManager
from aios.services.mission import MissionEngine
from aios.services.mission_impl import LocalMissionEngine
from aios.services.runtime import RuntimeService
from aios.services.runtime_impl import LocalRuntime
from aios.services.reasoning import ReasoningService
from aios.services.reasoning_impl import LocalReasoningService










logger = logging.getLogger(__name__)

def bootstrap_kernel(config_path: Path) -> Kernel:
    """
    Composition Root for Personal AI OS.
    Constructs, wires, and registers all concrete services.
    Returns a configured Kernel instance.
    """
    logger.info("Bootstrapping AI OS system (Composition Root)...")

    # 1. Initialize Registry
    registry = ServiceRegistry()
    config = load_config(Path(config_path))

    # 2. Construct services and wire dependencies

    event_bus = LocalEventBus()

    # Wire and register the Persistence Platform components
    from aios.services.persistence import (
        PersistenceConfigurationService,
        PersistenceRegistry,
        RepositoryRegistry,
        PersistenceService,
        WorkspaceRepository,
        WorkspaceSessionRepository,
        ProjectRepository,
        EngineeringProfileRepository,
        ConfigurationRepository,
        WorkspacePersistenceService,
        EngineeringTaskRepository,
        PlanningRepository,
        ApprovalRepository,
        ReviewRepository,
        DocumentationMetadataRepository,
        TestSessionRepository,
        TestResultRepository,
        EngineeringMemoryService,
        WorkflowRepository,
        WorkflowExecutionRepository,
        WorkflowMonitoringRepository,
        WorkflowOptimizationRepository,
        WorkflowVersionRepository,
        WorkflowTranslationRepository,
        WorkflowIntegrationRepository,
        AutomationTelemetryRepository,
        AutomationStatisticsRepository,
        AutomationPersistenceService,
        AIProviderRepository,
        ProviderCapabilityRepository,
        ProviderHealthRepository,
        ProviderTelemetryRepository,
        ProviderStatisticsRepository,
        ProviderQuotaRepository,
        ProviderRoutingRepository,
        ProviderSessionRepository,
        ProviderCheckpointRepository,
        ProviderFailoverRepository,
        AIUsageStatisticsRepository,
        AIMemoryRepository,
        AIMemoryPersistenceService,
        RuntimeIntelligenceService,
        RedisTransport,
        RedisProvider,
        RedisRuntimeService,
        CachePolicy,
        CachePolicyManager,
        CacheInvalidationManager,
        CacheWarmupService,
        CacheRebuildService,
        CacheStatisticsCollector,
        CacheHealthMonitor,
        CacheDiagnostics,
        CacheRecommendationEngine,
        RedisCacheService,
        SessionPolicy,
        SessionRegistry,
        SessionExpirationManager,
        SessionRecoveryManager,
        SessionStatisticsCollector,
        SessionHealthMonitor,
        SessionDiagnostics,
        SessionRecommendationEngine,
        SessionStore,
        SessionManager,
        RedisSessionService,
        LockPolicy,
        LockRegistry,
        LockLeaseManager,
        LockRecoveryManager,
        DeadlockDetector,
        MutexManager,
        CoordinationStatisticsCollector,
        CoordinationHealthMonitor,
        CoordinationDiagnostics,
        CoordinationRecommendationEngine,
        DistributedLockManager,
        RedisCoordinationService,
        QueuePriority,
        QueueRegistry,
        QueueManager,
        PriorityQueueManager,
        DelayedQueueManager,
        RetryQueueManager,
        QueueScheduler,
        QueueWorkerCoordinator,
        QueueRecoveryManager,
        QueueStatisticsCollector,
        QueueHealthMonitor,
        QueueDiagnostics,
        QueueRecommendationEngine,
        RedisQueueService,
    )
    from aios.services.persistence_impl import (
        PostgreSQLProvider,
        PersistenceServiceImpl,
        PersistenceHealthMonitor,
        PersistenceDiagnostics,
        PersistenceValidator,
        PersistenceReportGenerator,
        WorkspaceRepositoryImpl,
        WorkspaceSessionRepositoryImpl,
        ProjectRepositoryImpl,
        EngineeringProfileRepositoryImpl,
        ConfigurationRepositoryImpl,
        WorkspacePersistenceValidator as WPValidator,
        WorkspacePersistenceTelemetry as WPTelemetry,
        WorkspacePersistenceStatistics as WPStats,
        WorkspacePersistenceServiceImpl as WPServiceImpl,
        WorkspacePersistenceReportGenerator as WPReportGenerator,
        PersistenceBootstrapper,
        EngineeringTaskRepositoryImpl,
        PlanningRepositoryImpl,
        ApprovalRepositoryImpl,
        ReviewRepositoryImpl,
        DocumentationMetadataRepositoryImpl,
        TestSessionRepositoryImpl,
        TestResultRepositoryImpl,
        EngineeringMemoryValidator,
        EngineeringMemoryTelemetry,
        EngineeringMemoryStatistics,
        EngineeringMemoryHealthMonitor,
        EngineeringMemoryReportGenerator,
        EngineeringMemoryServiceImpl,
        WorkflowRepositoryImpl,
        WorkflowExecutionRepositoryImpl,
        WorkflowMonitoringRepositoryImpl,
        WorkflowOptimizationRepositoryImpl,
        WorkflowVersionRepositoryImpl,
        WorkflowTranslationRepositoryImpl,
        WorkflowIntegrationRepositoryImpl,
        AutomationTelemetryRepositoryImpl,
        AutomationStatisticsRepositoryImpl,
        AutomationPersistenceValidator,
        AutomationPersistenceTelemetry,
        AutomationPersistenceStatistics,
        AutomationPersistenceHealthMonitor,
        AutomationPersistenceReportGenerator,
        AutomationPersistenceServiceImpl,
        AIProviderRepositoryImpl,
        ProviderCapabilityRepositoryImpl,
        ProviderHealthRepositoryImpl,
        ProviderTelemetryRepositoryImpl,
        ProviderStatisticsRepositoryImpl,
        ProviderQuotaRepositoryImpl,
        ProviderRoutingRepositoryImpl,
        ProviderSessionRepositoryImpl,
        ProviderCheckpointRepositoryImpl,
        ProviderFailoverRepositoryImpl,
        AIUsageStatisticsRepositoryImpl,
        AIMemoryRepositoryImpl,
        AIMemoryValidator,
        AIMemoryTelemetry,
        AIMemoryStatistics,
        AIMemoryHealthMonitor,
        AIMemoryReportGenerator,
        AIMemoryPersistenceServiceImpl,
        RuntimeIntelligenceServiceImpl,
        RuntimeHealthMonitor,
        RuntimeTelemetryCollector,
        RuntimeStatisticsEngine,
        RuntimeDiagnosticsEngine,
        RuntimeCapacityAnalyzer,
        RuntimeRecommendationEngine,
        RuntimePerformanceAnalyzer,
        RuntimeQueryProfiler,
        RuntimeTransactionProfiler,
        RuntimeRepositoryProfiler,
        RuntimeLifecycleMonitor,
        RuntimeCorrelationManager,
        RuntimeReportGenerator,
        RedisConfigurationService,
        RedisConnectionManager,
        RedisTransportImpl,
        RedisProviderImpl,
        RedisTelemetry,
        RedisStatistics,
        RedisDiagnostics,
        RedisHealthMonitor,
        RedisValidator,
        RedisReportGenerator,
        RedisRuntimeServiceImpl,
        CachePolicyManagerImpl,
        CacheStatisticsCollectorImpl,
        CacheDiagnosticsImpl,
        CacheHealthMonitorImpl,
        CacheRecommendationEngineImpl,
        CacheInvalidationManagerImpl,
        CacheWarmupServiceImpl,
        CacheRebuildServiceImpl,
        RedisCacheServiceImpl,
        SessionRegistryImpl,
        SessionStatisticsCollectorImpl,
        SessionDiagnosticsImpl,
        SessionHealthMonitorImpl,
        SessionRecommendationEngineImpl,
        SessionStoreImpl,
        SessionExpirationManagerImpl,
        SessionRecoveryManagerImpl,
        SessionManagerImpl,
        RedisSessionServiceImpl,
        LockRegistryImpl,
        DeadlockDetectorImpl,
        CoordinationStatisticsCollectorImpl,
        CoordinationDiagnosticsImpl,
        CoordinationHealthMonitorImpl,
        CoordinationRecommendationEngineImpl,
        LockLeaseManagerImpl,
        LockRecoveryManagerImpl,
        MutexManagerImpl,
        DistributedLockManagerImpl,
        RedisCoordinationServiceImpl,
        QueueRegistryImpl,
        QueueStatisticsCollectorImpl,
        QueueDiagnosticsImpl,
        QueueHealthMonitorImpl,
        QueueRecommendationEngineImpl,
        PriorityQueueManagerImpl,
        DelayedQueueManagerImpl,
        RetryQueueManagerImpl,
        QueueSchedulerImpl,
        QueueWorkerCoordinatorImpl,
        QueueRecoveryManagerImpl,
        QueueManagerImpl,
        RedisQueueServiceImpl,
    )

    p_config = PersistenceConfigurationService()
    p_registry = PersistenceRegistry()
    p_repos = RepositoryRegistry()
    
    # Register postgreSQL provider class in registry
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

    # Run connect so we can migrate
    p_service.on_ready()

    # Run bootstrapper migrations
    bootstrapper = PersistenceBootstrapper(p_service)
    bootstrapper.initialize()
    bootstrapper.on_ready()

    # Instantiate Repositories
    workspace_repo = WorkspaceRepositoryImpl(p_service)
    session_repo = WorkspaceSessionRepositoryImpl(p_service)
    project_repo = ProjectRepositoryImpl(p_service)
    profile_repo = EngineeringProfileRepositoryImpl(p_service)
    config_repo = ConfigurationRepositoryImpl(p_service)

    # Register repositories
    p_repos.register_repository("workspaces", workspace_repo)
    p_repos.register_repository("workspace_sessions", session_repo)
    p_repos.register_repository("projects", project_repo)
    p_repos.register_repository("engineering_profiles", profile_repo)
    p_repos.register_repository("configuration_profiles", config_repo)

    # Instantiate workspace services
    wp_validator = WPValidator()
    wp_telemetry = WPTelemetry()
    wp_stats = WPStats(workspace_repo, session_repo)
    wp_service = WPServiceImpl(
        workspace_repo, session_repo, project_repo, profile_repo, config_repo,
        wp_validator, wp_telemetry, wp_stats
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

    # Instantiate Engineering Memory Repositories
    task_repo = EngineeringTaskRepositoryImpl(p_service)
    planning_repo = PlanningRepositoryImpl(p_service)
    approval_repo = ApprovalRepositoryImpl(p_service)
    review_repo = ReviewRepositoryImpl(p_service)
    doc_repo = DocumentationMetadataRepositoryImpl(p_service)
    test_session_repo = TestSessionRepositoryImpl(p_service)
    test_result_repo = TestResultRepositoryImpl(p_service)

    # Register in RepositoryRegistry
    p_repos.register_repository("engineering_tasks", task_repo)
    p_repos.register_repository("planning_sessions", planning_repo)
    p_repos.register_repository("approval_sessions", approval_repo)
    p_repos.register_repository("review_sessions", review_repo)
    p_repos.register_repository("documentation_metadata", doc_repo)
    p_repos.register_repository("test_sessions", test_session_repo)
    p_repos.register_repository("test_results", test_result_repo)

    # Instantiate auxiliary services
    eng_validator = EngineeringMemoryValidator()
    eng_telemetry = EngineeringMemoryTelemetry()
    eng_stats = EngineeringMemoryStatistics(p_service)
    eng_health = EngineeringMemoryHealthMonitor(p_service, eng_telemetry, eng_stats)
    eng_report = EngineeringMemoryReportGenerator(os.getcwd(), eng_health)

    # Instantiate core EngineeringMemoryServiceImpl
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
        eng_report
    )

    # Initialize all of them
    task_repo.initialize()
    planning_repo.initialize()
    approval_repo.initialize()
    review_repo.initialize()
    doc_repo.initialize()
    test_session_repo.initialize()
    test_result_repo.initialize()

    eng_validator.initialize()
    eng_telemetry.initialize()
    eng_stats.initialize()
    eng_health.initialize()
    eng_report.initialize()
    eng_memory_service.initialize()

    # Register in DI container
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

    # Instantiate Automation Persistence Repositories
    workflow_repo = WorkflowRepositoryImpl(p_service)
    execution_repo = WorkflowExecutionRepositoryImpl(p_service)
    monitor_repo = WorkflowMonitoringRepositoryImpl(p_service)
    optimization_repo = WorkflowOptimizationRepositoryImpl(p_service)
    version_repo = WorkflowVersionRepositoryImpl(p_service)
    translation_repo = WorkflowTranslationRepositoryImpl(p_service)
    integration_repo = WorkflowIntegrationRepositoryImpl(p_service)
    telemetry_repo = AutomationTelemetryRepositoryImpl(p_service)
    stats_repo = AutomationStatisticsRepositoryImpl(p_service)

    # Register in RepositoryRegistry
    p_repos.register_repository("automation_workflows", workflow_repo)
    p_repos.register_repository("workflow_executions", execution_repo)
    p_repos.register_repository("workflow_monitoring", monitor_repo)
    p_repos.register_repository("workflow_optimizations", optimization_repo)
    p_repos.register_repository("workflow_versions", version_repo)
    p_repos.register_repository("workflow_translations", translation_repo)
    p_repos.register_repository("workflow_integrations", integration_repo)
    p_repos.register_repository("automation_statistics", stats_repo)

    # Instantiate auxiliary services
    aut_validator = AutomationPersistenceValidator()
    aut_telemetry = AutomationPersistenceTelemetry()
    aut_stats = AutomationPersistenceStatistics(p_service)
    aut_health = AutomationPersistenceHealthMonitor(p_service, aut_telemetry, aut_stats)
    aut_report = AutomationPersistenceReportGenerator(os.getcwd(), aut_health)

    # Instantiate core AutomationPersistenceServiceImpl
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
        aut_report
    )

    # Initialize all of them
    workflow_repo.initialize()
    execution_repo.initialize()
    monitor_repo.initialize()
    optimization_repo.initialize()
    version_repo.initialize()
    translation_repo.initialize()
    integration_repo.initialize()
    telemetry_repo.initialize()
    stats_repo.initialize()

    aut_validator.initialize()
    aut_telemetry.initialize()
    aut_stats.initialize()
    aut_health.initialize()
    aut_report.initialize()
    aut_persistence_service.initialize()

    # Register in DI container
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

    # Instantiate AI Memory Persistence Repositories
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

    # Register in RepositoryRegistry
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

    # Instantiate auxiliary services
    ai_validator = AIMemoryValidator()
    ai_telemetry = AIMemoryTelemetry()
    ai_stats_compiler = AIMemoryStatistics(p_service)
    ai_health_monitor = AIMemoryHealthMonitor(p_service, ai_telemetry, ai_stats_compiler)
    ai_report_generator = AIMemoryReportGenerator(os.getcwd(), ai_health_monitor)

    # Instantiate core AIMemoryPersistenceServiceImpl
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
        ai_report_generator
    )

    # Initialize all of them
    ai_provider_repo.initialize()
    ai_cap_repo.initialize()
    ai_health_repo.initialize()
    ai_telem_repo.initialize()
    ai_stats_repo.initialize()
    ai_quota_repo.initialize()
    ai_routing_repo.initialize()
    ai_session_repo.initialize()
    ai_chk_repo.initialize()
    ai_failover_repo.initialize()
    ai_usage_repo.initialize()
    ai_mem_repo.initialize()

    ai_validator.initialize()
    ai_telemetry.initialize()
    ai_stats_compiler.initialize()
    ai_health_monitor.initialize()
    ai_report_generator.initialize()
    ai_persistence_service.initialize()

    # Register in DI container
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

    # Instantiate Runtime Intelligence auxiliary classes
    ri_telem = RuntimeTelemetryCollector()
    ri_perf = RuntimePerformanceAnalyzer(ri_telem)
    ri_capacity = RuntimeCapacityAnalyzer(ri_telem)
    ri_query_prof = RuntimeQueryProfiler()
    ri_tx_prof = RuntimeTransactionProfiler()
    ri_repo_prof = RuntimeRepositoryProfiler()
    ri_lifecycle = RuntimeLifecycleMonitor()
    ri_stats = RuntimeStatisticsEngine(p_service)
    ri_diag = RuntimeDiagnosticsEngine()
    ri_recommend = RuntimeRecommendationEngine(ri_telem, ri_perf, ri_capacity, ri_query_prof, ri_tx_prof, ri_repo_prof)
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
        ri_report
    )
    ri_report.intelligence = ri_service

    # Inject ri_service reference into the main persistence service
    p_service.ri_service = ri_service

    # Initialize all Runtime Intelligence classes
    ri_telem.initialize()
    ri_perf.initialize()
    ri_capacity.initialize()
    ri_query_prof.initialize()
    ri_tx_prof.initialize()
    ri_repo_prof.initialize()
    ri_lifecycle.initialize()
    ri_stats.initialize()
    ri_diag.initialize()
    ri_recommend.initialize()
    ri_health.initialize()
    ri_report.initialize()
    ri_service.initialize()

    # Register in DI container
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

    # Instantiate Redis Platform foundation classes
    redis_cfg = RedisConfigurationService()
    redis_conn = RedisConnectionManager(redis_cfg)
    redis_transport = RedisTransportImpl(redis_cfg, redis_conn)
    redis_provider = RedisProviderImpl(redis_transport)
    redis_telem = RedisTelemetry()
    redis_stats = RedisStatistics(redis_telem)
    redis_diag = RedisDiagnostics(redis_conn)
    redis_health = RedisHealthMonitor(redis_transport)
    redis_validator = RedisValidator()
    redis_report = RedisReportGenerator(os.getcwd(), None)

    redis_service = RedisRuntimeServiceImpl(
        redis_cfg,
        redis_transport,
        redis_provider,
        redis_health,
        redis_diag,
        redis_telem,
        redis_stats,
        redis_validator,
        redis_report
    )
    redis_report.runtime_service = redis_service

    # Initialize all Redis Platform classes
    redis_cfg.initialize()
    redis_conn.initialize()
    redis_transport.initialize()
    redis_provider.initialize()
    redis_telem.initialize()
    redis_stats.initialize()
    redis_diag.initialize()
    redis_health.initialize()
    redis_validator.initialize()
    redis_report.initialize()
    redis_service.initialize()

    # Instantiate Runtime Cache Platform classes
    cache_policy_mgr = CachePolicyManagerImpl()
    cache_stats = CacheStatisticsCollectorImpl()
    cache_diag = CacheDiagnosticsImpl(redis_provider)
    cache_health = CacheHealthMonitorImpl(redis_provider)
    cache_recommend = CacheRecommendationEngineImpl(cache_stats, cache_diag)
    cache_inval = CacheInvalidationManagerImpl(redis_provider, cache_stats)
    redis_cache_service = RedisCacheServiceImpl(
        redis_provider,
        cache_policy_mgr,
        cache_stats,
        cache_diag
    )
    cache_warmup = CacheWarmupServiceImpl(p_service, redis_cache_service, cache_stats)
    cache_rebuild = CacheRebuildServiceImpl(p_service, redis_provider, cache_stats, cache_warmup)

    # Initialize all Runtime Cache classes
    cache_policy_mgr.initialize()
    cache_stats.initialize()
    cache_diag.initialize()
    cache_health.initialize()
    cache_recommend.initialize()
    cache_inval.initialize()
    redis_cache_service.initialize()
    cache_warmup.initialize()
    cache_rebuild.initialize()

    # Trigger Startup Cache Warmup in background
    cache_warmup.warmup_all_background()

    # Register in DI container
    registry.register(RedisConfigurationService, redis_cfg)
    registry.register(RedisConnectionManager, redis_conn)
    registry.register(RedisTransport, redis_transport)
    registry.register(RedisProvider, redis_provider)
    registry.register(RedisTelemetry, redis_telem)
    registry.register(RedisStatistics, redis_stats)
    registry.register(RedisDiagnostics, redis_diag)
    registry.register(RedisHealthMonitor, redis_health)
    registry.register(RedisValidator, redis_validator)
    registry.register(RedisReportGenerator, redis_report)
    registry.register(RedisRuntimeService, redis_service)

    registry.register(CachePolicyManager, cache_policy_mgr)
    registry.register(CacheStatisticsCollector, cache_stats)
    registry.register(CacheDiagnostics, cache_diag)
    registry.register(CacheHealthMonitor, cache_health)
    registry.register(CacheRecommendationEngine, cache_recommend)
    registry.register(CacheInvalidationManager, cache_inval)
    registry.register(CacheWarmupService, cache_warmup)
    registry.register(CacheRebuildService, cache_rebuild)
    registry.register(RedisCacheService, redis_cache_service)

    # Instantiate Runtime Session Platform classes
    session_registry = SessionRegistryImpl()
    session_stats = SessionStatisticsCollectorImpl()
    session_diag = SessionDiagnosticsImpl(redis_provider)
    session_health = SessionHealthMonitorImpl(redis_provider)
    session_recommend = SessionRecommendationEngineImpl(session_stats, session_diag)
    session_store = SessionStoreImpl(
        redis_provider,
        session_registry,
        session_stats,
        session_diag
    )
    session_expiration = SessionExpirationManagerImpl(session_store, session_registry)
    session_recovery = SessionRecoveryManagerImpl(p_service, redis_provider, session_stats)
    session_manager = SessionManagerImpl(
        session_store,
        session_recovery,
        session_registry,
        session_stats
    )
    redis_session_service = RedisSessionServiceImpl(
        redis_provider,
        session_registry,
        session_store,
        session_manager,
        session_stats,
        session_diag
    )

    # Initialize all Runtime Session classes
    session_registry.initialize()
    session_stats.initialize()
    session_diag.initialize()
    session_health.initialize()
    session_recommend.initialize()
    session_store.initialize()
    session_expiration.initialize()
    session_recovery.initialize()
    session_manager.initialize()
    redis_session_service.initialize()

    # Register Session Platform in DI container
    registry.register(SessionRegistry, session_registry)
    registry.register(SessionStatisticsCollector, session_stats)
    registry.register(SessionDiagnostics, session_diag)
    registry.register(SessionHealthMonitor, session_health)
    registry.register(SessionRecommendationEngine, session_recommend)
    registry.register(SessionStore, session_store)
    registry.register(SessionExpirationManager, session_expiration)
    registry.register(SessionRecoveryManager, session_recovery)
    registry.register(SessionManager, session_manager)
    registry.register(RedisSessionService, redis_session_service)

    # Instantiate Distributed Coordination Platform classes
    lock_registry = LockRegistryImpl()
    deadlock_detector = DeadlockDetectorImpl()
    coord_stats = CoordinationStatisticsCollectorImpl()
    coord_diag = CoordinationDiagnosticsImpl(redis_provider)
    coord_health = CoordinationHealthMonitorImpl(redis_provider)
    coord_recommend = CoordinationRecommendationEngineImpl(coord_stats, coord_diag)
    lock_lease_mgr = LockLeaseManagerImpl(
        redis_provider,
        lock_registry,
        deadlock_detector,
        coord_stats,
        coord_diag
    )
    lock_recovery_mgr = LockRecoveryManagerImpl(coord_stats)
    mutex_mgr = MutexManagerImpl(lock_lease_mgr, coord_stats)
    dist_lock_mgr = DistributedLockManagerImpl(
        lock_lease_mgr,
        deadlock_detector,
        coord_stats
    )
    redis_coordination_service = RedisCoordinationServiceImpl(
        redis_provider,
        lock_registry,
        lock_lease_mgr,
        dist_lock_mgr
    )

    # Initialize all Distributed Coordination classes
    lock_registry.initialize()
    deadlock_detector.initialize()
    coord_stats.initialize()
    coord_diag.initialize()
    coord_health.initialize()
    coord_recommend.initialize()
    lock_lease_mgr.initialize()
    lock_recovery_mgr.initialize()
    mutex_mgr.initialize()
    dist_lock_mgr.initialize()
    redis_coordination_service.initialize()

    # Register Coordination Platform in DI container
    registry.register(LockRegistry, lock_registry)
    registry.register(DeadlockDetector, deadlock_detector)
    registry.register(CoordinationStatisticsCollector, coord_stats)
    registry.register(CoordinationDiagnostics, coord_diag)
    registry.register(CoordinationHealthMonitor, coord_health)
    registry.register(CoordinationRecommendationEngine, coord_recommend)
    registry.register(LockLeaseManager, lock_lease_mgr)
    registry.register(LockRecoveryManager, lock_recovery_mgr)
    registry.register(MutexManager, mutex_mgr)
    registry.register(DistributedLockManager, dist_lock_mgr)
    registry.register(RedisCoordinationService, redis_coordination_service)

    # Instantiate Queue Platform classes
    queue_registry = QueueRegistryImpl()
    queue_stats = QueueStatisticsCollectorImpl()
    queue_diag = QueueDiagnosticsImpl(redis_provider)
    queue_health = QueueHealthMonitorImpl(redis_provider)
    queue_recommend = QueueRecommendationEngineImpl(queue_stats, queue_diag)
    priority_q_mgr = PriorityQueueManagerImpl()
    delayed_q_mgr = DelayedQueueManagerImpl()
    retry_q_mgr = RetryQueueManagerImpl(queue_registry, queue_stats)
    queue_recovery_mgr = QueueRecoveryManagerImpl(queue_stats)
    queue_worker_coordinator = QueueWorkerCoordinatorImpl()
    
    queue_manager = QueueManagerImpl(
        redis_provider,
        queue_registry,
        priority_q_mgr,
        delayed_q_mgr,
        retry_q_mgr,
        queue_stats,
        queue_diag
    )
    queue_scheduler = QueueSchedulerImpl(queue_manager)
    redis_queue_service = RedisQueueServiceImpl(
        redis_provider,
        queue_registry,
        queue_manager,
        queue_stats
    )

    # Initialize all Queue Platform classes
    queue_registry.initialize()
    queue_stats.initialize()
    queue_diag.initialize()
    queue_health.initialize()
    queue_recommend.initialize()
    priority_q_mgr.initialize()
    delayed_q_mgr.initialize()
    retry_q_mgr.initialize()
    queue_recovery_mgr.initialize()
    queue_worker_coordinator.initialize()
    queue_manager.initialize()
    queue_scheduler.initialize()
    redis_queue_service.initialize()

    # Register Queue Platform in DI container
    registry.register(QueueRegistry, queue_registry)
    registry.register(QueueStatisticsCollector, queue_stats)
    registry.register(QueueDiagnostics, queue_diag)
    registry.register(QueueHealthMonitor, queue_health)
    registry.register(QueueRecommendationEngine, queue_recommend)
    registry.register(PriorityQueueManager, priority_q_mgr)
    registry.register(DelayedQueueManager, delayed_q_mgr)
    registry.register(RetryQueueManager, retry_q_mgr)
    registry.register(QueueRecoveryManager, queue_recovery_mgr)
    registry.register(QueueWorkerCoordinator, queue_worker_coordinator)
    registry.register(QueueManager, queue_manager)
    registry.register(QueueScheduler, queue_scheduler)
    registry.register(RedisQueueService, redis_queue_service)





    session_service = LocalSessionService(event_bus)
    context_service = LocalContextService(event_bus)
    memory_service = LocalMemoryService(event_bus)
    tool_service = LocalToolManager(event_bus)
    intent_resolver = LocalIntentResolver()
    model_service = LocalModelService(config_path=str(config_path), registry=registry)
    memory_service.set_model_service(model_service)

    project_intelligence = LocalProjectIntelligence()
    developer_workspace = LocalDeveloperWorkspace()
    research_service = LocalResearchService(model_service, registry=registry)

    research_service.initialize()
    n8n_service = LocalN8NService(model_service)
    n8n_service.initialize()
    personal_service = LocalPersonalService()
    personal_service.initialize()

    notion_cfg = getattr(config, "notion", None)
    knowledge_hub = LocalKnowledgeHub(
        config=notion_cfg,
        personal_service=personal_service
    )
    knowledge_hub.initialize()

    command_registry = CommandRegistry()

    command_registry.initialize()
    orchestrator_service = LocalOrchestratorService(command_registry)
    orchestrator_service.initialize()
    agent_registry = AgentRegistry()
    agent_manager = LocalAgentManager(agent_registry, orchestrator_service)
    agent_manager.initialize()

    github_cfg = getattr(config, "github", None)
    github_service = LocalGitHubService(
        model_service=model_service,
        project_intel=project_intelligence,
        dev_workspace=developer_workspace,
        token=github_cfg.token if github_cfg else None,
        base_url=github_cfg.base_url if github_cfg else "https://api.github.com",
        timeout=github_cfg.timeout if github_cfg else 30,
        max_retries=github_cfg.max_retries if github_cfg else 3,
        rate_limit_per_min=github_cfg.rate_limit_per_min if github_cfg else 60,
        cache_enabled=github_cfg.cache_enabled if github_cfg else True,
        offline_mode=github_cfg.offline_mode if github_cfg else False,
    )
    github_service.initialize()
    github_service._registry = registry

    # Source Control Intelligence Platform instantiations
    from aios.source_control import (
        SourceControlRegistry,
        ProviderDiscovery,
        ProviderConfigurationService,
        ProviderHealthMonitor,
        ProviderDiagnostics,
        ProviderValidator,
        SourceControlService,
        LocalGitExecutor,
        RepositoryManager,
        BranchManager,
        CommitManager,
        TagManager,
        MergeManager,
        DiffManager,
        WorkspaceRepositoryManager,
        PullRequestManager,
        IssueManager,
        ReleaseManager,
        WorkflowManager,
        WebhookManager,
        SourceControlTelemetry,
        SourceControlStatistics,
        SourceControlReportGenerator,
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
        validator=sc_validator
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
        statistics=sc_statistics
    )

    # Initialize all MIXIN classes
    sc_registry.initialize()
    sc_discovery.initialize()
    sc_config.initialize()
    sc_health.initialize()
    sc_diagnostics.initialize()
    sc_validator.initialize()
    source_control_service.initialize()
    local_git.initialize()
    repo_mgr.initialize()
    branch_mgr.initialize()
    commit_mgr.initialize()
    tag_mgr.initialize()
    merge_mgr.initialize()
    diff_mgr.initialize()
    workspace_repo_mgr.initialize()
    pr_mgr.initialize()
    issue_mgr.initialize()
    release_mgr.initialize()
    workflow_mgr.initialize()
    webhook_mgr.initialize()
    sc_telemetry.initialize()
    sc_statistics.initialize()
    sc_report.initialize()

    from aios.services.career import CareerOSService
    from aios.services.career_impl import LocalCareerOSService
    career_os = LocalCareerOSService(
        model_service=model_service,
        personal_service=personal_service,
        github_service=github_service,
        project_intel=project_intelligence,
        n8n_service=n8n_service,
        registry=registry
    )

    career_os.initialize()
    registry.register(CareerOSService, career_os)


    from aios.services.daily import DailyOSService
    from aios.services.daily_impl import LocalDailyOSService
    daily_os = LocalDailyOSService(
        model_service=model_service,
        personal_service=personal_service,
        github_service=github_service,
        project_intel=project_intelligence,
        career_os=career_os,
        registry=registry,
    )

    daily_os.initialize()
    registry.register(DailyOSService, daily_os)

    # Instantiate agents
    career_agent = CareerAgent(
        memory_service, context_service, tool_service, model_service, github_service, career_os, daily_os
    )


    developer_agent = DeveloperAgent(memory_service, context_service, tool_service, model_service)
    mock_agent = MockAgent(memory_service, context_service, tool_service)


    # Register to AgentRegistry
    agent_registry.register(career_agent)
    agent_registry.register(developer_agent)
    agent_registry.register(mock_agent)

    agent_runtime = LocalAgentRuntime(
        event_bus=event_bus,
        memory_service=memory_service,
        context_service=context_service,
        tool_service=tool_service,
        model_service=model_service
    )

    mission_engine = LocalMissionEngine(agent_runtime, registry=registry)

    mission_engine.initialize()
    runtime_service = LocalRuntime()
    runtime_service.initialize()
    reasoning_service = LocalReasoningService()
    reasoning_service.initialize()



    # 3. Register agents to the Agent Runtime
    agent_runtime.register_agent(mock_agent)
    agent_runtime.register_agent(developer_agent)
    agent_runtime.register_agent(career_agent)

    # 4. Register services on registry
    registry.register(EventBusService, event_bus)
    registry.register(SessionService, session_service)
    registry.register(ContextService, context_service)
    registry.register(MemoryService, memory_service)
    registry.register(IntentResolverService, intent_resolver)
    registry.register(ModelService, model_service)
    registry.register(ToolService, tool_service)
    registry.register(AgentRuntimeService, agent_runtime)
    registry.register(GitHubService, github_service)

    # Register Source Control Intelligence Platform components
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

    registry.register(ProjectIntelligenceService, project_intelligence)

    registry.register(DeveloperWorkspaceService, developer_workspace)
    registry.register(ResearchService, research_service)
    registry.register(N8NService, n8n_service)
    registry.register(PersonalService, personal_service)
    registry.register(KnowledgeHubService, knowledge_hub)

    registry.register(CommandRegistry, command_registry)
    registry.register(OrchestratorService, orchestrator_service)
    registry.register(AgentRegistry, agent_registry)
    registry.register(LocalAgentManager, agent_manager)
    registry.register(MissionEngine, mission_engine)
    registry.register(RuntimeService, runtime_service)
    registry.register(ReasoningService, reasoning_service)

    from aios.services.intent_engine import IntentEngine
    from aios.services.intent_engine_impl import LocalIntentEngine

    intent_engine = LocalIntentEngine(
        memory_service=memory_service,
        reasoning_service=reasoning_service,
        model_service=model_service
    )
    intent_engine.initialize()
    registry.register(IntentEngine, intent_engine)

    from aios.services.workspace_intelligence import WorkspaceIntelligenceService, CodeIntelligenceService
    from aios.services.workspace_intelligence_impl import LocalWorkspaceIntelligenceService, LocalCodeIntelligenceService

    workspace_intel = LocalWorkspaceIntelligenceService(
        project_intel=project_intelligence,
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    workspace_intel.initialize()
    registry.register(WorkspaceIntelligenceService, workspace_intel)

    code_intel = LocalCodeIntelligenceService(
        project_intel=project_intelligence,
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    code_intel.initialize()
    registry.register(CodeIntelligenceService, code_intel)

    from aios.services.engineering_intelligence import EngineeringIntelligenceService
    from aios.services.engineering_intelligence_impl import LocalEngineeringIntelligenceService

    eng_intel = LocalEngineeringIntelligenceService(
        code_intel=code_intel,
        workspace_intel=workspace_intel,
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    eng_intel.initialize()
    registry.register(EngineeringIntelligenceService, eng_intel)

    from aios.services.software_engineer import SoftwareEngineerService
    from aios.services.software_engineer_impl import LocalSoftwareEngineerService

    swe_service = LocalSoftwareEngineerService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    swe_service.initialize()
    registry.register(SoftwareEngineerService, swe_service)

    from aios.services.execution_engine import ExecutionEngine
    from aios.services.execution_engine_impl import LocalExecutionEngine

    exec_engine = LocalExecutionEngine(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    exec_engine.initialize()
    registry.register(ExecutionEngine, exec_engine)

    from aios.services.ai_workspace import AIWorkspaceService
    from aios.services.ai_workspace_impl import LocalAIWorkspaceService

    workspace_service = LocalAIWorkspaceService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        registry=registry
    )
    workspace_service.initialize()
    registry.register(AIWorkspaceService, workspace_service)

    from aios.services.file_planner import FilePlanner
    from aios.services.file_planner_impl import LocalFilePlanner

    file_planner_service = LocalFilePlanner(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    file_planner_service.initialize()
    registry.register(FilePlanner, file_planner_service)

    from aios.services.patch_generation import PatchGenerationService
    from aios.services.patch_generation_impl import LocalPatchGenerationService

    patch_service = LocalPatchGenerationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        registry=registry
    )
    patch_service.initialize()
    registry.register(PatchGenerationService, patch_service)

    from aios.services.code_generation import CodeGenerationService
    from aios.services.code_generation_impl import LocalCodeGenerationService

    codegen_service = LocalCodeGenerationService(
        memory_service=memory_service,
        model_service=model_service,
        knowledge_hub=knowledge_hub,
        registry=registry
    )
    codegen_service.initialize()
    registry.register(CodeGenerationService, codegen_service)

    from aios.services.test_engineer import AITestEngineerService
    from aios.services.test_engineer_impl import LocalAITestEngineerService

    test_eng_service = LocalAITestEngineerService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    test_eng_service.initialize()
    registry.register(AITestEngineerService, test_eng_service)

    from aios.services.test_impact import ChangeImpactAnalyzer
    from aios.services.test_impact_impl import LocalChangeImpactAnalyzer

    impact_analyzer = LocalChangeImpactAnalyzer(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    impact_analyzer.initialize()
    registry.register(ChangeImpactAnalyzer, impact_analyzer)

    from aios.services.test_generation import TestGenerationService
    from aios.services.test_generation_impl import LocalTestGenerationService

    test_gen_service = LocalTestGenerationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    test_gen_service.initialize()
    registry.register(TestGenerationService, test_gen_service)

    from aios.services.test_execution import TestExecutionService
    from aios.services.test_execution_impl import LocalTestExecutionService

    test_exec_service = LocalTestExecutionService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    test_exec_service.initialize()
    registry.register(TestExecutionService, test_exec_service)

    from aios.services.test_coverage import AITestCoverageService
    from aios.services.test_coverage_impl import LocalAITestCoverageService

    test_cov_service = LocalAITestCoverageService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    test_cov_service.initialize()
    registry.register(AITestCoverageService, test_cov_service)

    from aios.services.test_failure import FailureAnalysisService
    from aios.services.test_failure_impl import LocalFailureAnalysisService

    test_fail_service = LocalFailureAnalysisService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    test_fail_service.initialize()
    registry.register(FailureAnalysisService, test_fail_service)

    from aios.services.test_validation import ValidationService
    from aios.services.test_validation_impl import LocalValidationService

    validation_service = LocalValidationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    validation_service.initialize()
    registry.register(ValidationService, validation_service)

    from aios.services.engineering_profile import EngineeringProfileService
    from aios.services.engineering_profile_impl import LocalEngineeringProfileService

    profile_service = LocalEngineeringProfileService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
        profile_repo=profile_repo
    )
    profile_service.initialize()
    registry.register(EngineeringProfileService, profile_service)

    from aios.services.documentation_intelligence import DocumentationService
    from aios.services.documentation_intelligence_impl import LocalDocumentationService

    doc_service = LocalDocumentationService(
        memory_service=memory_service,
        engineering_profile_service=profile_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    doc_service.initialize()
    registry.register(DocumentationService, doc_service)

    from aios.services.readme_intelligence import READMEIntelligenceService
    from aios.services.readme_intelligence_impl import LocalREADMEIntelligenceService

    readme_service = LocalREADMEIntelligenceService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    readme_service.initialize()
    registry.register(READMEIntelligenceService, readme_service)

    from aios.services.api_documentation import APIDocumentationService
    from aios.services.api_documentation_impl import LocalAPIDocumentationService

    api_doc_service = LocalAPIDocumentationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    api_doc_service.initialize()
    registry.register(APIDocumentationService, api_doc_service)

    from aios.services.architecture_documentation import ArchitectureDocumentationService
    from aios.services.architecture_documentation_impl import LocalArchitectureDocumentationService

    arch_doc_service = LocalArchitectureDocumentationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    arch_doc_service.initialize()
    registry.register(ArchitectureDocumentationService, arch_doc_service)

    from aios.services.engineering_documentation import EngineeringDocumentationService
    from aios.services.engineering_documentation_impl import LocalEngineeringDocumentationService

    eng_doc_service = LocalEngineeringDocumentationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    eng_doc_service.initialize()
    registry.register(EngineeringDocumentationService, eng_doc_service)

    from aios.services.release_documentation import ReleaseDocumentationService
    from aios.services.release_documentation_impl import LocalReleaseDocumentationService

    release_doc_service = LocalReleaseDocumentationService(
        memory_service=memory_service,
        profile_service=profile_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    release_doc_service.initialize()
    registry.register(ReleaseDocumentationService, release_doc_service)

    from aios.services.approval import ApprovalEngineService
    from aios.services.approval_impl import LocalApprovalEngineService

    approval_service = LocalApprovalEngineService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    approval_service.initialize()
    registry.register(ApprovalEngineService, approval_service)

    from aios.services.review import ReviewEngine
    from aios.services.review_impl import LocalReviewEngine

    review_service = LocalReviewEngine(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    review_service.initialize()
    registry.register(ReviewEngine, review_service)

    from aios.services.collaboration import ReviewCollaborationService
    from aios.services.collaboration_impl import LocalReviewCollaborationService

    collab_service = LocalReviewCollaborationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    collab_service.initialize()
    registry.register(ReviewCollaborationService, collab_service)

    from aios.services.approval_history import ApprovalHistoryService
    from aios.services.approval_history_impl import LocalApprovalHistoryService

    history_service = LocalApprovalHistoryService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    history_service.initialize()
    registry.register(ApprovalHistoryService, history_service)

    from aios.services.automation import AutomationService
    from aios.services.automation_impl import LocalAutomationService

    automation_service = LocalAutomationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    automation_service.initialize()
    registry.register(AutomationService, automation_service)

    from aios.services.workflow_planning import WorkflowPlanner
    from aios.services.workflow_planning_impl import LocalWorkflowPlanner

    workflow_planner = LocalWorkflowPlanner(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    workflow_planner.initialize()
    registry.register(WorkflowPlanner, workflow_planner)

    from aios.services.n8n_translation import WorkflowTranslator
    from aios.services.n8n_translation_impl import LocalWorkflowTranslator

    workflow_translator = LocalWorkflowTranslator(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    workflow_translator.initialize()
    registry.register(WorkflowTranslator, workflow_translator)

    from aios.services.n8n_integration import N8NIntegrationService
    from aios.services.n8n_integration_impl import LocalN8NIntegrationService

    n8n_integration_service = LocalN8NIntegrationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    n8n_integration_service.initialize()
    registry.register(N8NIntegrationService, n8n_integration_service)

    # Register Production self-hosted n8n components
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
        n8n_client,
        n8n_auth,
        n8n_workflow,
        n8n_execution,
        n8n_version,
        n8n_capability
    )
    n8n_telemetry = N8NTelemetryCollector(n8n_health)
    n8n_event = N8NEventMonitor()
    n8n_validator = N8NValidator()
    n8n_diagnostics = N8NDiagnostics(n8n_config, n8n_auth, n8n_session)
    n8n_report = N8NReportGenerator(os.getcwd(), n8n_health, n8n_diagnostics)

    n8n_config.initialize()
    n8n_session.initialize()
    n8n_auth.initialize()
    n8n_conn.initialize()
    n8n_client.initialize()
    n8n_workflow.initialize()
    n8n_execution.initialize()
    n8n_credential.initialize()
    n8n_workspace.initialize()
    n8n_health.initialize()
    n8n_version.initialize()
    n8n_capability.initialize()
    n8n_telemetry.initialize()
    n8n_event.initialize()
    n8n_validator.initialize()
    n8n_diagnostics.initialize()
    n8n_report.initialize()

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

    from aios.services.workflow_monitoring import WorkflowMonitoringService
    from aios.services.workflow_monitoring_impl import LocalWorkflowMonitoringService

    workflow_monitoring_service = LocalWorkflowMonitoringService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    workflow_monitoring_service.initialize()
    registry.register(WorkflowMonitoringService, workflow_monitoring_service)

    from aios.services.workflow_optimization import WorkflowOptimizationService
    from aios.services.workflow_optimization_impl import LocalWorkflowOptimizationService

    workflow_optimization_service = LocalWorkflowOptimizationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    workflow_optimization_service.initialize()
    registry.register(WorkflowOptimizationService, workflow_optimization_service)

    from aios.services.workflow_versioning import WorkflowVersionService
    from aios.services.workflow_versioning_impl import LocalWorkflowVersionService

    workflow_version_service = LocalWorkflowVersionService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    workflow_version_service.initialize()
    registry.register(WorkflowVersionService, workflow_version_service)

    # 5. Instantiate Kernel with the registry
    kernel = Kernel(config_path=config_path, registry=registry)
    runtime_service._kernel = kernel
    return kernel
