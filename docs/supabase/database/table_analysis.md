# Table & Column Analysis Spec
**Sprint 12 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define column metadata parsing, size estimations, and datatype validations.
* **Scope**: Governs column schemas, data types, and constraint checkers.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [supabase/capabilities.md](file:///Users/anzarakhtar/aios/docs/supabase/capabilities.md) - Capabilities matrix.
  * [supabase/database/schema_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/database/schema_intelligence.md) - Schema intelligence.

---

## 1. Table Inspections

The **Table Analysis** module inspects table structures to map column metadata and detect potential schema issues:
* **Size & Row Count Estimations**:
  ```sql
  SELECT pg_total_relation_size(quote_ident(table_schema) || '.' || quote_ident(table_name)) AS total_bytes,
         reltuples::bigint AS estimated_row_count
  FROM pg_class c
  JOIN pg_namespace n ON n.oid = c.relnamespace
  WHERE n.nspname = :schema_name AND c.relname = :table_name;
  ```
* **Column Definitions**: Extracts data types (e.g. `uuid`, `text`, `timestamp with time zone`), primary keys, default values, and nullable constraints from `information_schema.columns`.

---

## 2. JSONB Schema Verification

JSONB columns hold unstructured data but require validation to prevent application-level errors:
* **Check Constraints**: The analysis engine verifies if JSONB fields have validation constraints (e.g., verifying keys exist) applied:
  `ALTER TABLE profiles ADD CONSTRAINT check_metadata CHECK (jsonb_typeof(metadata->'age') = 'number');`
* **Local Payload Validation**: If a query contains JSONB inputs, the local AST checks the payload syntax against active schema specifications.
