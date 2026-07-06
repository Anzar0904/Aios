# Auth, RLS & Security Intelligence — Navigation Hub
**Sprint 12 · Milestone 3** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory houses the **Auth, RLS & Security Intelligence** specifications for the Personal AI OS.
> It builds upon the [Supabase Foundation](file:///Users/anzarakhtar/aios/docs/supabase/README.md) and [Database Intelligence](file:///Users/anzarakhtar/aios/docs/supabase/database/README.md) documents.
>
> In accordance with local-first system design guidelines, all policy validation checks, authorization graphs, security audits, and configuration drift monitors are processed locally, keeping the AI OS kernel as the reasoning and execution core.

---

## Documents

| Document | Purpose |
|---|---|
| [auth_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/security/auth_intelligence.md) | GoTrue settings audits, JWT session lifecycles, and the Desired/Observed State abstraction |
| [rls_analysis.md](file:///Users/anzarakhtar/aios/docs/supabase/security/rls_analysis.md) | Row-Level Security checks, table policy extractions, and PostgreSQL catalog queries |
| [policy_validation.md](file:///Users/anzarakhtar/aios/docs/supabase/security/policy_validation.md) | Dynamic policy validation, compiling local mock JWT context, and testing policy criteria |
| [authentication_flows.md](file:///Users/anzarakhtar/aios/docs/supabase/security/authentication_flows.md) | User signup/signin lifecycles, MFA checks, and OAuth provider scopes |
| [authorization_graph.md](file:///Users/anzarakhtar/aios/docs/supabase/security/authorization_graph.md) | Directed authorization graphs mapping roles, scopes, RLS filters, and table schemas |
| [security_auditing.md](file:///Users/anzarakhtar/aios/docs/supabase/security/security_auditing.md) | Scanning public schemas, tracking public profiles, and flagging permissive policies |
| [compliance_monitoring.md](file:///Users/anzarakhtar/aios/docs/supabase/security/compliance_monitoring.md) | Audit logging, configuration drift detection, and automated security reporting |

---

## Reading Order

1. **[`auth_intelligence.md`](file:///Users/anzarakhtar/aios/docs/supabase/security/auth_intelligence.md)**: Start here to study auth auditing and the Desired/Observed State schema.
2. **[`rls_analysis.md`](file:///Users/anzarakhtar/aios/docs/supabase/security/rls_analysis.md)** & **[`policy_validation.md`](file:///Users/anzarakhtar/aios/docs/supabase/security/policy_validation.md)**: Explore RLS policies and validation steps.
3. **[`authentication_flows.md`](file:///Users/anzarakhtar/aios/docs/supabase/security/authentication_flows.md)** & **[`authorization_graph.md`](file:///Users/anzarakhtar/aios/docs/supabase/security/authorization_graph.md)**: Learn about authentication steps and roles mapping.
4. **[`security_auditing.md`](file:///Users/anzarakhtar/aios/docs/supabase/security/security_auditing.md)** & **[`compliance_monitoring.md`](file:///Users/anzarakhtar/aios/docs/supabase/security/compliance_monitoring.md)**: Review security auditing and configuration drift detection.
