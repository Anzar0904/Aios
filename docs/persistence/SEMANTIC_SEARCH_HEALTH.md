# Semantic Search Health Monitoring

This document details health checking and status tracking of the semantic search service.

---

## 1. Status Codes

* **`HEALTHY`**: Active embedding provider connected, zero failures recorded.
* **`DEGRADED`**: High failure rate (10+ errors) logged in the diagnostic manager.
* **`OFFLINE`**: Connection to Qdrant is broken or no active embedding provider is configured.

---

## 2. Diagnostics Integration

Health monitors verify that the background indexing queue does not grow excessively, alerting the user to configure cloud credentials if local fallbacks degrade.
