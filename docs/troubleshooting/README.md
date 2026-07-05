# Troubleshooting Documentation

> This section provides diagnostic guides, failure recovery playbooks, and known-issue references.

---

## Workspace & Core Persistence

| Document | Purpose |
|---|---|
| [WORKSPACE_DIAGNOSTICS.md](WORKSPACE_DIAGNOSTICS.md) | Workspace layer: diagnosing save/load/session failures |

## PostgreSQL

| Document | Purpose |
|---|---|
| [POSTGRESQL_DIAGNOSTICS.md](POSTGRESQL_DIAGNOSTICS.md) | PostgreSQL connectivity, query errors, schema validation failures |
| [POSTGRESQL_FAILURE_RECOVERY.md](POSTGRESQL_FAILURE_RECOVERY.md) | PostgreSQL recovery playbook: connection pool exhaustion, migration errors |

## Redis

| Document | Purpose |
|---|---|
| [REDIS_DIAGNOSTICS.md](REDIS_DIAGNOSTICS.md) | Redis connectivity issues, eviction storms, TTL bugs |
| [REDIS_FAILURE_RECOVERY.md](REDIS_FAILURE_RECOVERY.md) | Redis recovery playbook: reconnection, cache invalidation, failover |

---

## Common Issues

| Symptom | Likely Cause | Guide |
|---|---|---|
| `Database execution blocked: Awaiting Runtime Configuration` | PersistenceService not initialized before use | [OPERATIONS_MANUAL.md](../deployment/OPERATIONS_MANUAL.md) |
| `NameError: name 'ctx_str' is not defined` | Pre-existing bug in `ProviderCheckpointRepositoryImpl` (fixed in 780defd) | — |
| Redis tests fail | Redis service not running | [REDIS_DIAGNOSTICS.md](REDIS_DIAGNOSTICS.md) |
| Qdrant tests fail | Qdrant service not running locally | [OPERATIONS_MANUAL.md](../deployment/OPERATIONS_MANUAL.md) |
| `Module not found: skills.github` | Missing skills package in PYTHONPATH | [IMPLEMENTATION_GUIDELINES.md](../guides/IMPLEMENTATION_GUIDELINES.md) |

---

## Full Diagnostics Suite

Complete diagnostic reports for all subsystems are in `docs/persistence/`:
- `AI_MEMORY_DIAGNOSTICS.md`
- `AUTOMATION_PERSISTENCE_DIAGNOSTICS.md`
- `REDIS_PLATFORM_DIAGNOSTICS.md`
- `RUNTIME_INTELLIGENCE_DIAGNOSTICS.md`
- `SEMANTIC_SEARCH_DIAGNOSTICS.md`

---

## Related Sections
- [Deployment →](../deployment/README.md)
- [Infrastructure →](../infrastructure/README.md)
- [Database →](../database/README.md)
