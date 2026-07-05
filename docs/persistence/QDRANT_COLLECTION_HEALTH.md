# Qdrant Collection Health Indicators

This document describes the health checks and statuses of the vector collections.

---

## 1. Collection Status Codes

Each collection status is derived from Qdrant:
* **`HEALTHY`**: Connection is reachable and collection status is `green` or `ok`.
* **`DEGRADED`**: Connection is reachable but collection status indicates warnings (e.g. `yellow`).
* **`OFFLINE`**: Connection is unreachable, or the collection has failed to instantiate.

---

## 2. Recovery Plan

If a repository's health degraded to `OFFLINE` or `DEGRADED`:
1. The connection manager attempts active reconnections.
2. Callers degrade gracefully and execute fallback lexical searches directly against PostgreSQL.
3. Once back online, the background indexer pushes `pending_index=True` records to Qdrant to restore synchronization.
