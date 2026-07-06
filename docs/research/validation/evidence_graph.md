# Evidence Graph Architecture Spec
**Sprint 11 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define graph node schemas, relationships edges, and topological mapping algorithms.
* **Scope**: Governs SQL graph registries, Qdrant payload filters, and network connections.
* **Audience**: Systems Architects, DBAs, and Lead Developers.
* **Related Documents**:
  * [research/processing/knowledge_structuring.md](file:///Users/anzarakhtar/aios/docs/research/processing/knowledge_structuring.md) - Database schemas.
  * [research/validation/README.md](file:///Users/anzarakhtar/aios/docs/research/validation/README.md) - Validation navigation hub.

---

## 1. Evidence Graph Topology

The **Evidence Graph** is a directed acyclic graph ($G_{evid} = (V_{nodes}, E_{edges})$) that tracks technical claims and their supporting documentation. The model extends the system hierarchy:

**KnowledgeNode → Fact → Evidence → Confidence → Version**

```
  +----------------------+
  |    KnowledgeNode     | (System cognitive context block)
  +----------------------+
            | (1-to-1)
            v
  +----------------------+
  |       Fact           | (Verified core statement)
  +----------------------+
            | (SUPPORTED_BY)
            v
  +----------------------+
  |     Evidence         | (Document excerpt / test verification)
  +----------------------+
            | (HAS_CONFIDENCE)
            v
  +----------------------+
  |     Confidence       | (Credibility score & decay index)
  +----------------------+
            | (HAS_VERSION)
            v
  +----------------------+
  |      Version         | (Revision logs history)
  +----------------------+
```

---

## 2. Graph Nodes & Edges Definitions

### 2.1 Nodes ($V_{nodes}$)
* **`KnowledgeNode`**: Represents a concept cached in Qdrant/SQLite.
* **`FactNode`**: Stores verified assertions (e.g. "RRF hybrid search combines keyword and vector matches").
* **`EvidenceNode`**: Stores citations (e.g. standard file paths, URL links, specific code outputs).
* **`ConfidenceNode`**: Stores dynamic confidence scores (0.0 to 1.0) and validation logs.
* **`VersionNode`**: Stores timestamped revision records and deprecation flags.

### 2.2 Edges ($E_{edges}$)
* **`SUPPORTED_BY`**: FactNode $\rightarrow$ EvidenceNode. Links claims to their documentation sources.
* **`CONTRADICTS`**: FactNode $\rightarrow$ FactNode. Links conflicting statements, triggering verification checks.
* **`VERSION_OF`**: VersionNode $\rightarrow$ FactNode. Maps the version history of a claim.
