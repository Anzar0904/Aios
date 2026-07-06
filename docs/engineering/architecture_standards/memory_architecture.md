# Memory & Persistence Architecture Standards
**Engineering Bible — Milestone 3**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. The Tiered Memory Hierarchy

The Personal AI OS implements a tiered memory system to balance context relevance, token usage, and persistence duration.

```
                  +-----------------------------------+
                  |        PERMANENT MEMORY           |
                  |  (User Profile, Constitution)     |
                  +----------------─┬────────────────-+
                                    │
                                    ▼
                  +----------------────────────────---+
                  |        LONG-LIVED MEMORY          |
                  |  (Project History, Metrics, ADRs) |
                  +----------------─┬────────────────-+
                                    │
                                    ▼
                  +----------------────────────────---+
                  |        SHORT-LIVED MEMORY         |
                  |  (Dialogs, Tool Outputs, Traces)  |
                  +----------------────────────────---+
```

### Memory Tiers
1. **Permanent Memory**:
   * **Duration**: Infinite (never expires).
   * **Content**: Core user identity, system values, user profile documents, and personal configuration files.
2. **Long-Lived Memory**:
   * **Duration**: 1 to 3 years.
   * **Content**: Project metadata, git history insights, engineering profiles, system design logs, and technical decisions.
3. **Short-Lived Memory**:
   * **Duration**: Days or weeks (automatically pruned).
   * **Content**: Chat dialogue lines, terminal command outputs, action logs, and system error traces.

---

## 2. Dynamic Context Assembly

To keep LLM prompt token counts within limits, the Memory Service dynamically constructs prompt contexts:
* **Workspace Resolution**: Reads the current directory path (CWD) and git status to resolve the active repository context.
* **Semantic Recall**: Queries semantic databases for entries that match active workflow topics.
* **Relevance Assembly**: Combines active dialogue turns, relevant semantic results, and permanent guidelines into a consolidated, token-bounded system prompt.

---

## 3. Storage Tier Specifications

The system utilizes three distinct persistence technologies:

### 1. Vector Database Tier (Qdrant)
* **Purpose**: Handles semantic search, semantic similarity matching, and conceptual recall.
* **Structure**: Manages nine distinct collections and repositories (e.g., code snippets, project documents, search cache, insights).
* **Validation**: Input vectors must pass validation checks to prevent invalid NaN embeddings from entering collections.

### 2. Relational Database Tier (PostgreSQL)
* **Purpose**: Serves as the primary source of truth for structured relational data.
* **Scope**: Persists session details, task history lists, audit trail logs, and workspace configuration properties.
* **Integrity**: Enforces relational constraints and transaction safety.

### 3. High-Speed Cache & Coordination Tier (Redis)
* **Purpose**: Provides quick temporary storage, session caching, and runtime coordination.
* **Scope**: Manages short-term caches, rate-limiting counters, mutual locks, and message queues.
* **Fallback Gate**: If the Redis service goes offline, temporary cache operations fall back to in-memory dictionaries, ensuring uninterrupted execution.

---

*Engineering Bible Architecture Standards · Personal AI OS · Sprint 8 M3 · Governed by [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md)*
