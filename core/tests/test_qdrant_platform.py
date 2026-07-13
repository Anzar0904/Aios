from pathlib import Path

from aios.bootstrap import bootstrap_kernel
from aios.services.persistence import (
    ChunkingService,
    ChunkStrategy,
    CollectionManager,
    ContextBuilder,
    ContextCandidate,
    EmbeddingCache,
    EmbeddingService,
    EmbeddingVersionManager,
    QdrantProvider,
    QdrantRuntimeService,
    QdrantTransport,
    RuntimeIntelligenceService,
)
from aios.services.persistence_impl import (
    ChunkingServiceImpl,
    CollectionManagerImpl,
    ContextBuilderImpl,
    EmbeddingCacheImpl,
    QdrantConfigurationService,
    QdrantConnectionManager,
    QdrantProviderImpl,
    QdrantTransportImpl,
)


def test_qdrant_configuration(monkeypatch):
    monkeypatch.setenv("QDRANT_HOST", "127.0.0.1")
    monkeypatch.setenv("QDRANT_PORT", "6333")
    monkeypatch.setenv("QDRANT_GRPC_PORT", "6334")
    monkeypatch.setenv("QDRANT_API_KEY", "test-api-key")
    monkeypatch.setenv("QDRANT_HTTPS", "true")
    monkeypatch.setenv("QDRANT_TIMEOUT", "10.0")
    monkeypatch.setenv("QDRANT_RETRY_COUNT", "5")
    monkeypatch.setenv("QDRANT_DEFAULT_DIMENSIONS", "384")
    monkeypatch.setenv("QDRANT_DEFAULT_DISTANCE", "cosine")
    monkeypatch.setenv("QDRANT_ON_DISK_PAYLOAD", "false")
    monkeypatch.setenv("QDRANT_QUANTIZATION", "true")

    config = QdrantConfigurationService()
    assert config.host == "127.0.0.1"
    assert config.port == 6333
    assert config.grpc_port == 6334
    assert config.api_key == "test-api-key"
    assert config.https is True
    assert config.timeout == 10.0
    assert config.retry_count == 5
    assert config.default_vector_dimensions == 384
    assert config.default_distance_metric == "COSINE"
    assert config.on_disk_payload is False
    assert config.quantization is True


def test_qdrant_connection_manager_and_transport():
    config = QdrantConfigurationService()
    # Override host/port to run against local live server
    config.host = "127.0.0.1"
    config.port = 6333
    config.api_key = None
    config.https = False

    conn_mgr = QdrantConnectionManager(config)
    conn_mgr.initialize()
    conn_mgr.start()

    import time

    for _ in range(50):
        if conn_mgr.is_connected():
            break
        time.sleep(0.1)

    assert conn_mgr.is_connected() is True
    assert conn_mgr.get_client() is not None

    transport = QdrantTransportImpl(config, conn_mgr)
    assert transport.is_connected() is True

    # Test execution of collections lookup
    collections_info = transport.execute_command("get_collections")
    assert collections_info is not None

    conn_mgr.stop()
    assert conn_mgr.is_connected() is False


def test_qdrant_provider_and_collection_manager():
    config = QdrantConfigurationService()
    config.host = "127.0.0.1"
    config.port = 6333
    config.api_key = None
    config.https = False

    conn_mgr = QdrantConnectionManager(config)
    conn_mgr.start()

    transport = QdrantTransportImpl(config, conn_mgr)
    provider = QdrantProviderImpl(transport)
    col_mgr = CollectionManagerImpl(provider, config)

    collection_name = "test_pytest_qdrant_platform"

    # Create collection
    if col_mgr.exists(collection_name):
        col_mgr.delete_collection(collection_name)
    success = col_mgr.create_collection(collection_name, dimensions=4, distance="cosine")
    assert success is True

    # Check existence
    assert col_mgr.exists(collection_name) is True

    # Create Index
    index_success = col_mgr.create_index(collection_name, "category", "keyword")
    assert index_success is True

    # Get Stats
    stats = col_mgr.get_statistics(collection_name)
    assert (
        "green" in stats["status"].lower()
        or "ok" in stats["status"].lower()
        or "yellow" in stats["status"].lower()
    )

    # Upsert point
    upsert_success = provider.upsert_points(
        collection_name,
        [{"id": 1, "vector": [0.1, 0.2, 0.3, 0.4], "payload": {"category": "test"}}],
    )
    assert upsert_success is True

    # Search Vector
    res = provider.search_vectors(collection_name, [0.1, 0.2, 0.3, 0.4], limit=1)
    assert len(res) > 0
    assert res[0]["id"] == 1
    assert res[0]["payload"]["category"] == "test"

    # Delete Points
    delete_success = provider.delete_points(collection_name, [1])
    assert delete_success is True

    # Verify deleted
    res_after = provider.search_vectors(collection_name, [0.1, 0.2, 0.3, 0.4], limit=1)
    assert len(res_after) == 0 or res_after[0]["id"] != 1

    # Delete collection
    del_success = col_mgr.delete_collection(collection_name)
    assert del_success is True
    assert col_mgr.exists(collection_name) is False

    conn_mgr.stop()


