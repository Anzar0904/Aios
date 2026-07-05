# Semantic Search Diagnostics & Remediation

This document defines diagnostic alerts and suggested remediations for the semantic search platform.

---

## 1. Alert Configurations

* **`EMBEDDING_GENERATION_FAILED`**: Triggered when the active provider raises an API error or network exception.
  * *Remediation*: Check cloud provider API keys, quota, or local CPU availability.
* **`NaN_VECTOR_DETECTED`**: Triggered when generated embedding vectors contain invalid floats.
  * *Remediation*: Inspect text chunking size or re-initialize SentenceTransformers.
* **`POSTGRES_RETRY_QUEUE_FULL`**: Triggered when the pending retry queue exceeds 100 entries.
  * *Remediation*: Verify database transport connectivity is active.
