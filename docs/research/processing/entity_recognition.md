# Named Entity Recognition (NER) Spec
**Sprint 11 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define entity schemas, regex pattern recognizers, and class mappings for technical entities.
* **Scope**: Governs entity catalog models, syntax matches, and domain tags.
* **Audience**: Systems Integrators, DBAs, and Lead Developers.
* **Related Documents**:
  * [workspace/capabilities.md](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) - Workspace capabilities.
  * [research/processing/concept_extraction.md](file:///Users/anzarakhtar/aios/docs/research/processing/concept_extraction.md) - Concept extraction.

---

## 1. Technical Entity Schemas

When processing technical literature, the system extracts key programming and architectural entities, categorizing them using structured schemas:

```
+------------------+-----------------------+---------------------------------------+
| Entity Category  | Entity Type           | Representative Example                |
+------------------+-----------------------+---------------------------------------+
| Programming      | `LANGUAGE`            | Python, TypeScript, Go, Rust          |
|                  | `LIBRARY`             | pytest, poetry, pg_query, Qdrant      |
|                  | `CLASS`               | LocalKnowledgeHub, NotionProvider     |
|                  | `METHOD`              | sync_document, evaluate_consensus    |
+------------------+-----------------------+---------------------------------------+
| Interface & API  | `ENDPOINT`            | POST /v1/pages, GET /users/me         |
|                  | `PARAMETER`           | document_id, external_page_id        |
|                  | `PAYLOAD_SCHEMA`      | JSON Web Token claims structure       |
+------------------+-----------------------+---------------------------------------+
| Diagnostic       | `ERROR_CODE`          | HTTP 429, E0308, PytestCollectionError|
+------------------+-----------------------+---------------------------------------+
```

---

## 2. Extraction & Pattern Recognition Heuristics

The NER module uses a combination of regex patterns and local NLP models:
* **API Endpoints**: Matches standard HTTP patterns:
  `\b(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)\s+(/[a-zA-Z0-9_\-\.\/\{\}]+)\b`
* **Code Identifiers**: Extracts classes and methods using syntax rules (e.g. CamelCase strings for classes, snake_case with parenthesized parameters for methods).
* **Package/Library References**: Scans lockfile configurations and matches them against mentions in the text.
