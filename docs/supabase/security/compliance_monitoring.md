# Compliance Monitoring & Drift Detection Spec
**Sprint 12 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define configuration drift checks, compliance logs, and security alert triggers.
* **Scope**: Governs drift checkers, compliance records, and alert systems.
* **Audience**: Quality Auditors, Systems Architects, and Security Engineers.
* **Related Documents**:
  * [supabase/security/auth_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/security/auth_intelligence.md) - State drift abstraction.
  * [supabase/security/security_auditing.md](file:///Users/anzarakhtar/aios/docs/supabase/security/security_auditing.md) - Security auditing.

---

## 1. Schema & Security Drift Monitor

The **Compliance Monitoring** engine runs background checks to detect discrepancies between local configurations and the remote Supabase state:

```
[Start Compliance Check]
            |
            v
[Scan Local Configs] (Desired State) <===> [Scan Supabase Instance] (Observed State)
            |
            v
[Compute Configuration Drift]
            - Checks RLS state discrepancies.
            - Compares policy expressions (USING / WITH CHECK).
            - Audits GoTrue authentication settings.
            |
            v
[Register Drift Alert] ===> Print warning in REPL & generate SQL recommendation
```

---

## 2. Drift Alerts & Recommendations

When configuration drift is detected:
1. **Log Alert**: Logs details (including parameter differences and timestamps) to the database.
2. **Generate Recommendation**: Compiles SQL statements to resolve the drift:
   - For disabled RLS: `ALTER TABLE [table_name] ENABLE ROW LEVEL SECURITY;`
   - For missing policies: Generates corresponding `CREATE POLICY` statements.
3. **Execution Plan**: Bundles recommendations into a migration file, requiring developer approval before running.
