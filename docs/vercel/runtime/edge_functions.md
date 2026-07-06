# Edge Functions Specification & Middleware Spec
**Sprint 13 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define Edge Runtime Deno parameters, middleware configurations, and geo-routing settings.
* **Scope**: Governs Deno parameters, middleware rules, and geo-routing logs.
* **Audience**: Systems Engineers, DBAs, and Lead Developers.
* **Related Documents**:
  * [vercel/capabilities.md](file:///Users/anzarakhtar/aios/docs/vercel/capabilities.md) - Capabilities.
  * [vercel/runtime/serverless_functions.md](file:///Users/anzarakhtar/aios/docs/vercel/runtime/serverless_functions.md) - Serverless functions.

---

## 1. Edge Runtime Configurations

Edge Functions run in Vercel's Edge Network, utilizing Vercel's Deno-based runtime:
* **Middleware Configurations**: Audits `middleware.ts` configurations, ensuring path matchers are configured to run only on targeted paths, preventing unnecessary executions on static assets.
* **Geo-Routing Settings**: Inspects routing parameters (`x-vercel-ip-country`, `x-vercel-ip-city`), validating geo-routing behavior.
* **Metadata Logging**: Maps edge function names and deployment details to the SQLite database, updating the catalog.
