# Bucket Metadata & Policy Analysis Spec
**Sprint 12 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define bucket auditing rules, size estimations, and MIME type verifications.
* **Scope**: Governs bucket parameters, access policies, and size checkers.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [supabase/security/rls_analysis.md](file:///Users/anzarakhtar/aios/docs/supabase/security/rls_analysis.md) - RLS policies.
  * [supabase/platform/storage_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/platform/storage_intelligence.md) - Storage intelligence.

---

## 1. Bucket Inspections

The **Bucket Analysis** module audits storage bucket settings and access policies:
* **Size & File Count Audits**: Queries remote API metadata to track total consumed bytes and file counts.
* **MIME Types Validation**: Checks allowed MIME types (e.g. `image/png`, `application/pdf`), flagging buckets that allow any upload types (`*/*`) to prevent malicious script uploads.

---

## 2. Storage Policy Checks

Storage buckets use Row-Level Security (RLS) policies defined in the `storage.objects` table. The analysis engine:
* **Access Checks**: Verifies if read/write policies restrict access to authenticated users or object owners.
* **Public Bucket Audits**: Flags public buckets that allow write access to unauthenticated users, warning of potential security risks.
* **Recommendation Generation**: Generates SQL recommendations to fix insecure storage policies.