def test_embedding_cache():
    cache = EmbeddingCacheImpl()
    assert cache.get("hello", "v1") is None

    cache.set("hello", [0.1, 0.2, 0.3], "v1")
    assert cache.get("hello", "v1") == [0.1, 0.2, 0.3]

    stats = cache.get_statistics()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["cache_size"] == 1

    cache.invalidate("hello", "v1")
    assert cache.get("hello", "v1") is None


def test_chunking_service():
    service = ChunkingServiceImpl()
    text = "Paragraph one is here.\n\nParagraph two is also here.\n\nParagraph three."

    # Paragraph Strategy
    res_p = service.chunk_text(text, ChunkStrategy.PARAGRAPH)
    assert len(res_p) == 3
    assert res_p[0].text == "Paragraph one is here."
    assert res_p[1].text == "Paragraph two is also here."

    # Fixed Size Strategy
    res_f = service.chunk_text(text, ChunkStrategy.FIXED_SIZE, chunk_size=10, overlap=2)
    assert len(res_f) > 0


def test_context_builder():
    builder = ContextBuilderImpl()
    candidates = [
        ContextCandidate(
            text="Point 1 text", score=0.8, metadata={}, source_collection="coll", point_id="1"
        ),
        ContextCandidate(
            text="Point 2 text", score=0.6, metadata={}, source_collection="coll", point_id="2"
        ),
        ContextCandidate(
            text="Point 1 text", score=0.85, metadata={}, source_collection="coll", point_id="1"
        ),  # Duplicate text
    ]

    # Rank
    rankings = builder.rank_candidates(candidates, objective="Search Point 1")
    assert len(rankings) == 3
    # Top ranked should be Point 1 (score boost due to keyword match)
    assert "Point 1 text" in rankings[0].candidate.text

    # Deduplicate
    unique = builder.deduplicate(candidates)
    assert len(unique) == 2

    # Assemble
    assembly = builder.assemble_context(candidates, token_budget=10)
    assert assembly.budget_respected is True
    assert "Point 1 text" in assembly.assembled_text
    assert "Point 2 text" in assembly.assembled_text


def test_dependency_injection_and_runtime_intelligence():
    # Construct paths
    config_path = Path("aios.toml")
    kernel = bootstrap_kernel(config_path)
    registry = kernel.registry

    # Check that services are registered correctly in DI container
    assert registry.get(QdrantConfigurationService) is not None
    assert registry.get(QdrantConnectionManager) is not None
    assert registry.get(QdrantTransport) is not None
    assert registry.get(QdrantProvider) is not None
    assert registry.get(CollectionManager) is not None
    assert registry.get(QdrantRuntimeService) is not None
    assert registry.get(EmbeddingCache) is not None
    assert registry.get(EmbeddingService) is not None
    assert registry.get(EmbeddingVersionManager) is not None
    assert registry.get(ChunkingService) is not None
    assert registry.get(ContextBuilder) is not None

    # Check Runtime Intelligence integration
    qdrant_conn = registry.get(QdrantConnectionManager)
    import time

    for _ in range(50):
        if qdrant_conn.is_connected():
            break
        time.sleep(0.1)

    ri_service = registry.get(RuntimeIntelligenceService)
    assert ri_service is not None

    health = ri_service.get_health()
    assert "qdrant_health" in health
    assert health["qdrant_health"]["reachable"] is True

    telemetry = ri_service.get_telemetry()
    assert "qdrant_telemetry" in telemetry
    assert telemetry["qdrant_telemetry"]["connection_healthy"] is True

    diagnostics = ri_service.get_diagnostics()
    assert "qdrant_diagnostics" in diagnostics

    stats = ri_service.get_statistics()
    assert "qdrant_statistics" in stats
    assert "embedding_cache_statistics" in stats


