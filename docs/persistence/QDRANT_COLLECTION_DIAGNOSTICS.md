# Qdrant Collection Diagnostics Alerts

This document details collection diagnostics, alerts, and remediations.

---

## 1. Diagnostics Alert Definitions

* **`COLLECTION_MISSING`**: Triggered when a collection was deleted or was not created.
  * *Remediation*: "Call `initialize()` on the repository to automatically create and register payload indices."
* **`INDEX_LATENCY_SPIKE`**: Triggered when search latency averages exceed 50.0ms.
  * *Remediation*: "Configure Scalar Quantization to optimize memory footprint and search speed."
* **`DESYNC_DETECTED`**: Triggered when count of records in PostgreSQL deviates from the Qdrant count.
  * *Remediation*: "Trigger the re-indexing worker to sync pending index states."
