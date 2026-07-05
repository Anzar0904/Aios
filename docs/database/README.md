# Database Documentation

> This section covers all persistence layers: SQLite (primary), PostgreSQL (production), Redis (cache/queue), and Qdrant (vector store).

---

## Architecture

| Document | Purpose |
|---|---|
| [ARCHITECTURE_DISCOVERY.md](ARCHITECTURE_DISCOVERY.md) | Persistence architecture discovery: schema, indexes, and data flow |
| [REPOSITORY_REGISTRY.md](REPOSITORY_REGISTRY.md) | Complete registry of all repository implementations and their SQL tables |

## PostgreSQL

| Document | Purpose |
|---|---|
| [POSTGRESQL_PERFORMANCE_BASELINE.md](POSTGRESQL_PERFORMANCE_BASELINE.md) | Performance benchmarks: connection pool, query latency, throughput |
| [POSTGRESQL_PRODUCTION_VALIDATION_REPORT.md](POSTGRESQL_PRODUCTION_VALIDATION_REPORT.md) | Full production validation: all 80+ repositories tested live |
| [POSTGRESQL_CAPACITY_REPORT.md](POSTGRESQL_CAPACITY_REPORT.md) | Capacity planning: row counts, index sizes, growth projections |

---

## Full Persistence Report Suite

The complete persistence documentation suite (162 files) is located in `docs/persistence/`. Key categories:

### SQLite / Core Persistence
- `WORKSPACE_PERSISTENCE_STATUS.md` — Workspace layer persistence status
- `AUTOMATION_PERSISTENCE_ARCHITECTURE.md` — Automation workflow persistence design

### Redis
- `REDIS_PLATFORM_ARCHITECTURE.md` — Redis cache/queue/rate-limit architecture
- `REDIS_PLATFORM_M1_REPORT.md` through `M7_REPORT.md` — Sprint milestone reports
- `REDIS_FAILURE_RECOVERY.md` — Redis failure modes and recovery procedures

### Qdrant (Vector Store)
- `AI_MEMORY_ARCHITECTURE.md` — Qdrant collection design for AI memory
- `SEMANTIC_SEARCH_ARCHITECTURE.md` — Hybrid retrieval pipeline
- `CHUNKING_ARCHITECTURE.md` — Document chunking strategy

---

## Related Sections
- [Runtime →](../runtime/README.md)
- [Troubleshooting →](../troubleshooting/README.md)
- [Architecture →](../architecture/README.md)
