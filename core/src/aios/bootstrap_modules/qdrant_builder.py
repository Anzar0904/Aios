"""
bootstrap_modules/qdrant_builder.py

Constructs and registers the Qdrant and Vector memory platform:
  - Qdrant connection and runtime service
  - Embedding providers (SentenceTransformer, OpenAI, Gemini, Ollama, Mock)
  - Chunking and Context Builder
  - Vector Memory Repositories (Engineering, Workspace, etc.)
  - Qdrant Runtime Intelligence Platform
  - Semantic Memory Manager
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def build_qdrant_platform(registry, config_path, p_repos, ri_service, redis_provider):  # noqa: ANN001
    """Wire and register the Qdrant & Vector memory components into *registry*."""
    from aios.services.persistence import (
        AutomationMemoryRepository,
        ChunkingService,
        CollectionManager,
        ContextBuilder,
        ConversationMemoryRepository,
        DocumentationMemoryRepository,
        EmbeddingCache,
        EmbeddingEngine,
        EmbeddingService,
        EmbeddingVersionManager,
        EngineeringMemoryRepository,
        KnowledgeMemoryRepository,
        ProjectMemoryRepository,
        ProviderMemoryRepository,
        QdrantCapacityAnalyzer,
        QdrantDiagnosticsEngine,
        QdrantHealthAnalyzer,
        QdrantPerformanceAnalyzer,
        QdrantProvider,
        QdrantRecommendationEngine,
        QdrantRuntimeCoordinator,
        QdrantRuntimeReporter,
        QdrantRuntimeService,
        QdrantRuntimeTelemetry,
        QdrantRuntimeValidator,
        QdrantStatisticsCollector,
        QdrantTransport,
        ResearchMemoryRepository,
        SemanticMemoryManager,
        SemanticSearchService,
        WorkspaceMemoryRepository,
    )
    from aios.services.persistence_impl import (
        AutomationMemoryRepositoryImpl,
        ChunkingServiceImpl,
        CollectionManagerImpl,
        ContextBuilderImpl,
        ConversationMemoryRepositoryImpl,
        DocumentationMemoryRepositoryImpl,
        EmbeddingCacheImpl,
        EmbeddingEngineImpl,
        EmbeddingServiceImpl,
        EmbeddingVersionManagerImpl,
        EngineeringMemoryRepositoryImpl,
        GeminiProvider,
        KnowledgeMemoryRepositoryImpl,
        MockEmbeddingProvider,
        OllamaProvider,
        OpenAIProvider,
        ProjectMemoryRepositoryImpl,
        ProviderMemoryRepositoryImpl,
        QdrantCapacityAnalyzerImpl,
        QdrantConfigurationService,
        QdrantConnectionManager,
        QdrantDiagnosticsEngineImpl,
        QdrantHealthAnalyzerImpl,
        QdrantPerformanceAnalyzerImpl,
        QdrantProviderImpl,
        QdrantRecommendationEngineImpl,
        QdrantRuntimeCoordinatorImpl,
        QdrantRuntimeReporterImpl,
        QdrantRuntimeServiceImpl,
        QdrantRuntimeTelemetryImpl,
        QdrantRuntimeValidatorImpl,
        QdrantStatisticsCollectorImpl,
        QdrantTransportImpl,
        ResearchMemoryRepositoryImpl,
        SemanticMemoryManagerImpl,
        SemanticSearchServiceImpl,
        SentenceTransformerProvider,
        WorkspaceMemoryRepositoryImpl,
    )

    # ── Qdrant Service & Connection ───────────────────────────────────────
    qdrant_cfg = QdrantConfigurationService()
    qdrant_conn = QdrantConnectionManager(qdrant_cfg)
    qdrant_transport = QdrantTransportImpl(qdrant_cfg, qdrant_conn)
    qdrant_provider = QdrantProviderImpl(qdrant_transport)
    col_manager = CollectionManagerImpl(qdrant_provider, qdrant_cfg)
    qdrant_service = QdrantRuntimeServiceImpl(qdrant_provider, col_manager, qdrant_cfg)

    # ── Embedding & Chunking Services ──────────────────────────────────────
    embedding_cache = EmbeddingCacheImpl()
    embedding_service = EmbeddingServiceImpl()
    mock_embed_provider = MockEmbeddingProvider()
    embedding_service.register_provider("mock", mock_embed_provider)
    embed_ver_manager = EmbeddingVersionManagerImpl()

    chunking_service = ChunkingServiceImpl()
    context_builder = ContextBuilderImpl()

    ri_service.qdrant_service = qdrant_service
    ri_service.embedding_cache = embedding_cache
    ri_service.p_repos = p_repos

    for svc in (
        qdrant_cfg,
        qdrant_conn,
        qdrant_transport,
        qdrant_provider,
        col_manager,
        qdrant_service,
        embedding_cache,
        embedding_service,
        mock_embed_provider,
        embed_ver_manager,
        chunking_service,
    ):
        svc.initialize()

    qdrant_conn.start()

    registry.register(QdrantConfigurationService, qdrant_cfg)
    registry.register(QdrantConnectionManager, qdrant_conn)
    registry.register(QdrantTransport, qdrant_transport)
    registry.register(QdrantProvider, qdrant_provider)
    registry.register(CollectionManager, col_manager)
    registry.register(QdrantRuntimeService, qdrant_service)
    registry.register(EmbeddingCache, embedding_cache)
    registry.register(EmbeddingService, embedding_service)
    registry.register(EmbeddingVersionManager, embed_ver_manager)
    registry.register(ChunkingService, chunking_service)
    registry.register(ContextBuilder, context_builder)

    # ── Vector Memory Repositories ────────────────────────────────────────
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

    for repo in (
        eng_mem_repo,
        work_mem_repo,
        proj_mem_repo,
        doc_mem_repo,
        conv_mem_repo,
        auto_mem_repo,
        prov_mem_repo,
        res_mem_repo,
        know_mem_repo,
    ):
        repo.initialize()

    p_repos.register_repository("engineering_memory", eng_mem_repo)
    p_repos.register_repository("workspace_memory", work_mem_repo)
    p_repos.register_repository("project_memory", proj_mem_repo)
    p_repos.register_repository("documentation_memory", doc_mem_repo)
    p_repos.register_repository("conversation_memory", conv_mem_repo)
    p_repos.register_repository("automation_memory", auto_mem_repo)
    p_repos.register_repository("provider_memory", prov_mem_repo)
    p_repos.register_repository("research_memory", res_mem_repo)
    p_repos.register_repository("knowledge_memory", know_mem_repo)

    registry.register(EngineeringMemoryRepository, eng_mem_repo)
    registry.register(WorkspaceMemoryRepository, work_mem_repo)
    registry.register(ProjectMemoryRepository, proj_mem_repo)
    registry.register(DocumentationMemoryRepository, doc_mem_repo)
    registry.register(ConversationMemoryRepository, conv_mem_repo)
    registry.register(AutomationMemoryRepository, auto_mem_repo)
    registry.register(ProviderMemoryRepository, prov_mem_repo)
    registry.register(ResearchMemoryRepository, res_mem_repo)
    registry.register(KnowledgeMemoryRepository, know_mem_repo)

    # ── Additional Embedding Providers ─────────────────────────────────────
    st_provider = SentenceTransformerProvider()
    st_provider.initialize()
    embedding_service.register_provider("sentence_transformer", st_provider)

    openai_provider = OpenAIProvider()
    openai_provider.initialize()
    embedding_service.register_provider("openai", openai_provider)

    gemini_provider = GeminiProvider()
    gemini_provider.initialize()
    embedding_service.register_provider("gemini", gemini_provider)

    ollama_provider = OllamaProvider()
    ollama_provider.initialize()
    embedding_service.register_provider("ollama", ollama_provider)

    embedding_engine = EmbeddingEngineImpl(embedding_service, embedding_cache)
    semantic_search = SemanticSearchServiceImpl(embedding_engine)

    ri_service.embedding_engine = embedding_engine
    ri_service.semantic_search = semantic_search

    embedding_engine.initialize()
    embedding_engine.start()
    semantic_search.initialize()
    semantic_search.start()

    registry.register(EmbeddingEngine, embedding_engine)
    registry.register(SemanticSearchService, semantic_search)

    # ── Hybrid Retrieval Platform ─────────────────────────────────────────
    from aios.services.persistence import (
        CandidateRanker,
        CollectionSelector,
        ContextOptimizer,
        HybridRetrievalService,
        QueryAnalysisService,
        RetrievalCache,
    )
    from aios.services.persistence_impl import (
        CandidateRankerImpl,
        CollectionSelectorImpl,
        ContextOptimizerImpl,
        HybridRetrievalServiceImpl,
        QueryAnalysisServiceImpl,
        RetrievalCacheImpl,
    )

    query_analyzer = QueryAnalysisServiceImpl()
    if hasattr(query_analyzer, "load_config_file"):
        query_analyzer.load_config_file(config_path)

    col_selector = CollectionSelectorImpl()
    if hasattr(col_selector, "load_config_file"):
        col_selector.load_config_file(config_path)

    ranker = CandidateRankerImpl()
    optimizer = ContextOptimizerImpl()

    # Pass global redis_provider for distributed retrieval caching if available
    retrieval_cache = RetrievalCacheImpl(redis_provider)

    hybrid_retrieval = HybridRetrievalServiceImpl(
        query_analyzer, col_selector, semantic_search, ranker, optimizer, retrieval_cache
    )

    for svc in (
        query_analyzer,
        col_selector,
        ranker,
        optimizer,
        retrieval_cache,
        hybrid_retrieval,
    ):
        svc.initialize()
        svc.start()

    ri_service.hybrid_retrieval = hybrid_retrieval

    registry.register(QueryAnalysisService, query_analyzer)
    registry.register(CollectionSelector, col_selector)
    registry.register(CandidateRanker, ranker)
    registry.register(ContextOptimizer, optimizer)
    registry.register(RetrievalCache, retrieval_cache)
    registry.register(HybridRetrievalService, hybrid_retrieval)

    # ── Qdrant Runtime Intelligence Platform ──────────────────────────────
    qdrant_telemetry_service = QdrantRuntimeTelemetryImpl(registry)
    qdrant_health_analyzer = QdrantHealthAnalyzerImpl(qdrant_telemetry_service)
    qdrant_capacity_analyzer = QdrantCapacityAnalyzerImpl(qdrant_telemetry_service)
    qdrant_performance_analyzer = QdrantPerformanceAnalyzerImpl(qdrant_telemetry_service)
    qdrant_diagnostics = QdrantDiagnosticsEngineImpl(qdrant_telemetry_service)
    qdrant_recommendation_engine = QdrantRecommendationEngineImpl(
        qdrant_diagnostics, qdrant_capacity_analyzer, qdrant_performance_analyzer
    )
    qdrant_stats_collector = QdrantStatisticsCollectorImpl(qdrant_telemetry_service)
    qdrant_validator = QdrantRuntimeValidatorImpl()

    qdrant_coordinator = QdrantRuntimeCoordinatorImpl(
        qdrant_telemetry_service,
        qdrant_health_analyzer,
        qdrant_capacity_analyzer,
        qdrant_performance_analyzer,
        qdrant_recommendation_engine,
        qdrant_diagnostics,
        qdrant_stats_collector,
        None,
        qdrant_validator,
    )
    qdrant_reporter = QdrantRuntimeReporterImpl(qdrant_coordinator)
    qdrant_coordinator.reporter = qdrant_reporter

    for svc in (
        qdrant_telemetry_service,
        qdrant_health_analyzer,
        qdrant_capacity_analyzer,
        qdrant_performance_analyzer,
        qdrant_diagnostics,
        qdrant_recommendation_engine,
        qdrant_stats_collector,
        qdrant_reporter,
        qdrant_validator,
        qdrant_coordinator,
    ):
        svc.initialize()
        svc.start()

    ri_service.qdrant_telemetry = qdrant_coordinator

    registry.register(QdrantRuntimeTelemetry, qdrant_telemetry_service)
    registry.register(QdrantHealthAnalyzer, qdrant_health_analyzer)
    registry.register(QdrantCapacityAnalyzer, qdrant_capacity_analyzer)
    registry.register(QdrantPerformanceAnalyzer, qdrant_performance_analyzer)
    registry.register(QdrantRecommendationEngine, qdrant_recommendation_engine)
    registry.register(QdrantDiagnosticsEngine, qdrant_diagnostics)
    registry.register(QdrantStatisticsCollector, qdrant_stats_collector)
    registry.register(QdrantRuntimeReporter, qdrant_reporter)
    registry.register(QdrantRuntimeValidator, qdrant_validator)
    registry.register(QdrantRuntimeCoordinator, qdrant_coordinator)

    # ── Semantic Memory Manager ───────────────────────────────────────────
    semantic_mem_mgr = SemanticMemoryManagerImpl(registry)
    semantic_mem_mgr.initialize()
    semantic_mem_mgr.start()
    ri_service.semantic_mem_mgr = semantic_mem_mgr
    registry.register(SemanticMemoryManager, semantic_mem_mgr)