def test_repositories_dependency_injection():
    from aios.services.persistence import RepositoryRegistry

    config_path = Path("aios.toml")
    kernel = bootstrap_kernel(config_path)
    registry = kernel.registry

    # Verify registered in ServiceRegistry
    from aios.services.persistence import (
        AutomationMemoryRepository,
        ConversationMemoryRepository,
        DocumentationMemoryRepository,
        EngineeringMemoryRepository,
        KnowledgeMemoryRepository,
        ProjectMemoryRepository,
        ProviderMemoryRepository,
        ResearchMemoryRepository,
        WorkspaceMemoryRepository,
    )

    assert registry.get(EngineeringMemoryRepository) is not None
    assert registry.get(WorkspaceMemoryRepository) is not None
    assert registry.get(ProjectMemoryRepository) is not None
    assert registry.get(DocumentationMemoryRepository) is not None
    assert registry.get(ConversationMemoryRepository) is not None
    assert registry.get(AutomationMemoryRepository) is not None
    assert registry.get(ProviderMemoryRepository) is not None
    assert registry.get(ResearchMemoryRepository) is not None
    assert registry.get(KnowledgeMemoryRepository) is not None

    # Verify registered in RepositoryRegistry (p_repos)
    p_repos = registry.get(RepositoryRegistry)
    assert p_repos is not None
    assert p_repos.get_repository("engineering_memory") is not None
    assert p_repos.get_repository("workspace_memory") is not None
    assert p_repos.get_repository("project_memory") is not None
    assert p_repos.get_repository("documentation_memory") is not None
    assert p_repos.get_repository("conversation_memory") is not None
    assert p_repos.get_repository("automation_memory") is not None
    assert p_repos.get_repository("provider_memory") is not None
    assert p_repos.get_repository("research_memory") is not None
    assert p_repos.get_repository("knowledge_memory") is not None


def test_repository_operations():
    from aios.services.persistence import EngineeringMemoryRepository

    config_path = Path("aios.toml")
    kernel = bootstrap_kernel(config_path)
    registry = kernel.registry

    repo = registry.get(EngineeringMemoryRepository)
    assert repo is not None

    # Clear and prepare test collection
    repo.clear()
    assert repo.count() == 0

    memory_id = "test-mem-id-1"
    vector = [0.2, 0.4, 0.6, 0.8] + [0.0] * 1532  # 1536 dim
    payload = {
        "workspace_id": "ws-123",
        "project_id": "proj-456",
        "user_id": "user-789",
        "memory_type": "code",
        "tags": ["python", "pytest"],
        "importance": 5,
        "created_at": 1700000000.0,
        "updated_at": 1700000000.0,
    }

    # Save
    assert repo.save(memory_id, vector, payload) is True
    assert repo.exists(memory_id) is True

    # Get
    res = repo.get(memory_id)
    assert res is not None
    assert res["payload"]["workspace_id"] == "ws-123"

    # Search with filters
    # Exact filter
    search_res = repo.search(vector, filter_query={"workspace_id": "ws-123"}, limit=1)
    assert len(search_res) == 1
    assert search_res[0]["id"] == memory_id or search_res[0]["payload"]["workspace_id"] == "ws-123"

    # Tag filter (MatchAny list)
    search_res_tag = repo.search(vector, filter_query={"tags": ["python"]}, limit=1)
    assert len(search_res_tag) == 1

    # Range filter
    search_res_range = repo.search(vector, filter_query={"importance": {"gt": 3, "lt": 7}}, limit=1)
    assert len(search_res_range) == 1

    # Combined filter
    search_res_combined = repo.search(
        vector,
        filter_query={"workspace_id": "ws-123", "importance": {"gt": 3}, "tags": ["python"]},
        limit=1,
    )
    assert len(search_res_combined) == 1

    # Count
    assert repo.count() == 1

    # Batch operations
    points = [
        {
            "id": "test-mem-id-2",
            "vector": [0.1] * 1536,
            "payload": {"workspace_id": "ws-123", "importance": 2, "tags": ["rust"]},
        },
        {
            "id": "test-mem-id-3",
            "vector": [0.3] * 1536,
            "payload": {"workspace_id": "ws-999", "importance": 8, "tags": ["python"]},
        },
    ]
    assert repo.batch_upsert(points) is True
    assert repo.count() == 3

    # Batch Delete
    assert repo.batch_delete(["test-mem-id-2", "test-mem-id-3"]) is True
    assert repo.count() == 1

    # Health and statistics
    health = repo.health()
    assert health["status"] == "HEALTHY"

    stats = repo.statistics()
    assert stats["collection_name"] == "engineering_memory"
    assert stats["points_count"] == 1
    assert stats["operation_counts"]["save"] >= 1

    # Cleanup
    assert repo.delete(memory_id) is True
    assert repo.count() == 0


