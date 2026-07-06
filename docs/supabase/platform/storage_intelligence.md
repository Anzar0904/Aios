# Storage Intelligence & Configuration State Spec
**Sprint 12 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define storage bucket configurations, access policies, and asset management rules.
* **Scope**: Governs bucket schemas, asset metadata, and access rules.
* **Audience**: DBAs, Systems Engineers, and Lead Developers.
* **Related Documents**:
  * [supabase/capabilities.md](file:///Users/anzarakhtar/aios/docs/supabase/capabilities.md) - Capabilities.
  * [supabase/platform/edge_functions.md](file:///Users/anzarakhtar/aios/docs/supabase/platform/edge_functions.md) - Edge functions.

---

## 1. Storage Configuration States

Supabase Storage buckets are monitored using the configuration state model:
* **Infrastructure Resource**: Storage Bucket instance.
* **Desired State**: Expected configurations defined in local schema settings.
* **Observed State**: Actual active configuration and access rules retrieved from Supabase.
* **Drift**: Discrepancies between Desired and Observed states (e.g. private bucket is public).
* **Recommendation**: Suggested remediation (e.g. update bucket visibility to private).
* **Execution Plan**: Run DDL/API commands to align configurations with the desired state.

---

## 2. Storage Schema Mappings

Storage configurations are stored in the local SQLite catalog:

```sql
CREATE TABLE IF NOT EXISTS storage_buckets (
    bucket_id TEXT PRIMARY KEY,
    instance_id TEXT NOT NULL,
    bucket_name TEXT NOT NULL UNIQUE,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    max_file_size BIGINT,
    allowed_mime_types TEXT,             -- JSON array of allowed MIME types
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(instance_id) REFERENCES supabase_instances(instance_id) ON DELETE CASCADE
);
```

Discovered bucket metadata is indexed in Qdrant, helping agents generate valid upload requests.
