# Security Audit Report

This document reports the security, credential management, and filesystem permissions audit.

---

## 1. Credentials Isolation
All integration tokens and credentials files are isolated under `.agent/` subdirectory config files:
- `.agent/credentials/openrouter.json`
- `.agent/github/credentials.json`
- `.agent/supabase/credentials.json`
- `.agent/vercel/credentials.json`

All files are strictly written using owner-only `0600` file permissions (`chmod 600`) to prevent any read/write exposure from external system processes.

---

## 2. Governance Middleware Verification
- **Middleware Routing**: Intercepts all high-impact actions (database writes, deployment changes, etc.).
- **Replay Protection**: Single-use approval tokens prevent duplicate execution.
- **Audit trail**: Chronological audit logs written to `.agent/approval/audit.json`.
