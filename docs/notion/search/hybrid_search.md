# Notion Intelligence — Hybrid Search Specification
**Sprint 9 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the hybrid lexical-semantic query architecture and Reciprocal Rank Fusion (RRF) ranking algorithm.
* **Scope**: Governs Python search interfaces, rank merger classes, and query routers.
* **Audience**: Backend Engineers, Systems Architects, and Search Quality Auditors.
* **Related Documents**:
  * [notion/search/indexing.md](file:///Users/anzarakhtar/aios/docs/notion/search/indexing.md) - SQLite indexing.
  * [notion/search/semantic_memory.md](file:///Users/anzarakhtar/aios/docs/notion/search/semantic_memory.md) - Qdrant schemas.

---

## 1. Hybrid Search Architecture

Lexical searches (SQLite FTS5) are fast and exact, while semantic searches (Qdrant) capture context and synonyms. To combine the strengths of both methods, the Personal AI OS uses a **Parallel Hybrid Search Engine**:

```
                              [User Search Query]
                               /               \
                              /                 \
                             v                   v
                     [SQLite FTS5]           [Qdrant DB]
                     Lexical Search         Semantic Search
                           |                       |
                     - Raw Rank Lists        - Similarity Scores
                     - Sorted by BM25        - Cosine Vectors
                           \                       /
                            \                     /
                             v                   v
                         [Reciprocal Rank Fusion]
                                    |
                                    v
                           [Ranked Output Hits]
```

---

## 2. Reciprocal Rank Fusion (RRF) Algorithm

Because BM25 ranks and cosine similarity scores have different scale distributions, they cannot be merged by simple addition. Instead, the system uses the **Reciprocal Rank Fusion (RRF)** algorithm. 

RRF scores documents based on their position in each search method's results:

$$\text{RRF\_Score}(d) = \sum_{m \in \text{Models}} \frac{1}{k + \text{rank}_m(d)}$$

* $m$: The search model (Lexical or Semantic).
* $\text{rank}_m(d)$: The 1-based index rank of document $d$ in model $m$.
* $k$: A constant parameter that dampens the influence of outlier high-ranked documents (default: **$60$**).

---

## 3. Python Rank Merger Implementation

The fusion ranker is implemented under `aios.providers.notion.search.fusion`:

```python
from typing import List, Dict, Any

class ReciprocalRankFusion:
    def __init__(self, k: int = 60):
        self.k = k

    def fuse_results(
        self, 
        lexical_hits: List[Dict[str, Any]], 
        semantic_hits: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge lexical and semantic search hits using the RRF algorithm."""
        rrf_scores: Dict[str, float] = {}
        document_registry: Dict[str, Dict[str, Any]] = {}

        # Process Lexical Hits (BM25 Sorted)
        for rank, hit in enumerate(lexical_hits, start=1):
            doc_id = hit["document_id"]
            document_registry[doc_id] = hit
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (self.k + rank))

        # Process Semantic Hits (Cosine Similarity Sorted)
        for rank, hit in enumerate(semantic_hits, start=1):
            doc_id = hit["document_id"]
            if doc_id not in document_registry:
                document_registry[doc_id] = hit
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (self.k + rank))

        # Sort documents by their calculated RRF score
        sorted_doc_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

        merged_results = []
        for doc_id in sorted_doc_ids:
            doc = document_registry[doc_id]
            doc["rrf_score"] = rrf_scores[doc_id]
            merged_results.append(doc)

        return merged_results
```
