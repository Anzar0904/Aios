# Deployment Governance & Credential Isolation Spec
**Sprint 13 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define Deno bundle verification, key encryption vaults, and domains access controls.
* **Scope**: Governs Deno security, credentials storage, and access controls.
* **Audience**: Security Auditors, System Architects, and Integration Developers.
* **Related Documents**:
  * [vercel/security_model.md](file:///Users/anzarakhtar/aios/docs/vercel/security_model.md) - Security model.
  * [vercel/orchestration/approval_workflows.md](file:///Users/anzarakhtar/aios/docs/vercel/orchestration/approval_workflows.md) - Approval workflows.

---

## 1. Deno Bundle Verification

To prevent execution of unauthorized commands:
* **Import Map Audits**: Scans the `import_map.json` file, checking that external dependency versions are locked.
* **Build File Audits**: Scans local build folders before deployment to ensure no sensitive files (e.g. `.env`, `.git`) are packaged.

---

## 2. API Key Vault Guards

* **Access Tokens**: Vercel API access tokens are stored in the database using SQLCipher. Access is limited to registered deployment adapters, preventing plaintext keys from leaking in console outputs or logs.
* **Domain Lockdowns**: Changes to DNS settings and domain redirects require explicit user approval before saving, preventing unauthorized redirection.
