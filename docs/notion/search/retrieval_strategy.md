# Notion Intelligence — Context Retrieval Strategy
**Sprint 9 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define prompt context compilation rules, maximum token budgets, similarity thresholds, and sorting parameters for query retrieval.
* **Scope**: Governs Python query parsers, context compiler classes, and OmniRoute parameters.
* **Audience**: AI Prompt Engineers, Integration Developers, and Systems Architects.
* **Related Documents**:
  * [notion/search/hybrid_search.md](file:///Users/anzarakhtar/aios/docs/notion/search/hybrid_search.md) - RRF rank merger models.
  * [docs/04_AI_MODEL_STRATEGY.md](file:///Users/anzarakhtar/aios/docs/04_AI_MODEL_STRATEGY.md) - Core system context budgets.

---

## 1. Context Retrieval Pipeline

When a local service (like the `Brain` orchestrator) queries the database to build context for LLM prompts, it follows a structured retrieval pipeline:

```
 [User Query / Target Objective]
               |
               v
 [NotionSearchService.search()] ===> Performs Lexical + Semantic Search
               |
               v
 [RRF Rank Merger Engine] ===> Combines & Ranks Results
               |
               v
 [Context Assembly Evaluator] ===> Applies Thresholds & Token Budgets
               |
               v
 [Markdown Prompt String] ===> Appended directly to LLM Prompt Context
```

---

## 2. Thresholds and Filtering

To ensure context relevance and prevent prompt clutter:
* **Cosine Similarity Threshold**: Points returned from Qdrant must have a similarity score of **$\ge 0.75$**. Low-scoring points are discarded.
* **RRF Score Threshold**: Merged hits are filtered using a relative RRF threshold to exclude tail results.
* **Workspace Scoping Filter**: Hits originating from inactive workspaces are excluded.

---

## 3. Context Token Budgets

The amount of Notion context appended to an LLM prompt is controlled by a token budget:

```
+------------------+------------------------+---------------------------------------+
| Query Category   | Target Token Budget    | Max Retrieval Hits Count              |
+------------------+------------------------+---------------------------------------+
| Daily Status     | 1,500 Tokens           | Top 3 Page Summaries / To-Do items    |
+------------------+------------------------+---------------------------------------+
| Scoping / Design | 3,000 Tokens           | Top 6 Structural Design Chunks        |
+------------------+------------------------+---------------------------------------+
| Code Audits      | 4,000 Tokens           | Top 8 Code Blocks / Review Threads    |
+------------------+------------------------+---------------------------------------+
```

### Context Formatting
Merged hits are formatted into Markdown text sections before injection:
```markdown
---
Source: Notion Page (Notion Integration Design)
Last Modified: 2026-07-06T18:49:00Z
Relevance Score: 0.89
---
This document defines the sync state machine...
```

---

## 4. Sorting and Deduplication

* **Deduplication**: If multiple retrieved chunks belong to the same page, the indexer groups them to reconstruct the original document flow rather than displaying fragmented sections.
* **Sorting Policy**: Chunks are sorted first by parent page hierarchy, and then by their sequence order (`chunk_index` metadata property). This preserves logical reading order for the LLM.
