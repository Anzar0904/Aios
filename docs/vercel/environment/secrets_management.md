# Secrets Management & Key Isolation Spec
**Sprint 13 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define environment variable encryption, secret scopes, and credential isolation.
* **Scope**: Governs secret configs, variables encryption, and access scopes.
* **Audience**: Security Auditors, System Architects, and Lead Developers.
* **Related Documents**:
  * [vercel/security_model.md](file:///Users/anzarakhtar/aios/docs/vercel/security_model.md) - Security model.
  * [vercel/environment/environment_management.md](file:///Users/anzarakhtar/aios/docs/vercel/environment/environment_management.md) - Environment management.

---

## 1. Secrets Vault & Variable Encryption

Environment variables often contain sensitive API keys and connection parameters:
* **AES-256-GCM Encryption**: Local copies of Vercel project environment variables are encrypted in SQLite using SQLCipher (AES-256-GCM).
* **Decryption Gate**: Decryption occurs only during sync cycles with Vercel APIs.

---

## 2. Environment Scopes Isolation

To prevent development database keys from leaking to production:
* **Explicit Targeting**: Environment variables are locked to specific Vercel environments (`production`, `preview`, `development`).
* **Supabase Synced Secrets**: Database connection strings retrieved from Supabase are mapped to Vercel production variables using encrypted pipelines, preventing keys from leaking to logs.
