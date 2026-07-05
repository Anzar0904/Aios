# Qdrant Provider Architecture

This document describes the design, interfaces, and responsibilities of the Qdrant Provider layer in the Personal AI OS.

---

## 1. Provider Pattern Responsibility

The `QdrantProvider` sits between the lower-level Transport and the upper-level repositories and services (such as Memory Service). It insulates the operating system from raw Qdrant client classes.

```text
+------------------------------------------------------+
|                     Repositories                     |
|           (MemoryRepository, CacheService)           |
+------------------------------------------------------+
                           │ (Resolves from DI)
                           ▼
+------------------------------------------------------+
|                    QdrantProvider                    |
|    - Handles collection lifecycle                    |
|    - Maps vectors to point payloads                  |
|    - Exposes upsert, delete, search endpoints         |
+------------------------------------------------------+
                           │
                           ▼
+------------------------------------------------------+
|                   QdrantTransport                    |
+------------------------------------------------------+
```

---

## 2. Interface Definitions

### `QdrantProvider`
Interface declared in `aios.services.persistence`:
* **`create_collection(self, name, vector_size, distance, on_disk_payload, quantization_config)`**: Requests the transport to create a collection with vector parameters.
* **`delete_collection(self, name)`**: Deletes a collection.
* **`collection_exists(self, name)`**: Checks collection existence.
* **`upsert_points(self, collection, points)`**: Upserts point payloads with dense vector coordinates.
* **`delete_points(self, collection, point_ids)`**: Deletes points by ID list.
* **`search_vectors(self, collection, vector, filter_query, limit, score_threshold)`**: Search closest matches.
* **`get_collection_info(self, name)`**: Returns collection stats and configurations.

---

## 3. Concrete Implementation

The `QdrantProviderImpl` maps raw payload arguments into structured `qdrant_client` models (such as `PointStruct`, `VectorParams`, `Distance`, `PointIdsList`).

All calls to the connection client are routed via `transport.execute_command(cmd, *args, **kwargs)` which measures latencies and wraps connection faults.
