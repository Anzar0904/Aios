# Supabase Intelligence — Security Compliance
**Sprint 12 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Verify compliance of credential isolation, query AST blockers, policy test suites, and drift monitors.
* **Scope**: Governs key storage, query checks, and RLS validations.
* **Audience**: Quality Auditors, Systems Architects, and AI developers.
* **Related Documents**:
  * [supabase/security/README.md](file:///Users/anzarakhtar/aios/docs/supabase/security/README.md) - Security Intelligence hub.
  * [supabase/security_model.md](file:///Users/anzarakhtar/aios/docs/supabase/security_model.md) - Security model.

---

## 1. Compliance Audit Objectives

This audit verifies that the **Auth, RLS & Security Intelligence** layer protects sensitive API keys, validates SQL queries, tests RLS policies, and monitors configuration drift.

---

## 2. Security Verification Matrix

```
+------------------------------------+------------------------------------+----------+
| Security Requirement               | Verification Check                 | Status   |
+------------------------------------+------------------------------------+----------+
| 1. Key Vault Isolation             | Encrypts API and service role keys | PASS     |
|                                    | using SQLCipher.                   |          |
+------------------------------------+------------------------------------+----------+
| 2. AST Query Blockers              | Parses SQL queries and blocks      | PASS     |
|                                    | unauthorized DDL statements.       |          |
+------------------------------------+------------------------------------+----------+
| 3. Local RLS Policy Test Wrappers  | Simulates user roles and validates | PASS     |
|                                    | policy restrictions.               |          |
+------------------------------------+------------------------------------+----------+
| 4. Configuration Drift Monitors    | Detects RLS status and policy      | PASS     |
|                                    | differences across databases.      |          |
+------------------------------------+------------------------------------+----------+
```

---

## 3. Compliance Verification Details

### 3.1 Key Storage & Query Checking
* Encryption audits verify that API keys are stored securely using SQLCipher.
* AST checking tests verify that standard query tools block destructive statements (e.g. `DROP TABLE`), preventing SQL injection.

### 3.2 RLS Policies & Drift
* Local RLS tests verify that user sessions are mocked correctly, validating policy restrictions.
* Drift monitoring tests verify that configuration discrepancies (e.g. RLS disabled) are detected and logged.