def test_embedding_engine_and_semantic_search():
    import time

    from aios.services.persistence import (
        EmbeddingEngine,
        EmbeddingRequest,
        SemanticQuery,
        SemanticSearchService,
    )
    from aios.services.persistence_impl import SentenceTransformerProvider

    config_path = Path("aios.toml")
    kernel = bootstrap_kernel(config_path)
    registry = kernel.registry

    engine = registry.get(EmbeddingEngine)
    search_service = registry.get(SemanticSearchService)

    assert engine is not None
    assert search_service is not None

    # Test SentenceTransformer CPU fallback provider
    st_prov = SentenceTransformerProvider()
    st_prov.initialize()
    meta = st_prov.get_metadata()
    assert meta.dimensions == 384
    vec = st_prov.embed_text("test content")
    assert len(vec) == 384

    # Test EmbeddingEngine pipeline
    req = EmbeddingRequest(text="Query semantic search text", provider_name="mock")
    res = engine.embed_text(req)
    assert res.error is None
    assert len(res.vector) == 1532 or len(res.vector) == 1536  # matches mock provider dimensions

    # Test cache logic (duplicate vector prevention)
    res2 = engine.embed_text(req)
    # Both returns should match
    assert res.vector == res2.vector

    # Prepare repository and collection
    from aios.services.persistence import EngineeringMemoryRepository

    repo = registry.get(EngineeringMemoryRepository)
    repo.dimensions = 1536  # Align repo with mock provider vector size
    repo.clear()

    # Save point with vector
    memory_id = "test-query-id-1"
    repo.save(
        memory_id,
        res.vector,
        {"text": "Query semantic search text", "workspace_id": "ws-777", "project_id": "proj-888"},
    )

    # Test SemanticSearch query
    query = SemanticQuery(
        query_text="Query semantic search text",
        collection_name="engineering_memory",
        workspace_id="ws-777",
        limit=5,
    )

    prev_active = engine._active_provider
    engine._active_provider = "mock"
    search_res = search_service.search(query)
    engine._active_provider = prev_active

    assert len(search_res) == 1
    import uuid

    expected_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, memory_id))
    assert search_res[0].id == expected_uuid
    assert search_res[0].text == "Query semantic search text"

    # Test cross-collection search
    cross_res = search_service.cross_collection_search(query, collections=["engineering_memory"])
    assert len(cross_res) == 1
    assert cross_res[0].id == expected_uuid

    # Test Failure Recovery (Simulating Qdrant write block and retries)
    import sys

    from aios.services.persistence import PersistenceService

    sys.path.insert(0, str(Path(__file__).parent))
    from test_persistence import SQLiteTransportForTests

    db = registry.get(PersistenceService)

    # Inject SQLite test transport safely
    db.fallback_to_sqlite()
    test_transport = SQLiteTransportForTests(db.config)
    db.active_provider.transport = test_transport
    db.active_provider.transport.connect()

    # Explicitly create tables on the SQLite test instance
    db.execute(
        "CREATE TABLE IF NOT EXISTS pending_embedding_jobs ("
        "  id TEXT PRIMARY KEY, text TEXT, provider_name TEXT, collection_name TEXT, "
        "  status TEXT, attempts INTEGER, last_error TEXT, created_at REAL, updated_at REAL"
        ")"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS pending_indexing_jobs ("
        "  id TEXT PRIMARY KEY, entity_id TEXT, collection_name TEXT, vector TEXT, payload TEXT, status TEXT, "
        "  workspace_id TEXT, project_id TEXT, embedding_version TEXT, retry_count INTEGER, "
        "  failure_reason TEXT, attempts INTEGER, last_error TEXT, created_at REAL, updated_at REAL"
        ")"
    )

    # Save a fake pending embedding job
    job_id = "pending-job-uuid-1"
    past_time = time.time() - 100
    db.execute(
        "INSERT INTO pending_embedding_jobs (id, text, provider_name, collection_name, status, attempts, created_at, updated_at) VALUES (?, ?, ?, ?, 'PENDING', 0, ?, ?)",
        (job_id, "pending text message", "mock", "engineering_memory", past_time, past_time),
    )

    # Let the retry worker process it
    engine.run_retry_cycle()

    # Check that job has been processed and cleared
    rows = db.execute("SELECT id FROM pending_embedding_jobs WHERE id = ?", (job_id,))
    assert len(rows) == 0

    # Clean up
    repo.clear()


def test_hybrid_retrieval_pipeline():
    import time

    from aios.services.persistence import (
        CandidateRanker,
        CollectionSelector,
        ContextOptimizer,
        EngineeringMemoryRepository,
        HybridRetrievalService,
        QueryAnalysisService,
        RetrievalCache,
        RetrievalCandidate,
    )

    config_path = Path("aios.toml")
    kernel = bootstrap_kernel(config_path)
    registry = kernel.registry

    query_analyzer = registry.get(QueryAnalysisService)
    selector = registry.get(CollectionSelector)
    ranker = registry.get(CandidateRanker)
    optimizer = registry.get(ContextOptimizer)
    cache = registry.get(RetrievalCache)
    hybrid_retrieval = registry.get(HybridRetrievalService)
    from aios.services.persistence import SemanticSearchService

    search_service = registry.get(SemanticSearchService)

    # Test Query Analysis intent detection
    analysis = query_analyzer.analyze_query("def optimize_context_query(): pass")
    assert analysis.intent == "code_search"
    assert "engineering" in analysis.domains

    # Test Collection Selector
    cols = selector.select_collections(analysis)
    assert "engineering_memory" in cols

    # Test Candidate Ranker score weighting and decay
    c1 = RetrievalCandidate(
        id="cand-1",
        text="some source code block",
        score=0.0,
        metadata={},
        source_collection="engineering_memory",
        similarity_score=0.8,
        importance_score=0.9,
        freshness_score=0.7,
    )
    c2 = RetrievalCandidate(
        id="cand-2",
        text="older code documentation",
        score=0.0,
        metadata={},
        source_collection="engineering_memory",
        similarity_score=0.9,
        importance_score=0.4,
        freshness_score=0.3,
    )

    ranked = ranker.rank_candidates([c2, c1])
    # c1 has higher combined score (0.8*0.5 + 0.9*0.3 + 0.7*0.2 = 0.81) vs c2 (0.9*0.5 + 0.4*0.3 + 0.3*0.2 = 0.63)
    assert ranked[0].id == "cand-1"

    # Test Context Optimizer token budgeting and duplicate elimination
    # token budget 20 tokens (approx 80 characters)
    c_opt_1 = RetrievalCandidate(
        id="cand-opt-1",
        text="A very long text chunk that should exceed the token budget if combined with other chunks.",
        score=0.9,
        metadata={},
        source_collection="engineering_memory",
        similarity_score=0.9,
        importance_score=0.8,
        freshness_score=0.8,
    )
    c_opt_2 = RetrievalCandidate(
        id="cand-opt-2",
        text="Short text",
        score=0.8,
        metadata={},
        source_collection="engineering_memory",
        similarity_score=0.8,
        importance_score=0.8,
        freshness_score=0.8,
    )
    res = optimizer.optimize_context([c_opt_1, c_opt_2], token_budget=15)
    # The first candidate (len // 4 = 90 // 4 = 22 tokens) exceeds budget 15, so it is skipped.
    # The second candidate (len // 4 = 10 // 4 = 2 tokens) fits within budget 15!
    assert len(res.candidates_included) == 1
    assert res.candidates_included[0].id == "cand-opt-2"

    # Test Retrieval Cache statistics
    cache_key = "test_retrieval_cache_key"
    cache.set_query_results(cache_key, [c1])
    retrieved = cache.get_query_results(cache_key)
    assert len(retrieved) == 1
    assert retrieved[0].id == "cand-1"
    stats = cache.get_statistics()
    assert stats["hits"] == 1

    # Populate Qdrant repository for end-to-end pipeline test
    repo = registry.get(EngineeringMemoryRepository)
    repo.dimensions = 384  # Align repo with sentence_transformer vector size
    repo.clear()

    # Save test item
    from aios.services.persistence import EmbeddingEngine, EmbeddingRequest

    engine = registry.get(EmbeddingEngine)
    res_embed = engine.embed_text(EmbeddingRequest(text="def hello_world_func(): print(123)"))

    # Save record with metadata
    memory_id = "test-retrieval-query-1"
    repo.save(
        memory_id,
        res_embed.vector,
        {"text": "def hello_world_func(): print(123)", "importance": 9, "created_at": time.time()},
    )

    # Test Hybrid retrieval service execution
    pipeline_res = hybrid_retrieval.retrieve(query_text="def hello_world_func", token_budget=1000)
    assert len(pipeline_res.candidates_included) >= 1
    assert "def hello_world_func" in pipeline_res.context_text

    # Test Fallback Behaviour (Database Lexical Fallback)
    # We simulate semantic search failure by calling retrieve with a non-existent mock collection
    # causing Qdrant query to fail and fallback to look up PG database ai_memory table.
    from aios.services.persistence import PersistenceService
    from test_persistence import SQLiteTransportForTests

    db = registry.get(PersistenceService)

    # Swap to test SQLite db
    db.fallback_to_sqlite()
    test_transport = SQLiteTransportForTests(db.config)
    db.active_provider.transport = test_transport
    db.active_provider.transport.connect()

    # Create schema and populate mock record
    db.execute(
        "CREATE TABLE IF NOT EXISTS ai_memory (id TEXT PRIMARY KEY, key TEXT, value TEXT, metadata TEXT, created_at REAL, updated_at REAL)"
    )
    db.execute(
        "INSERT INTO ai_memory (id, key, value, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (
            "fallback-id-123",
            "lexical_key",
            "lexical fallback text message content match",
            "{}",
            time.time(),
            time.time(),
        ),
    )

    # Force SemanticSearch to raise an exception by mocking it
    # which will trigger lexical fallback lookup against ai_memory table
    original_search = search_service.search
    from unittest.mock import MagicMock

    search_service.search = MagicMock(side_effect=Exception("Mocked Qdrant Offline"))

    try:
        fallback_res = hybrid_retrieval.retrieve(
            query_text="lexical fallback text message", token_budget=1000
        )
        assert len(fallback_res.candidates_included) >= 1
        assert "lexical fallback text message content match" in fallback_res.context_text
    finally:
        search_service.search = original_search

    # Clean up
    repo.clear()


