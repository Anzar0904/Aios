# User Authentication Flows Spec
**Sprint 12 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define user session states, multi-factor triggers, and authentication redirect parameters.
* **Scope**: Governs login/signup schemas, OAuth integrations, and verification logs.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [supabase/capabilities.md](file:///Users/anzarakhtar/aios/docs/supabase/capabilities.md) - Capabilities.
  * [supabase/security/auth_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/security/auth_intelligence.md) - Auth intelligence.

---

## 1. Authentication Flow Pipeline

The system maps user authentication flows to verify security and prevent session leaks:

```
[User Action: Login/Signup]
            |
            v
[Stage 1: Credentials Check] ===> Validate email/password or OAuth scopes
            |
            v
[Stage 2: Verification Check]
            - Requires email verification if enabled.
            - Redirects to allowed URL only.
            |
            v
[Stage 3: Multi-Factor Authentication (MFA)]
            - Checks for active TOTP setup.
            - Prompts for MFA token if enabled.
            |
            v
[Stage 4: Token Generation] ===> Generates JWT and stores refresh token
```

---

## 2. MFA & OAuth Security Auditing

* **MFA Level Enforcement**: The system audits configurations to ensure sensitive actions (e.g. updating billing details or deleting projects) require Multi-Factor Authentication (`aal2` context level).
* **OAuth Scopes Check**: Inspects OAuth provider configurations to verify requests are restricted to minimal user data scopes (e.g. `email` and `profile`).
* **Redirect Validation**: Checks auth redirect logs to ensure URLs are restricted to verified project domains, blocking open redirects.
