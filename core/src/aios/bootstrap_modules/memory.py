"""
bootstrap_modules/memory.py

Constructs and registers memory services, SQL repositories, and vector platforms.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from aios.services.memory import MemoryService
from aios.services.memory_impl import LocalMemoryService

# Interface imports
from aios.services.persistence import (
    AIMemoryPersistenceService,
    AIMemoryRepository,
    AIProviderRepository,
    AIUsageStatisticsRepository,
    ApprovalRepository,
    AutomationMemoryRepository,
    AutomationPersistenceService,
    AutomationStatisticsRepository,
    AutomationTelemetryRepository,
    CandidateRanker,
    ChunkingService,
    CollectionSelector,
    ContextBuilder,
    ContextOptimizer,
    ConversationMemoryRepository,
    DocumentationMemoryRepository,
    DocumentationMetadataRepository,
    EmbeddingCache,
    EmbeddingEngine,
    EmbeddingService,
    EmbeddingVersionManager,
    EngineeringMemoryRepository,
    EngineeringMemoryService,
    EngineeringTaskRepository,
    HybridRetrievalService,
    KnowledgeMemoryRepository,
    PlanningRepository,
    ProjectMemoryRepository,
    ProviderCapabilityRepository,
    ProviderCheckpointRepository,
    ProviderFailoverRepository,
    ProviderHealthRepository,
    ProviderMemoryRepository,
    ProviderQuotaRepository,
    ProviderRoutingRepository,
    ProviderSessionRepository,
    ProviderStatisticsRepository,
    ProviderTelemetryRepository,
    QueryAnalysisService,
    ResearchMemoryRepository,
    RetrievalCache,
    ReviewRepository,
    SemanticMemoryManager,
    SemanticSearchService,
    TestResultRepository,
    TestSessionRepository,
    WorkflowExecutionRepository,
    WorkflowIntegrationRepository,
    WorkflowMonitoringRepository,
    WorkflowOptimizationRepository,
    WorkflowRepository,
    WorkflowTranslationRepository,
    WorkflowVersionRepository,
    WorkspaceMemoryRepository,
)

# Implementation imports
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
    AutomationMemoryRepositoryImpl,
    AutomationPersistenceHealthMonitor,
    AutomationPersistenceReportGenerator,
    AutomationPersistenceServiceImpl,
    AutomationPersistenceStatistics,
    AutomationPersistenceTelemetry,
    AutomationPersistenceValidator,
    AutomationStatisticsRepositoryImpl,
    AutomationTelemetryRepositoryImpl,
    CandidateRankerImpl,
    ChunkingServiceImpl,
    CollectionSelectorImpl,
    ContextBuilderImpl,
    ContextOptimizerImpl,
    ConversationMemoryRepositoryImpl,
    DocumentationMemoryRepositoryImpl,
    DocumentationMetadataRepositoryImpl,
    EmbeddingCacheImpl,
    EmbeddingEngineImpl,
    EmbeddingServiceImpl,
    EmbeddingVersionManagerImpl,
    EngineeringMemoryHealthMonitor,
    EngineeringMemoryReportGenerator,
    EngineeringMemoryRepositoryImpl,
    EngineeringMemoryServiceImpl,
    EngineeringMemoryStatistics,
    EngineeringMemoryTelemetry,
    EngineeringMemoryValidator,
    EngineeringTaskRepositoryImpl,
    HybridRetrievalServiceImpl,
    KnowledgeMemoryRepositoryImpl,
    PlanningRepositoryImpl,
    ProjectMemoryRepositoryImpl,
    ProviderCapabilityRepositoryImpl,
    ProviderCheckpointRepositoryImpl,
    ProviderFailoverRepositoryImpl,
    ProviderHealthRepositoryImpl,
    ProviderMemoryRepositoryImpl,
    ProviderQuotaRepositoryImpl,
    ProviderRoutingRepositoryImpl,
    ProviderSessionRepositoryImpl,
    ProviderStatisticsRepositoryImpl,
    ProviderTelemetryRepositoryImpl,
    QueryAnalysisServiceImpl,
    ResearchMemoryRepositoryImpl,
    RetrievalCacheImpl,
    ReviewRepositoryImpl,
    SemanticMemoryManagerImpl,
    SemanticSearchServiceImpl,
    TestResultRepositoryImpl,
    TestSessionRepositoryImpl,
    WorkflowExecutionRepositoryImpl,
    WorkflowIntegrationRepositoryImpl,
    WorkflowMonitoringRepositoryImpl,
    WorkflowOptimizationRepositoryImpl,
    WorkflowRepositoryImpl,
    WorkflowTranslationRepositoryImpl,
    WorkflowVersionRepositoryImpl,
    WorkspaceMemoryRepositoryImpl,
)

logger = logging.getLogger(__name__)


def bootstrap_memory(
    registry,  # noqa: ANN001
    config_path: Path,
    infra_ctx: dict,
    event_bus,  # noqa: ANN001
) -> dict:
    """Wires, initializes, and registers memory repositories, embeddings and search systems."""
    p_service = infra_ctx["p_service"]
    p_repos = infra_ctx["p_repos"]
    ri_service = infra_ctx["ri_service"]
    redis_provider = infra_ctx["redis_provider"]
    col_manager = infra_ctx["col_manager"]
    qdrant_provider = infra_ctx["qdrant_provider"]

    # ── 1. SQL MEMORY REPOSITORIES & SERVICES ──

    # A. Engineering Memory Repositories
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
        eng_report,
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

    # B. Automation Persistence Repositories
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
        aut_report,
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

    # C. AI Memory Persistence Repositories
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
        ai_report_generator,
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

    # Register all SQL memory components in DI container
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

    # ── 2. VECTOR MEMORY SYSTEMS (QDRANT & EMBEDDINGS) ──
    embedding_cache = EmbeddingCacheImpl()
    embedding_service = EmbeddingServiceImpl()
    embed_ver_manager = EmbeddingVersionManagerImpl()
    chunking_service = ChunkingServiceImpl()
    context_builder = ContextBuilderImpl()

    # Link Qdrant service and embedding cache into global RuntimeIntelligenceService (ri_service)
    ri_service.qdrant_service = infra_ctx["qdrant_service"]
    ri_service.embedding_cache = embedding_cache
    ri_service.p_repos = p_repos

    # Initialize all vector platform foundation components
    embedding_cache.initialize()
    embedding_service.initialize()
    embed_ver_manager.initialize()
    chunking_service.initialize()

    # Qdrant Vector memory repositories
    eng_mem_repo = EngineeringMemoryRepositoryImpl(
        "engineering_memory", qdrant_provider, col_manager
    )
    work_mem_repo = WorkspaceMemoryRepositoryImpl("workspace_memory", qdrant_provider, col_manager)
    proj_mem_repo = ProjectMemoryRepositoryImpl("project_memory", qdrant_provider, col_manager)
    doc_mem_repo = DocumentationMemoryRepositoryImpl(
        "documentation_memory", qdrant_provider, col_manager
    )
    conv_mem_repo = ConversationMemoryRepositoryImpl(
        "conversation_memory", qdrant_provider, col_manager
    )
    auto_mem_repo = AutomationMemoryRepositoryImpl(
        "automation_memory", qdrant_provider, col_manager
    )
    prov_mem_repo = ProviderMemoryRepositoryImpl("provider_memory", qdrant_provider, col_manager)
    res_mem_repo = ResearchMemoryRepositoryImpl("research_memory", qdrant_provider, col_manager)
    know_mem_repo = KnowledgeMemoryRepositoryImpl("knowledge_memory", qdrant_provider, col_manager)

    # Initialize vector repositories
    eng_mem_repo.initialize()
    work_mem_repo.initialize()
    proj_mem_repo.initialize()
    doc_mem_repo.initialize()
    conv_mem_repo.initialize()
    auto_mem_repo.initialize()
    prov_mem_repo.initialize()
    res_mem_repo.initialize()
    know_mem_repo.initialize()

    # Register in RepositoryRegistry (p_repos)
    p_repos.register_repository("engineering_memory", eng_mem_repo)
    p_repos.register_repository("workspace_memory", work_mem_repo)
    p_repos.register_repository("project_memory", proj_mem_repo)
    p_repos.register_repository("documentation_memory", doc_mem_repo)
    p_repos.register_repository("conversation_memory", conv_mem_repo)
    p_repos.register_repository("automation_memory", auto_mem_repo)
    p_repos.register_repository("provider_memory", prov_mem_repo)
    p_repos.register_repository("research_memory", res_mem_repo)
    p_repos.register_repository("knowledge_memory", know_mem_repo)

    # Register in ServiceRegistry
    registry.register(EngineeringMemoryRepository, eng_mem_repo)
    registry.register(WorkspaceMemoryRepository, work_mem_repo)
    registry.register(ProjectMemoryRepository, proj_mem_repo)
    registry.register(DocumentationMemoryRepository, doc_mem_repo)
    registry.register(ConversationMemoryRepository, conv_mem_repo)
    registry.register(AutomationMemoryRepository, auto_mem_repo)
    registry.register(ProviderMemoryRepository, prov_mem_repo)
    registry.register(ResearchMemoryRepository, res_mem_repo)
    registry.register(KnowledgeMemoryRepository, know_mem_repo)

    registry.register(EmbeddingCache, embedding_cache)
    registry.register(EmbeddingService, embedding_service)
    registry.register(EmbeddingVersionManager, embed_ver_manager)
    registry.register(ChunkingService, chunking_service)
    registry.register(ContextBuilder, context_builder)

    from aios.bootstrap_modules.providers import bootstrap_providers

    bootstrap_providers(registry, embedding_service)

    embedding_engine = EmbeddingEngineImpl(embedding_service, embedding_cache)
    semantic_search = SemanticSearchServiceImpl(embedding_engine)

    # Link into global RuntimeIntelligenceService
    ri_service.embedding_engine = embedding_engine
    ri_service.semantic_search = semantic_search

    # We will initialize and start embedding engines in the memory bootstrap,
    # but we assume the providers have already been registered.
    # To do that, the orchestration calls providers right after infrastructure setup.
    embedding_engine.initialize()
    embedding_engine.start()
    semantic_search.initialize()
    semantic_search.start()

    registry.register(EmbeddingEngine, embedding_engine)
    registry.register(SemanticSearchService, semantic_search)

    # Hybrid Retrieval platform classes
    query_analyzer = QueryAnalysisServiceImpl()
    if hasattr(query_analyzer, "load_config_file"):
        query_analyzer.load_config_file(config_path)

    col_selector = CollectionSelectorImpl()
    if hasattr(col_selector, "load_config_file"):
        col_selector.load_config_file(config_path)

    ranker = CandidateRankerImpl()
    optimizer = ContextOptimizerImpl()
    retrieval_cache = RetrievalCacheImpl(redis_provider)
    hybrid_retrieval = HybridRetrievalServiceImpl(
        query_analyzer, col_selector, semantic_search, ranker, optimizer, retrieval_cache
    )

    query_analyzer.initialize()
    query_analyzer.start()
    col_selector.initialize()
    col_selector.start()
    ranker.initialize()
    ranker.start()
    optimizer.initialize()
    optimizer.start()
    retrieval_cache.initialize()
    retrieval_cache.start()
    hybrid_retrieval.initialize()
    hybrid_retrieval.start()

    ri_service.hybrid_retrieval = hybrid_retrieval

    registry.register(QueryAnalysisService, query_analyzer)
    registry.register(CollectionSelector, col_selector)
    registry.register(CandidateRanker, ranker)
    registry.register(ContextOptimizer, optimizer)
    registry.register(RetrievalCache, retrieval_cache)
    registry.register(HybridRetrievalService, hybrid_retrieval)

    # Semantic Memory Manager
    semantic_mem_mgr = SemanticMemoryManagerImpl(registry)
    semantic_mem_mgr.initialize()
    semantic_mem_mgr.start()
    ri_service.semantic_mem_mgr = semantic_mem_mgr
    registry.register(SemanticMemoryManager, semantic_mem_mgr)

    # Instantiate Local Memory Service
    memory_service = LocalMemoryService(event_bus)
    # Note: memory_service.set_model_service(model_service) will be done in the orchestrator
    # once model_service is available.

    registry.register(MemoryService, memory_service)

    return {
        "embedding_service": embedding_service,
        "memory_service": memory_service,
        "task_repo": task_repo,
        "planning_repo": planning_repo,
        "approval_repo": approval_repo,
        "review_repo": review_repo,
        "doc_repo": doc_repo,
        "test_session_repo": test_session_repo,
        "test_result_repo": test_result_repo,
        "workflow_repo": workflow_repo,
        "execution_repo": execution_repo,
        "monitor_repo": monitor_repo,
        "optimization_repo": optimization_repo,
        "version_repo": version_repo,
        "translation_repo": translation_repo,
        "integration_repo": integration_repo,
        "telemetry_repo": telemetry_repo,
        "stats_repo": stats_repo,
        "ai_provider_repo": ai_provider_repo,
        "ai_cap_repo": ai_cap_repo,
        "ai_health_repo": ai_health_repo,
        "ai_telem_repo": ai_telem_repo,
        "ai_stats_repo": ai_stats_repo,
        "ai_quota_repo": ai_quota_repo,
        "ai_routing_repo": ai_routing_repo,
        "ai_session_repo": ai_session_repo,
        "ai_chk_repo": ai_chk_repo,
        "ai_failover_repo": ai_failover_repo,
        "ai_usage_repo": ai_usage_repo,
        "ai_mem_repo": ai_mem_repo,
        "eng_memory_service": eng_memory_service,
        "aut_persistence_service": aut_persistence_service,
        "ai_persistence_service": ai_persistence_service,
    }
