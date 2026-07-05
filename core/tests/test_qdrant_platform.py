import pytest
import os
from pathlib import Path

from aios.bootstrap import bootstrap_kernel
from aios.registry import ServiceRegistry
from aios.services.persistence import (
    QdrantTransport, QdrantProvider, CollectionManager, QdrantRuntimeService,
    EmbeddingMetadata, EmbeddingBatchRequest, EmbeddingBatchResponse,
    EmbeddingProvider, EmbeddingService, EmbeddingVersionManager, EmbeddingCache,
    ChunkMetadata, ChunkStrategy, ChunkResult, ChunkingService,
    ContextCandidate, ContextRanking, ContextAssembly, ContextBuilder,
    RuntimeIntelligenceService
)
from aios.services.persistence_impl import (
    QdrantConfigurationService, QdrantConnectionManager, QdrantTransportImpl, QdrantProviderImpl,
    CollectionManagerImpl, QdrantRuntimeServiceImpl,
    MockEmbeddingProvider, EmbeddingServiceImpl, EmbeddingVersionManagerImpl, EmbeddingCacheImpl,
    ChunkingServiceImpl, ContextBuilderImpl
)


def test_qdrant_configuration():
    os.environ["QDRANT_HOST"] = "127.0.0.1"
    os.environ["QDRANT_PORT"] = "6333"
    os.environ["QDRANT_GRPC_PORT"] = "6334"
    os.environ["QDRANT_API_KEY"] = "test-api-key"
    os.environ["QDRANT_HTTPS"] = "true"
    os.environ["QDRANT_TIMEOUT"] = "10.0"
    os.environ["QDRANT_RETRY_COUNT"] = "5"
    os.environ["QDRANT_DEFAULT_DIMENSIONS"] = "384"
    os.environ["QDRANT_DEFAULT_DISTANCE"] = "cosine"
    os.environ["QDRANT_ON_DISK_PAYLOAD"] = "false"
    os.environ["QDRANT_QUANTIZATION"] = "true"

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

    # Cleanup environment variables
    for key in [
        "QDRANT_HOST", "QDRANT_PORT", "QDRANT_GRPC_PORT", "QDRANT_API_KEY",
        "QDRANT_HTTPS", "QDRANT_TIMEOUT", "QDRANT_RETRY_COUNT",
        "QDRANT_DEFAULT_DIMENSIONS", "QDRANT_DEFAULT_DISTANCE",
        "QDRANT_ON_DISK_PAYLOAD", "QDRANT_QUANTIZATION"
    ]:
        os.environ.pop(key, None)


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
    assert "green" in stats["status"].lower() or "ok" in stats["status"].lower() or "yellow" in stats["status"].lower()

    # Upsert point
    upsert_success = provider.upsert_points(collection_name, [
        {"id": 1, "vector": [0.1, 0.2, 0.3, 0.4], "payload": {"category": "test"}}
    ])
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
        ContextCandidate(text="Point 1 text", score=0.8, metadata={}, source_collection="coll", point_id="1"),
        ContextCandidate(text="Point 2 text", score=0.6, metadata={}, source_collection="coll", point_id="2"),
        ContextCandidate(text="Point 1 text", score=0.85, metadata={}, source_collection="coll", point_id="1"), # Duplicate text
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
