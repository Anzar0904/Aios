# Dynamic RLS Policy Validation Spec
**Sprint 12 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define verification steps for RLS policies, mocking token schemas, and testing policy conditions.
* **Scope**: Governs RLS test suites, mock builders, and transaction validators.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [supabase/security_model.md](file:///Users/anzarakhtar/aios/docs/supabase/security_model.md) - SQL security.
  * [supabase/security/rls_analysis.md](file:///Users/anzarakhtar/aios/docs/supabase/security/rls_analysis.md) - RLS analysis.

---

## 1. Local RLS Policy Testing

To verify RLS policy security locally, the **Policy Validation** engine runs queries within transaction wrappers under simulated user roles, rollback changes when complete:

```
[Start Transaction]
          |
          v
[Mock Auth Context] ===> Set local config variables (auth.uid, auth.role, JWT claims)
          |
          v
[Execute Test Query] ===> Run SELECT/INSERT/UPDATE queries
          |
          +--- Query succeeds: Access allowed.
          +--- Query fails: Access blocked.
          |
          v
[Rollback Transaction]
```

---

## 2. Mocking JWT Context Variables

The validation engine mocks JWT session contexts in PostgreSQL to test policies:
* **Simulating User ID**: Sets the session variable to simulate a specific user:
  `SET LOCAL request.jwt.claim.sub = 'user-uuid-value';`
* **Simulating User Role**: Sets the session role:
  `SET LOCAL request.jwt.claim.role = 'authenticated';`
* **Testing Policies**: Executes test queries to verify that:
  - Users can read only their own data.
  - Non-authenticated users are blocked.
  - Admins can manage all records.
