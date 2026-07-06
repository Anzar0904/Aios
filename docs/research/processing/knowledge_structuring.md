# Knowledge Structuring & Evidence Graph Spec
**Sprint 11 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define database schemas, Qdrant layouts, and connection structures for mapping research documents to the local knowledge base.
* **Scope**: Governs SQL tables, vector collections, and relationship mappings.
* **Audience**: DBAs, Search Engineers, and Quality Auditors.
* **Related Documents**:
  * [research/architecture.md](file:///Users/anzarakhtar/aios/docs/research/architecture.md) - Database architecture.
  * [research/processing/relationship_extraction.md](file:///Users/anzarakhtar/aios/docs/research/processing/relationship_extraction.md) - Relationship extraction.

---

## 1. Relational Database Knowledge Schemas

Processed research documents, concepts, and relationships are stored in the local SQLite/PostgreSQL database, preparing the data structure for the future **Evidence Graph**:

```sql
-- 1. Concepts Table (Core technical entities and definitions)
CREATE TABLE IF NOT EXISTS research_concepts (
    concept_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    concept_name TEXT NOT NULL,
    definition TEXT,
    FOREIGN KEY(document_id) REFERENCES research_documents(document_id) ON DELETE CASCADE
);

-- 2. Evidence Table (Supporting facts, constraints, and code snippets)
CREATE TABLE IF NOT EXISTS concept_evidences (
    evidence_id TEXT PRIMARY KEY,
    concept_id TEXT NOT NULL,
    section_title TEXT NOT NULL,
    evidence_statement TEXT NOT NULL,
    code_snippet TEXT,
    verification_status TEXT CHECK(verification_status IN ('UNVERIFIED', 'VERIFIED', 'CONFLICTING')) DEFAULT 'UNVERIFIED',
    FOREIGN KEY(concept_id) REFERENCES research_concepts(concept_id) ON DELETE CASCADE
);

-- 3. Relationships Table (Directed graph edges connecting concepts)
CREATE TABLE IF NOT EXISTS concept_relationships (
    relation_id TEXT PRIMARY KEY,
    source_concept_id TEXT NOT NULL,
    target_concept_id TEXT NOT NULL,
    relation_type TEXT CHECK(relation_type IN ('EXTENDS', 'DEPENDS_ON', 'REQUIRES', 'CONFLICTS_WITH', 'RESOLVES')) NOT NULL,
    FOREIGN KEY(source_concept_id) REFERENCES research_concepts(concept_id) ON DELETE CASCADE,
    FOREIGN KEY(target_concept_id) REFERENCES research_concepts(concept_id) ON DELETE CASCADE,
    UNIQUE(source_concept_id, target_concept_id, relation_type)
);
```

---

## 2. Qdrant Concept Indexing

Concepts and evidence statements are embedded and saved to the **`research_memory`** collection in Qdrant:
* **Vector Dimensions**: 384 dimensions.
* **Payload Fields**:
  ```json
  {
    "workspace_id": "global_or_profile_id",
    "source": "research",
    "concept_id": "concept_uuid",
    "concept_name": "RRF Hybrid Search",
    "evidence_text": "BM25 keyword ranks and vector similarity are fused using k=60 RRF.",
    "source_uri": "https://ai-os.org/docs/search/hybrid_search.md"
  }
  ```

---

## 3. Evidence Graph Integration

This structured schema provides the foundation for the future **Evidence Graph**:
* **Graph Traversal**: Agents can query SQLite to find all relationships (e.g. locating all libraries that `CONFLICTS_WITH` Python 3.7).
* **Direct Context Injections**: When an agent encounters a concept (e.g. `NotionProvider`), the system retrieves its linked evidence statements and injects them directly into the context window, improving code generation accuracy.
