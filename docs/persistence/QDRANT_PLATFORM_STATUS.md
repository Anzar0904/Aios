# Qdrant Platform Operational Status

- **Connection State**: OFFLINE (Discovery Phase)
- **Diagnostics State**: HEALTHY (Planning stage)
- **Active Sprints**: Sprint 6
- **Current Milestone**: Milestone 8.1 (Architecture Discovery)

---

## 1. Roadmap & Milestone Progress

```
+-----------------------------------------------------------------------------------+
|                            QDRANT MILESTONE ROADMAP                               |
+------------------------+---------------------------------+------------------------+
| Milestone Name         | Version Target                  | Status                 |
+------------------------+---------------------------------+------------------------+
| Architecture Discovery | v0.6.1                          | Current (Active) ⠋      |
+------------------------+---------------------------------+------------------------+
| Provider & Transport   | v0.6.2                          | Next (Planned) 📅      |
+------------------------+---------------------------------+------------------------+
| Subsystem Design       | v0.6.3                          | Planned 📅             |
+------------------------+---------------------------------+------------------------+
| Embeddings Integration | v0.6.4                          | Planned 📅             |
+------------------------+---------------------------------+------------------------+
| Memory Indexer/Search  | v0.6.5                          | Planned 📅             |
+------------------------+---------------------------------+------------------------+
| Telemetry & Indicators | v0.6.6                          | Planned 📅             |
+------------------------+---------------------------------+------------------------+
| Mock & Unit Tests      | v0.6.7                          | Planned 📅             |
+------------------------+---------------------------------+------------------------+
| Live Production Cert   | v0.6.8                          | Planned 📅             |
+------------------------+---------------------------------+------------------------+
```

---

## 2. Active Risks & Technical Considerations

* **Local Embeddings Latency**: CPU-based embeddings generation can cause substantial lag.
  * *Mitigation*: Run background worker threads for embeddings generation or fallback to async API-based embedding providers.
* **Vector Index Out of Memory**: Dense indexes (HNSW) are RAM-heavy.
  * *Mitigation*: Limit collection dimensions, set reasonable payload sizes, and apply scalar quantization settings in Qdrant configs if necessary.

---

## 3. Architecture Decision Records (ADR)

### ADR 6.1: Vector Storage Domain Isolation
* **Context**: The AI OS contains memories across multiple workspaces, projects, and users.
* **Decision**: We will maintain isolated collections for each primary memory domain (Engineering, Workspace, Documentation, etc.) rather than a single massive collection, and apply strict metadata payload pre-filters (`workspace_id`, `project_id`) on search operations.
* **Rationale**: Prevent semantic cross-talk, enforce data privacy boundaries, and increase query accuracy.

### ADR 6.2: Embeddings Failure Path
* **Context**: External LLM embeddings APIs or local sentence-transformers servers can become unreachable.
* **Decision**: Enforce synchronous fallbacks in repository layers to default back to PostgreSQL full-text/substring search. Vector indexing operations are logged to a synchronization queue in SQLite/PostgreSQL to retry indexing once the engine is online.
* **Rationale**: Maintains basic OS retrieval stability and prevents loss of memory synchronization.
