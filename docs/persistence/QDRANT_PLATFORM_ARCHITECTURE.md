# Qdrant Platform Architecture Design

This document details the software design, dependency graph, class interfaces, and integration paths for the Qdrant Vector Intelligence Platform in the Personal AI OS.

---

## 1. Software Component Architecture

To preserve the clean structural patterns established by the PostgreSQL and Redis platforms, Qdrant integration enforces strict separation of concerns through the **Provider → Transport** pattern.

No external service, repository, or CLI command is allowed to import the Qdrant SDK (`qdrant_client`) directly. All vector operations must flow through the [QdrantProvider](file:///Users/anzarakhtar/aios/docs/persistence/QDRANT_PLATFORM_ARCHITECTURE.md#QdrantProvider) interface.

### Component Layout:
```
+-----------------------------------------------------------+
|                      Memory Services                      |
|           (MemoryServiceImpl, MemoryRetriever)            |
+-----------------------------------------------------------+
                              │ (Resolves from DI)
                              ▼
+-----------------------------------------------------------+
|                     QdrantProvider                        |
|   (Exposes Collection CRUD, Upsert, Search, Scroll, etc.) |
+-----------------------------------------------------------+
                              │ (Directs commands)
                              ▼
+-----------------------------------------------------------+
|                     QdrantTransport                       |
|        (Low-level client commands executor, logs latency) |
+-----------------------------------------------------------+
                              │ (Manages connections)
                              ▼
+-----------------------------------------------------------+
|                  QdrantConnectionManager                  |
|          (Connection pooling, reconnection loops)         |
+-----------------------------------------------------------+
                              │ (Network IO)
                              ▼
+-----------------------------------------------------------+
|                     Qdrant Server                         |
|                   (Localhost:6333)                        |
+-----------------------------------------------------------+
```

---

## 2. Core Interfaces and Classes

### QdrantConfigurationService
Inherits from `ServiceLifecycle`. Loads connection details (Host, HTTP Port, GRPC Port, API Key, Connection Timeout, Max Retries, Default Dimensions, Default Distance metric).

### QdrantConnectionManager
Inherits from `ServiceLifecycle`. Manages active connections to Qdrant. Returns either the HTTP client or GRPC client. Handles connection failure counters and backoff-retries.

### QdrantTransport
Inherits from `ServiceLifecycle` and defines abstract operations:
* `execute_command(self, cmd: str, *args, **kwargs) -> Any`
* `is_connected(self) -> bool`
* `connect(self) -> None`
* `disconnect(self) -> None`

### QdrantTransportImpl
Concrete transport implementation wrapping the python `QdrantClient`. Intercepts queries to measure performance latencies and records telemetry.

### QdrantProvider
Defines vector database operations:
* `create_collection(self, name: str, vector_size: int, distance: str) -> bool`
* `delete_collection(self, name: str) -> bool`
* `collection_exists(self, name: str) -> bool`
* `upsert_points(self, collection: str, points: List[Dict[str, Any]]) -> bool`
* `delete_points(self, collection: str, point_ids: List[str]) -> bool`
* `search_vectors(self, collection: str, vector: List[float], filter_query: Optional[Dict[str, Any]] = None, limit: int = 5, score_threshold: Optional[float] = None) -> List[Dict[str, Any]]`

### QdrantRuntimeService
High-level service interface acting as the registry coordinator. Integrates health checks, diagnostics alerts, capacity profiling, and statistics aggregation.

---

## 3. Dependency Injection and Lifecycle Registration

All Qdrant components inherit from `ServiceLifecycle` and are initialized sequentially inside `bootstrap.py` during boot:

```python
# Proposed registration in bootstrap.py:
qdrant_cfg = QdrantConfigurationService()
qdrant_conn = QdrantConnectionManager(qdrant_cfg)
qdrant_transport = QdrantTransportImpl(qdrant_cfg, qdrant_conn)
qdrant_provider = QdrantProviderImpl(qdrant_transport)

# Telemetry and analyzers
qdrant_stats = QdrantStatisticsCollectorImpl()
qdrant_health = QdrantHealthMonitorImpl(qdrant_provider)
qdrant_diag = QdrantDiagnosticsImpl(qdrant_provider)
qdrant_service = QdrantRuntimeServiceImpl(
    qdrant_provider, qdrant_stats, qdrant_health, qdrant_diag
)

# Registry wiring
registry.register(QdrantProvider, qdrant_provider)
registry.register(QdrantRuntimeService, qdrant_service)
```

Lifecycles are triggered in order: `initialize()` -> `start()` -> `stop()`.

---

## 4. Architectural Flows

### Write Path:
1. `MemoryService.add_memory` is invoked.
2. Raw memory object is saved permanently in PostgreSQL.
3. `MemoryClassifier` extracts tags and category.
4. `EmbeddingService` generates vector array from content string.
5. `MemoryIndexer` calls `QdrantProvider.upsert_points` to save text chunk, vector, and filters to Qdrant.

### Semantic Search Path:
1. `MemoryService.search_memory` is invoked with query string.
2. `EmbeddingService` embeds query text into vector.
3. `MemoryRetriever` resolves workspace and project pre-filters.
4. `MemoryRetriever` invokes `QdrantProvider.search_vectors` passing embedded vector and pre-filters.
5. Qdrant returns matching points above the score threshold.
6. Retrieved payloads are returned as `Memory` entities.
