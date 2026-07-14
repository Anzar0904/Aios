# Document Engine Guide

The Document Engine registers and indexes generated manuals in the AI OS.

---

## 1. Database Schema

Seeded in `~/.aios_documentation.db`:

```sql
CREATE TABLE documents (
    document_id      TEXT PRIMARY KEY,
    title            TEXT NOT NULL,
    doc_type         TEXT NOT NULL, -- readme|architecture|api_docs etc.
    content          TEXT NOT NULL DEFAULT '',
    project_id       TEXT NOT NULL DEFAULT '',
    owner            TEXT NOT NULL DEFAULT '',
    status           TEXT NOT NULL DEFAULT 'draft', -- draft|published|archived
    version          INTEGER NOT NULL DEFAULT 1,
    created_at       REAL NOT NULL,
    updated_at       REAL NOT NULL,
    related_entities TEXT NOT NULL DEFAULT '[]' -- JSON list
);
```

---

## 2. Capabilities

- **Versioning**: Saving a document with an existing `document_id` automatically increments its version count.
- **Search Engine**: Searches match search words inside both title and content fields using SQLite keyword operators.

---

## 3. CLI Management

```bash
# Search document logs by keyword
aios docs search "API"
```
