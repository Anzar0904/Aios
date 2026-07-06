# Domain Routing & Redirects Spec
**Sprint 13 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define domain metadata audits, custom routing mappings, and redirect checks.
* **Scope**: Governs domain lists, redirect rules, and routing configurations.
* **Audience**: Systems Engineers, DBAs, and Lead Developers.
* **Related Documents**:
  * [vercel/capabilities.md](file:///Users/anzarakhtar/aios/docs/vercel/capabilities.md) - Capabilities.
  * [vercel/environment/environment_management.md](file:///Users/anzarakhtar/aios/docs/vercel/environment/environment_management.md) - Environment management.

---

## 1. Domain Configuration Maps

The **Domain Intelligence** module audits active domains linked to Vercel projects:
* **Custom Domains**: Queries Vercel APIs to retrieve custom domain records, mapping DNS alias routes in the local SQLite database:
  ```sql
  CREATE TABLE IF NOT EXISTS project_domains (
      domain_name TEXT PRIMARY KEY,
      project_id TEXT NOT NULL,
      redirect_target TEXT,                -- Target domain if redirect configured
      verified BOOLEAN NOT NULL DEFAULT FALSE,
      cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(project_id) REFERENCES vercel_projects(project_id) ON DELETE CASCADE
  );
  ```
* **Redirect Auditing**: Inspects redirect configurations, verifying that redirects are configured correctly to prevent redirect loops.
