# Research Intelligence — Knowledge Acquisition Compliance
**Sprint 11 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Verify compliance of search registries, crawler task queues, robots.txt caches, and rate-limiting loops.
* **Scope**: Governs search adapters, connection pools, and limiters.
* **Audience**: Quality Auditors, Systems Architects, and AI developers.
* **Related Documents**:
  * [research/source_discovery/README.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/README.md) - Source Discovery hub.
  * [research/source_discovery/rate_limiting.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/rate_limiting.md) - Rate limiting.

---

## 1. Compliance Audit Objectives

This audit verifies that the **Source Discovery & Knowledge Acquisition** layer routes searches to registered providers, walks sitemaps, obeys robots.txt rules, and throttles outbound requests.

---

## 2. Acquisition Verification Matrix

```
+------------------------------------+------------------------------------+----------+
| Acquisition Requirement            | Verification Check                 | Status   |
+------------------------------------+------------------------------------+----------+
| 1. Provider Registry Adapters      | Expose standard search interfaces  | PASS     |
|                                    | for DDG, Google, Serper, and arXiv.|          |
+------------------------------------+------------------------------------+----------+
| 2. Robots.txt Compliance           | Crawlers parse target robots.txt   | PASS     |
|                                    | files and skip blocked paths.      |          |
+------------------------------------+------------------------------------+----------+
| 3. Token-Bucket Rate Limiter       | Restricts requests per domain      | PASS     |
|                                    | (max 5 tokens, refill 2s).         |          |
+------------------------------------+------------------------------------+----------+
| 4. Jittered Request Delays         | Appends random delays (1.0-3.0s)   | PASS     |
|                                    | between domain queries.            |          |
+------------------------------------+------------------------------------+----------+
| 5. HTTP 429 Back-Off               | Detects 429 status and applies     | PASS     |
|                                    | exponential back-off delays.       |          |
+------------------------------------+------------------------------------+----------+
```

---

## 3. Compliance Verification Details

### 3.1 Scraper & Robots Validation
* Crawler tests verify that before downloading content, target `/robots.txt` paths are parsed, and blocked paths are successfully skipped.
* Search registry traces confirm queries are routed to registered adapters (DuckDuckGo, Google CSE) dynamically based on query configurations.

### 3.2 Request Throttling
* Rate limiter tests verify that token buckets restrict concurrent requests, preventing server overload.
* HTTP 429 tests verify that when a rate-limit error is simulated, the crawler pauses execution and waits according to back-off calculations.
