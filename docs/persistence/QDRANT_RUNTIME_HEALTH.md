# Qdrant Runtime Health

This document outlines the health scoring rules and grading status methodology of the Qdrant vector database layer in the Personal AI OS.

---

## 1. Health Status Scoring

The `QdrantHealthAnalyzerImpl` evaluates health status based on a weighted average of 7 essential subsystem components:

* **Transport Health** (Weight: 20%): Evaluates TCP reachability status to the database.
* **Provider Health** (Weight: 15%): Assesses connection manager setup and credentials validation status.
* **Collection Health** (Weight: 15%): Monitors schema validations and indexes availability.
* **Embedding Health** (Weight: 15%): Evaluates embedding provider responsiveness and generation latency.
* **Search Health** (Weight: 15%): Assesses semantic search query success ratios.
* **Retry Queue Health** (Weight: 10%): Monitors pending indexing backlogs.
* **Cache Health** (Weight: 10%): Evaluates Redis caching connection states and error rates.

---

## 2. Health Grades and Status Mappings

* **HEALTHY** (Score: 80.0 - 100.0)
  * All systems operational. Average search latencies remain below 100ms. Retry queue size is minimal (< 10 entries).
* **DEGRADED** (Score: 50.0 - 79.9)
  * System operational with warnings. Redis cache is offline (reverts to memory-only local cache), or slow query latencies detected (> 100ms).
* **OFFLINE** (Score: 0.0 - 49.9)
  * Critical issues detected. Primary Qdrant transport is unreachable (refuses connections). Retries are blocked. Fallbacks are triggered.
