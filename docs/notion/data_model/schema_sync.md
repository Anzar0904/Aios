# Notion Intelligence — Schema Synchronization
**Sprint 9 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define database schema validation rules, version control tracking, database property drift checks, and error handling for synchronization.
* **Scope**: Governs schema parsing algorithms, schema migration triggers, and synchronization warning logs.
* **Audience**: Systems Integrators, DBAs, and Security Architects.
* **Related Documents**:
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - Database mappings.
  * [notion/data_model/database_model.md](file:///Users/anzarakhtar/aios/docs/notion/data_model/database_model.md) - Database models.

---

## 1. Schema Synchronization & Verification

Because database definitions inside Notion are mutable and can be altered by users in their browsers (e.g. renaming columns, changing property types), the Personal AI OS runs a **Schema Verification Check** before executing sync operations.

```
 [Initiate Table Sync]
          |
          v
 [Fetch Notion Schema]  =====> Matches Schema in Local Registry
          |
  [Compare Column Maps]
         /     \
    Matches    Drift Detected
      /           \
     v             v
[Run Sync]   [Log Warning & Run Migration Policy]
```

---

## 2. Schema Drift Detection

Before querying or updating a database, the system pulls database metadata and compares it to the local cache:
1. **Name Mismatches**: A column mapping has changed names (e.g., `Priority` -> `Task Priority`).
2. **Type Drifts**: A property type has changed (e.g., a column changed from a `number` to a `select`).
3. **Missing Columns**: Expected fields have been deleted from Notion.
4. **Extra Columns**: Unmapped new columns have been added to Notion.

---

## 3. Drift Resolution Policies

The `SchemaSyncManager` handles drifts based on three configuration modes:

### 3.1 Mode A: Strict Validation (Default for Automated Systems)
If any schema discrepancy is found:
* The sync halts immediately.
* Log a high-severity alert to `logs/notion_sync.log`.
* Display a warning in the REPL console:
  ```
  [Notion Schema Alert]
  Schema drift detected on Database 'Job Applications' (ID: d9fa12...):
  - Expected column 'Match Score' (type: number) is missing.
  - Unexpected column 'Recruiter Notes' (type: rich_text) is present.
  
  Synchronization suspended. To ignore, run 'notion database sync --policy permissive'.
  ```

### 3.2 Mode B: Permissive Validation (Log & Ignore)
* Mismatched expected columns are treated as `None` or omitted from local updates.
* Unexpected columns are stored inside a generic `extra_properties` JSON column in the local database.
* The system logs a warning but continues synchronizing page content.

### 3.3 Mode C: Auto-Evolution (Local-First Push)
If the local OS model specifies a column schema that is missing from the remote Notion database:
* The `SchemaSyncManager` initiates a schema update request to Notion:
  * Send a `PATCH` request to `https://api.notion.com/v1/databases/{database_id}`.
  * **Payload**:
    ```json
    {
      "properties": {
        "Match Score": {
          "number": {
            "format": "number"
          }
        }
      }
    }
    ```
  * Update the local database schema cache on success.
* *Note: Column type conversions are blocked by Notion's API. Changing a column type (e.g. from `rich_text` to `number`) is not permitted and requires creating a new property.*
