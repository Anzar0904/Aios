# Notion Intelligence — Cache Strategy Specification
**Sprint 9 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define Redis cache configurations, key structures, TTL parameters, and invalidation rules for Notion search queries.
* **Scope**: Governs Redis adapter classes, cache interceptors, and database invalidation pipelines.
* **Audience**: Systems DBAs, Performance Engineers, and AI developers.
* **Related Documents**:
  * [docs/persistence/REDIS_CACHE_ARCHITECTURE.md](file:///Users/anzarakhtar/aios/docs/persistence/REDIS_CACHE_ARCHITECTURE.md) - System Redis cache specification.
  * [notion/search/hybrid_search.md](file:///Users/anzarakhtar/aios/docs/notion/search/hybrid_search.md) - Hybrid search model details.

---

## 1. Caching Strategy Overview

Running full hybrid searches (lexical SQLite queries + Qdrant similarity vector searches + RRF rank merging) is resource-intensive. To optimize response times for frequent queries, the Personal AI OS uses **Redis** to cache hot search queries.

```
 [Search Query] ===> Check Redis Cache (TTL: 15 Mins)
                           / \
                        Hit   Miss
                        /       \
                       v         v
             [Return Cache]     [Execute Hybrid Search Query]
                                         |
                                         v
                                [Write to Redis Cache]
```

---

## 2. Redis Key Layout & Key Schemes

All Redis keys for the Notion module are isolated using a dedicated namespace:

* **Key Format**: `notion:cache:<workspace_id>:<query_hash>`
  * `<workspace_id>`: Restricts search results to the active workspace.
  * `<query_hash>`: SHA-256 hash of the normalized query string and parameters (e.g. limit bounds, similarity thresholds).

### Serialization Format
Cache payloads are serialized into compact JSON strings:
```json
{
  "cached_at": "2026-07-06T19:09:00+00:00",
  "results": [
    {
      "document_id": "notion_8f8bca12-efd8-4ba3-bfd0-cd1712a4501a",
      "title": "Notion Integration Design",
      "text_snippet": "This document defines...",
      "rrf_score": 0.033
    }
  ]
}
```

---

## 3. TTL (Time to Live) Configurations

Cache expiration policies are tailored to the type of search query:

```
+------------------+------------------------+---------------------------------------+
| Cache Type       | TTL Parameter          | Description                           |
+------------------+------------------------+---------------------------------------+
| Query Cache      | 900 Seconds (15 Mins)  | General semantic/lexical search query |
|                  |                        | results.                              |
+------------------+------------------------+---------------------------------------+
| Document Cache   | 3,600 Seconds (1 Hour) | Clean parsed Markdown versions of     |
|                  |                        | individual pages.                     |
+------------------+------------------------+---------------------------------------+
| Metadata Cache   | 86,400 Seconds (1 Day) | Workspace profiles, databases list,    |
|                  |                        | and users mappings.                   |
+------------------+------------------------+---------------------------------------+
```

---

## 4. Cache Invalidation Triggers

To prevent serving stale data, the system implements **Active Cache Invalidation**. Cache entries are purged immediately when any of the following events occur:

1. **SQLite Change**: The `NotionSyncEngine` pull flow updates or deletes a page in the local SQLite cache.
   * *Action*: Purge all keys matching the workspace namespace: `EVAL "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" 0 notion:cache:<workspace_id>:*`
2. **Local Write**: The user modifies a page title or database record via a local command.
   * *Action*: Purge the specific document cache key and the query cache namespace.
3. **Workspace Switch / Disconnection**:
   * *Action*: Delete all cached data matching the workspace ID.
