# Automated Research & Cron Walkers Spec
**Sprint 11 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define background walk schedules, crawling loops, and cache update tasks.
* **Scope**: Governs backend crons, sitemap crawlers, and document checks.
* **Audience**: DBAs, Backend Developers, and System Architects.
* **Related Documents**:
  * [research/source_discovery/crawler_architecture.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/crawler_architecture.md) - Crawler structures.
  * [research/memory/knowledge_lifecycle.md](file:///Users/anzarakhtar/aios/docs/research/memory/knowledge_lifecycle.md) - Lifecycle states.

---

## 1. Background Research Walkers

To maintain a fresh knowledge base, the AI OS runs background **Research Walkers** during idle system periods:
* **Cron Walkers**: Scheduled tasks scan sitemaps of primary documentation sources (e.g. `docs.python.org`) once per week to discover new updates.
* **RFC Scrapers**: Periodically queries IETF feeds to fetch newly published RFC specifications, keeping the standards database updated.
* **Vulnerability Feed Updates**: Fetches daily updates from security databases (e.g. CVE feeds) to check package dependency logs.

---

## 2. Automated Cache Refresh Cycles

When a change is discovered on a monitored page:
1. **Calculate Delta**: Downloads the modified page, converts it to markdown, and calculates a SHA-256 hash.
2. **Re-Index Page**: If the hash differs from the database record, the page is re-parsed, updating SQLite metadata and Qdrant vector points.
3. **Invalidate Cache**: Purges matching Redis cache namespaces, ensuring agents retrieve the updated specifications.
