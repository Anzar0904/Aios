# Relationship & Dependency Mapping Spec
**Sprint 12 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define database relationship extraction queries, foreign key maps, and cycle detectors.
* **Scope**: Governs key connections, relationship tables, and dependency loops checkers.
* **Audience**: DBAs, Systems Architects, and Lead Developers.
* **Related Documents**:
  * [supabase/database/schema_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/database/schema_intelligence.md) - Schema intelligence.
  * [supabase/database/table_analysis.md](file:///Users/anzarakhtar/aios/docs/supabase/database/table_analysis.md) - Table analysis.

---

## 1. Relationship Extraction

The **Relationship Mapping** engine queries system catalogs to identify primary key and foreign key constraints, constructing a database dependency map:

```sql
SELECT kcu.table_name AS source_table,
       kcu.column_name AS source_column,
       ccu.table_name AS target_table,
       ccu.column_name AS target_column,
       rc.delete_rule AS cascade_rule
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.referential_constraints rc ON tc.constraint_name = rc.constraint_name
JOIN information_schema.constraint_column_usage ccu ON rc.unique_constraint_name = ccu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = :schema_name;
```

---

## 2. Cascade Actions & Cycle Detection

* **Cascade Checks**: Identifies cascade deletion rules (`ON DELETE CASCADE`, `ON DELETE SET NULL`), checking if child tables are cleaned up automatically when parent rows are deleted.
* **Cyclic Dependency Checks**: Uses Tarjan's cyclic dependency algorithm to detect loops in foreign key relations (e.g. Table A $\rightarrow$ Table B $\rightarrow$ Table A), alerting the developer to potential locking issues.
* **Metadata Registration**: Stores the extracted relationships in the SQLite schema database, helping agents generate valid join queries.
