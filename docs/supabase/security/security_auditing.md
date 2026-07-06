# Database Security Auditing Spec
**Sprint 12 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define database security audits, query scanners, and safety checklist scripts.
* **Scope**: Governs RLS audits, schema verifiers, and security alerts.
* **Audience**: Security Auditors, System Architects, and Integration Developers.
* **Related Documents**:
  * [supabase/security_model.md](file:///Users/anzarakhtar/aios/docs/supabase/security_model.md) - Security model.
  * [supabase/security/rls_analysis.md](file:///Users/anzarakhtar/aios/docs/supabase/security/rls_analysis.md) - RLS analysis.

---

## 1. Security Vulnerability Checks

The **Security Auditing** engine runs query checks against Supabase schemas to identify vulnerabilities:

```
+------------------------------------+------------------------------------+----------+
| Security Check                     | Target Result                      | Priority |
+------------------------------------+------------------------------------+----------+
| 1. Disabled RLS Checker            | 0 tables with RLS disabled         | Critical |
+------------------------------------+------------------------------------+----------+
| 2. Wildcard Policies (ALL)         | 0 ALL policies without role check  | High     |
+------------------------------------+------------------------------------+----------+
| 3. Security Definer Functions      | Audit functions using definer role | High     |
+------------------------------------+------------------------------------+----------+
| 4. Schema Public Exposure          | Verify public tables metadata      | Critical |
+------------------------------------+------------------------------------+----------+
```

---

## 2. Automated Vulnerability Scanners

* **Disabled RLS scan**: Queries catalog tables to locate any table with RLS disabled:
  ```sql
  SELECT schemaname, tablename FROM pg_tables
  WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
  AND rowsecurity = false;
  ```
* **Security Definer Check**: Scans user functions to locate any function using `SECURITY DEFINER` (which executes with creator privileges), warning if RLS checks are bypassed.
* **Wildcard Policies Check**: Identifies policies configured with `FOR ALL` or without role constraints, warning of overly permissive access.
* **Vulnerability Logs**: Writes discovered vulnerabilities to `docs/supabase/scratch/security_alerts.log`.
