# Citation Management & Evidence Mapping Spec
**Sprint 11 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define citation record structures, markdown citation formatting, and source verification mapping.
* **Scope**: Governs citation tables, document references, and coordinate logs.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [research/capabilities.md](file:///Users/anzarakhtar/aios/docs/research/capabilities.md) - Capabilities domains.
  * [research/validation/evidence_graph.md](file:///Users/anzarakhtar/aios/docs/research/validation/evidence_graph.md) - Graph structure.

---

## 1. Citation Record Schema

To ensure transparency, every verified Fact in the database must reference its source document. The SQLite database tracks these citations:

```sql
CREATE TABLE IF NOT EXISTS fact_citations (
    citation_id TEXT PRIMARY KEY,
    fact_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    section_title TEXT NOT NULL,
    exact_text_snippet TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    FOREIGN KEY(fact_id) REFERENCES codebase_facts(fact_id) ON DELETE CASCADE,
    FOREIGN KEY(document_id) REFERENCES research_documents(document_id) ON DELETE CASCADE
);
```

---

## 2. Agent Report Citations Formatting

When research agents publish reports (to local files or Notion databases), they use a standardized citation format:
* **Inline Citations**: Appends numeric bracket tags (e.g. `[1]`, `[2]`) directly to claims.
* **Sources Table**: Inserts a "Source Citations" section at the end of the document listing the referenced source titles, authors, URLs, and retrieval dates:
  ```markdown
  ## Source Citations
  * [1] IETF RFC 7519: JSON Web Token - Section 4.1 (https://rfc-editor.org/rfc/rfc7519.txt)
  * [2] Notion Developer Docs: Create Page (https://developers.notion.com/reference/post-page)
  ```
