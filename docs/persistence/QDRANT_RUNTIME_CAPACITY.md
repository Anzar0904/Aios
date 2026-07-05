# Qdrant Runtime Capacity

This document describes the capacity metrics, storage foot-printing rules, and queue limitations of the Qdrant vector database layer in the Personal AI OS.

---

## 1. Capacity Trackers

* **Vector Count**: Tracks point counts across all active collections.
* **Estimated Memory Usage**: Approximates database RAM footprint:
  $$\text{RAM Bytes} = \text{Vector Count} \times \text{Dimensions} \times 4 \text{ bytes}$$
* **Estimated Disk Usage**: Estimates HNSW disk indexing footprint:
  $$\text{Disk Bytes} = \text{Vector Count} \times \text{Dimensions} \times 4 \text{ bytes} \times 1.5$$
* **Estimated Payload Storage**: Estimates payload JSON metadata sizing:
  $$\text{Payload Bytes} = \text{Vector Count} \times \text{Dimensions} \times 4 \text{ bytes} \times 0.2$$
* **Queue sizes**: Monitors active embedding queues, pending database retry indexes counts, and cache entries occupancy.

---

## 2. Capacity Constraints and Thresholds

* **Maximum Collection Point Count**: Warning threshold set at **10,000** vectors. Exceeding this triggers a diagnostics warning suggesting collection splitting.
* **Maximum Pending Index Queue**: Warning threshold set at **50** items. Exceeding this indicates persistent vector index failures or Qdrant connection refusals.
