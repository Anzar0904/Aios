# Edge Functions Specification & Configuration State Spec
**Sprint 12 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define Deno runtime parameters, edge function settings, and state drift mappings.
* **Scope**: Governs Deno parameters, environment variables, and state models.
* **Audience**: Systems Architects, DBAs, and Lead Developers.
* **Related Documents**:
  * [supabase/security/auth_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/security/auth_intelligence.md) - State drift abstraction.
  * [supabase/platform/README.md](file:///Users/anzarakhtar/aios/docs/supabase/platform/README.md) - Platform navigation hub.

---

## 1. Edge Function Configuration States

Edge Functions are managed using the system configuration state model:
* **Infrastructure Resource**: Deno Edge Function script.
* **Desired State**: Script source code, environment variables, and configuration settings defined in local folders.
* **Observed State**: Actual active configuration and deployment hash retrieved from Supabase.
* **Drift**: Discrepancies between local code/variables and the remote deployment.
* **Recommendation**: Suggested remediation (e.g. compile and deploy local updates).
* **Execution Plan**: Deploy the updated function code using Deno adapters.

---

## 2. Deno Runtime Auditing

The **Edge Functions** module inspects and audits Deno configurations:
* **Environment Variables**: Flags missing variables on the remote instance that are defined in local config files.
* **Execution Limits**:
  * Timeout: Max **15 seconds** per invocation.
  * Memory limit: Max **150MB** per function instance.
* **Metadata Logging**: Maps function names and deployment details to the SQLite database, updating the catalog.
