# Runtime Documentation

> This section covers the runtime intelligence system: context assembly, retrieval pipelines, embedding engines, and semantic search infrastructure.

---

## Architecture

| Document | Purpose |
|---|---|
| [RUNTIME_INTELLIGENCE_ARCHITECTURE.md](RUNTIME_INTELLIGENCE_ARCHITECTURE.md) | Qdrant-backed runtime intelligence: collection design, indexing strategy |
| [RUNTIME_INTELLIGENCE_DIAGNOSTICS.md](RUNTIME_INTELLIGENCE_DIAGNOSTICS.md) | Operational diagnostics and health checks for the runtime intelligence layer |

---

## Full Runtime Report Suite

The complete runtime intelligence report suite (statistics, health, discovery, status) is located in:

```
docs/persistence/RUNTIME_INTELLIGENCE_*.md
```

Key reports:
- `RUNTIME_INTELLIGENCE_STATISTICS.md` — Embedding counts, query latency, cache hit rates
- `RUNTIME_INTELLIGENCE_HEALTH.md` — Service health across Qdrant collections
- `RUNTIME_INTELLIGENCE_DISCOVERY.md` — Collection auto-discovery and schema validation
- `RUNTIME_INTELLIGENCE_STATUS.md` — Current operational status snapshot

---

## Semantic Search Components

Documented in `docs/persistence/`:
- `SEMANTIC_SEARCH_ARCHITECTURE.md` — Hybrid retrieval: BM25 + dense vector fusion
- `CHUNKING_ARCHITECTURE.md` — Document chunking and overlap strategies
- `COLLECTION_SELECTOR_ARCHITECTURE.md` — Dynamic collection routing
- `CONTEXT_BUILDER_ARCHITECTURE.md` — Context window assembly
- `CANDIDATE_RANKING_ARCHITECTURE.md` — Re-ranking and relevance scoring

---

## Related Sections
- [Database →](../database/README.md)
- [Architecture →](../architecture/README.md)
- [Troubleshooting →](../troubleshooting/README.md)
