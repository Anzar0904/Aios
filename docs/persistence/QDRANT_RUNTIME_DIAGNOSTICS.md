# Qdrant Runtime Diagnostics

This document details the self-diagnosing alarms, alerts codes, and remediation guidelines for the Qdrant persistence layer in the Personal AI OS.

---

## 1. Automated Alarms Codes

* **`TRANSPORT_FAILURE`**
  * *Severity*: Critical
  * *Trigger*: TCP connection to Qdrant is offline.
  * *Remediation*: Verify local docker container or binary is running at configured address.
* **`SLOW_QUERIES`**
  * *Severity*: Warning
  * *Trigger*: Average query search latencies exceed 100ms.
  * *Remediation*: Tune collection parameters, increase RAM allocations, or reconstruct HNSW indices.
* **`LARGE_COLLECTION`**
  * *Severity*: Warning
  * *Trigger*: A single collection contains more than 10,000 vectors.
  * *Remediation*: Restructure workspace contexts, delete historical dialog items, or schedule manual cleanup.
* **`CACHE_INEFFICIENCY`**
  * *Severity*: Warning
  * *Trigger*: Overall cache hit ratio falls below 20% over 10+ operations.
  * *Remediation*: Warm up cache with frequent queries or increase cache TTL.
* **`RETRY_STORM`**
  * *Severity*: Warning
  * *Trigger*: Indexing retry backlog exceeds 50 items.
  * *Remediation*: Verify Qdrant database status and examine PostgreSQL write queue logs.