def test_qdrant_runtime_intelligence():
    from pathlib import Path

    from aios.services.persistence import (
        QdrantCapacityAnalyzer,
        QdrantDiagnosticsEngine,
        QdrantHealthAnalyzer,
        QdrantPerformanceAnalyzer,
        QdrantRecommendationEngine,
        QdrantRuntimeCoordinator,
        QdrantRuntimeReporter,
        QdrantRuntimeTelemetry,
        QdrantRuntimeValidator,
        QdrantStatisticsCollector,
        RuntimeIntelligenceService,
    )

    config_path = Path("aios.toml")
    kernel = bootstrap_kernel(config_path)
    registry = kernel.registry

    # 1. DI check
    telemetry = registry.get(QdrantRuntimeTelemetry)
    health = registry.get(QdrantHealthAnalyzer)
    capacity = registry.get(QdrantCapacityAnalyzer)
    performance = registry.get(QdrantPerformanceAnalyzer)
    diagnostics = registry.get(QdrantDiagnosticsEngine)
    recommendations = registry.get(QdrantRecommendationEngine)
    statistics = registry.get(QdrantStatisticsCollector)
    reporter = registry.get(QdrantRuntimeReporter)
    validator = registry.get(QdrantRuntimeValidator)
    coordinator = registry.get(QdrantRuntimeCoordinator)
    global_ri = registry.get(RuntimeIntelligenceService)

    assert telemetry is not None
    assert health is not None
    assert capacity is not None
    assert performance is not None
    assert diagnostics is not None
    assert recommendations is not None
    assert statistics is not None
    assert reporter is not None
    assert validator is not None
    assert coordinator is not None

    # 2. Telemetry and validator check
    telem_data = telemetry.get_telemetry()
    assert isinstance(telem_data, dict)
    assert validator.validate_telemetry(telem_data) is True

    # 3. Health check
    health_data = health.analyze_health()
    assert "overall_score" in health_data
    assert "status" in health_data
    assert health_data["status"] in ["HEALTHY", "DEGRADED", "OFFLINE"]
    assert "components" in health_data
    for comp in [
        "collection",
        "embedding",
        "search",
        "transport",
        "provider",
        "retry_queue",
        "cache",
    ]:
        assert comp in health_data["components"]
        assert "score" in health_data["components"][comp]
        assert "status" in health_data["components"][comp]

    # 4. Capacity check
    capacity_data = capacity.analyze_capacity()
    assert "vector_count" in capacity_data
    assert "memory_usage" in capacity_data
    assert "disk_usage" in capacity_data
    assert "payload_storage" in capacity_data
    assert "embedding_queue" in capacity_data
    assert "retry_backlog" in capacity_data
    assert "cache_utilisation" in capacity_data
    assert "collection_sizes" in capacity_data

    # 5. Performance check
    perf_data = performance.analyze_performance()
    assert "latencies" in perf_data
    assert "throughput" in perf_data
    assert "p50" in perf_data
    assert "p95" in perf_data
    assert "p99" in perf_data
    for l_key in [
        "embedding_latency",
        "batch_embedding_latency",
        "search_latency",
        "retrieval_latency",
    ]:
        assert l_key in perf_data["latencies"]

    # 6. Diagnostics check
    diagnostics.log_error("Test diagnostics alert", "WARNING", "No remediation action required")
    diag_data = diagnostics.get_diagnostics()
    assert len(diag_data["errors"]) > 0
    assert diag_data["errors"][0]["message"] == "Test diagnostics alert"

    # 7. Recommendations check
    recs_list = recommendations.generate_recommendations()
    assert isinstance(recs_list, list)
    if recs_list:
        assert "category" in recs_list[0]
        assert "issue" in recs_list[0]
        assert "suggestion" in recs_list[0]

    # 8. Report checks
    report_md = reporter.generate_report()
    assert "# Qdrant Runtime Intelligence Report" in report_md
    assert "Capacity Utilization" in report_md

    # 9. Coordinator getters checks
    assert coordinator.get_telemetry_service() == telemetry
    assert coordinator.get_health_analyzer() == health
    assert coordinator.get_capacity_analyzer() == capacity
    assert coordinator.get_performance_analyzer() == performance
    assert coordinator.get_diagnostics() == diagnostics
    assert coordinator.get_recommendation_engine() == recommendations
    assert coordinator.get_stats_collector() == statistics
    assert coordinator.get_reporter() == reporter
    assert coordinator.get_validator() == validator

    # 10. Global forwarding check
    global_health = global_ri.get_health()
    assert "qdrant_health" in global_health
    assert global_health["qdrant_health"]["status"] == health_data["status"]

    global_telemetry = global_ri.get_telemetry()
    assert "qdrant_telemetry" in global_telemetry
    assert "qdrant_capacity" in global_telemetry

    global_stats = global_ri.get_statistics()
    assert "qdrant_statistics" in global_stats

    global_diag = global_ri.get_diagnostics()
    assert "qdrant_diagnostics" in global_diag

    global_recs = global_ri.get_recommendations()
    # Check if our logged error alert is forwarded
    found_custom_alert = False
    for r in global_recs:
        if r.get("issue") == "Test diagnostics alert":
            found_custom_alert = True
            break
    assert found_custom_alert is True

    global_learning = global_ri.get_learning_payload()
    assert "qdrant_learning" in global_learning
