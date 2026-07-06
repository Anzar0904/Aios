# Source Discovery & Knowledge Acquisition — Navigation Hub
**Sprint 11 · Milestone 2** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory houses the **Source Discovery & Knowledge Acquisition** specifications for the Personal AI OS.
> It builds upon the [Research Intelligence Foundation](file:///Users/anzarakhtar/aios/docs/research/README.md) and maps the physical web traversal pipelines to the system-wide hierarchy:
> **Research Domain → Knowledge Source → Document → Section → Concept → Evidence → KnowledgeNode**.
>
> In accordance with the system guidelines, all source discovery, crawler queuing, rate-limiting, and fetching mechanisms operate strictly under a local-first, privacy-focused paradigm managed centrally by the AI OS.

---

## Documents

| Document | Purpose |
|---|---|
| [source_discovery.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/source_discovery.md) | Search index crawling, sitemap parsing, and target link harvesting logic |
| [provider_registry.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/provider_registry.md) | Provider registries for search backends (DuckDuckGo, arXiv, IETF, Serper) |
| [crawler_architecture.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/crawler_architecture.md) | Async web walkers, robots.txt compliance, worker queues, and download maps |
| [acquisition_pipeline.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/acquisition_pipeline.md) | Step-by-step acquisition flows from query to structured markdown document caching |
| [content_fetching.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/content_fetching.md) | Low-level download protocols, headers encoding, timeout guards, and PDF fetching |
| [source_prioritization.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/source_prioritization.md) | Credibility scoring formulas, ranking target resources, and context relevance weights |
| [rate_limiting.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/rate_limiting.md) | Token-bucket algorithms, request jitter delays, and HTTP 429 back-off triggers |

---

## Reading Order

1. **[`provider_registry.md`](file:///Users/anzarakhtar/aios/docs/research/source_discovery/provider_registry.md)**: Start here to understand registered search backends.
2. **[`source_discovery.md`](file:///Users/anzarakhtar/aios/docs/research/source_discovery/source_discovery.md)**: Study how targets and URI lists are resolved.
3. **[`crawler_architecture.md`](file:///Users/anzarakhtar/aios/docs/research/source_discovery/crawler_architecture.md)**: Review structural crawling threads and watchdog safety.
4. **[`acquisition_pipeline.md`](file:///Users/anzarakhtar/aios/docs/research/source_discovery/acquisition_pipeline.md)**: Learn how the multi-stage discovery loops coordinate.
5. **[`content_fetching.md`](file:///Users/anzarakhtar/aios/docs/research/source_discovery/content_fetching.md)** & **[`rate_limiting.md`](file:///Users/anzarakhtar/aios/docs/research/source_discovery/rate_limiting.md)**: Deep dive into network protocols and throttling algorithms.
6. **[`source_prioritization.md`](file:///Users/anzarakhtar/aios/docs/research/source_discovery/source_prioritization.md)**: Examine credibility and ranking computations.
