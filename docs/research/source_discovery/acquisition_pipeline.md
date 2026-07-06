# Knowledge Acquisition Pipeline Spec
**Sprint 11 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the multi-stage pipeline for acquiring external technical knowledge and converting it into structured formats.
* **Scope**: Governs pipeline tasks, data schemas, and status transitions.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [research/capabilities.md](file:///Users/anzarakhtar/aios/docs/research/capabilities.md) - Capabilities domains.
  * [research/source_discovery/content_fetching.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/content_fetching.md) - Content fetching.

---

## 1. Multi-Stage Pipeline Execution

The **Knowledge Acquisition Pipeline** processes external technical sources through a series of structured stages, converting raw web assets into verified, semantic Knowledge Nodes.

```
                    [Objective: Acquire Topic X]
                                  |
                                  v
                       [Stage 1: Source Discovery]
            - Query registries (DDG, IETF, arXiv) for link lists.
                                  |
                                  v
                      [Stage 2: Prioritization]
            - Rank links by type, domain authority, and relevance.
                                  |
                                  v
                      [Stage 3: Content Fetching]
            - Download content, adhering to robots.txt and rate limits.
                                  |
                                  v
                     [Stage 4: Markdown Conversion]
            - Strip non-content markup (navs, ads, scripts).
                                  |
                                  v
                       [Stage 5: Local Caching]
            - SQLite: Store content md5 hashes and metadata records.
            - Qdrant: Embed sections and concepts (384d Cosine).
```

---

## 2. Pipeline State Transitions

Crawl and download tasks are tracked inside the `crawl_tasks_queue` database using explicit state transitions:
* **`PENDING`**: Tasks discovered but not scheduled.
* **`PROCESSING`**: Scheduled to an active worker thread.
* **`COMPLETED`**: Successfully downloaded, parsed to markdown, and cached in local databases.
* **`FAILED`**: Hit retry limits (e.g. DNS errors or HTTP 404). Failed tasks record the error message and timestamp for diagnostics.
