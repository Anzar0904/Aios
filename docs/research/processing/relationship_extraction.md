# Relationship Extraction Spec
**Sprint 11 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define relation data models, schema definitions, and dependency extraction rules.
* **Scope**: Governs entity relationships, database schemas, and validation links.
* **Audience**: Systems Architects, DBAs, and Lead Developers.
* **Related Documents**:
  * [workspace/project_discovery/dependency_graph.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/dependency_graph.md) - Graph dependencies.
  * [research/processing/entity_recognition.md](file:///Users/anzarakhtar/aios/docs/research/processing/entity_recognition.md) - Entity recognition.

---

## 1. Entity Relationship Schema

The **Relationship Extraction** module identifies links between extracted entities to construct a local knowledge topology:

```
[Entity A] ===(RELATION)===> [Entity B]
```

The system maps five core relationship types:
1. **`EXTENDS`**: Class inheritance connections (e.g. `NotionProvider EXTENDS KnowledgeProvider`).
2. **`DEPENDS_ON`**: Library or module requirements (e.g. `NotionProvider DEPENDS_ON urllib3`).
3. **`REQUIRES`**: API parameter constraints (e.g. `POST /v1/pages REQUIRES ParentID`).
4. **`CONFLICTS_WITH`**: Version incompatibilities (e.g. `Poetry 1.8 CONFLICTS_WITH Python 3.7`).
5. **`RESOLVES`**: Solutions to diagnostics (e.g. `ConventionalCommits RESOLVES CommitFormatError`).

---

## 2. Structural Parsing Rules

To extract relationships:
* **AST Mapping**: Inspects code examples in documentation to map actual class inheritances (`EXTENDS`) and method dependencies (`DEPENDS_ON`).
* **Text Analysis**: Analyzes text patterns to identify dependencies and version constraints (e.g., "This endpoint requires...", "Requires version X or later").
* **Schema Verification**: Maps parameter requirements directly from OpenAPI schema files.
