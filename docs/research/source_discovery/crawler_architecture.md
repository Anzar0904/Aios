# Scraper & Crawler Architecture Spec
**Sprint 11 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical specifications for multi-threaded scrapers, worker queues, and robots.txt parsing logic.
* **Scope**: Governs async crawlers, worker configurations, and file observers.
* **Audience**: DBAs, Backend Developers, and System Architects.
* **Related Documents**:
  * [research/integration_strategy.md](file:///Users/anzarakhtar/aios/docs/research/integration_strategy.md) - Caching and integration.
  * [research/source_discovery/rate_limiting.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/rate_limiting.md) - Rate-limiting specifications.

---

## 1. Async Crawler Queue

To download large documentation trees (e.g. ECMA specs) efficiently without blocking agent reasoning, the crawling engine uses a non-blocking queue design:

```
[Harvester link output] ===> Crawl Task Queue (SQLite-backed)
                                    |
                                    v
                         [Robots.txt Evaluator] ===> Skip if path blocked
                                    |
                                    v
                           [Worker Scheduler]
                     - Poll queue every 200ms
                     - Limit active worker threads (default: 3)
                     - Respect target domain rate-limits
                                    |
                                    v
                          [Background Workers] ===> Fetch content -> write cache
```

* **SQLite Task Queue**: The crawl queue is persisted in SQLite (`crawl_tasks_queue`), ensuring crawling tasks resume correctly if the AI OS kernel restarts.
* **Robots.txt Parser Cache**: Crawler instances cache parsed `/robots.txt` properties internally for **3600 seconds** (1 hour) per target domain.

---

## 2. Crawler Worker Configurations

* **Thread Quotas**: Background scraping is restricted to at most **3 active worker threads** to prevent outbound network spikes or high RAM utilization.
* **Watchdog Timers**: Individual worker threads monitor HTTP socket operations. If a download hangs for **> 15 seconds**, the watchdog aborts the connection, flags the task as failed in the queue, and schedules a retry with exponential back-off.
* **Raw Content Caching**: Downloaded bytes are written directly to a local cache folder in `docs/research/scratch/raw_downloads/`, preventing repeated downloads of identical targets.
