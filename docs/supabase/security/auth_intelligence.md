# Authentication Intelligence & Configuration State Spec
**Sprint 12 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define GoTrue auth configurations auditing, JWT sessions checks, and state drift abstractions.
* **Scope**: Governs auth configurations, session verifiers, and state models.
* **Audience**: Security Auditors, System Architects, and Lead Developers.
* **Related Documents**:
  * [supabase/security_model.md](file:///Users/anzarakhtar/aios/docs/supabase/security_model.md) - Security model.
  * [supabase/security/README.md](file:///Users/anzarakhtar/aios/docs/supabase/security/README.md) - Security navigation hub.

---

## 1. The Configuration State Abstraction

To track and resolve database security issues, the AI OS uses a structured state evaluation pipeline:

```
[Infrastructure Resource]
          |
          +---> Desired State: Expected configuration defined in local schema settings.
          +---> Observed State: Actual configuration parsed from Supabase.
          |
          v
[Compute Drift] ===> Identify differences (e.g. RLS disabled on table X)
          |
          v
[Recommendation] ===> Generate SQL fix (e.g. "ALTER TABLE X ENABLE ROW LEVEL SECURITY;")
          |
          v
[Execution Plan] ===> Apply changes via dry-run checked migrations
```

---

## 2. GoTrue Auth Config Auditing

The **Authentication Intelligence** module inspects the authentication service (GoTrue) parameters:
* **JWT Lifetimes**: Flags configurations where token expiration times exceed **3600 seconds** (1 hour) to limit exposure.
* **MFA Status**: Checks if Multi-Factor Authentication is enabled for security-critical roles.
* **SMTP Settings**: Verifies SMTP server settings to ensure emails are sent through verified custom domains.
* **OAuth Settings**: Audits allowed redirect URLs, checking for wildcard redirects (`*`) that could allow authorization code leakage.
* **Metadata Logging**: Saves audited parameters to the SQLite database, updating the security dashboard.
