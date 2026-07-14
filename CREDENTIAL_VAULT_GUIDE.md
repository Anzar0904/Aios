# Credential Vault Guide

The Credential Vault secures API keys, OAuth tokens, and webhook secrets from plaintext exposure in the codebase.

---

## 1. Vault Database Schema

Stored in `~/.aios_integrations.db`:

```sql
CREATE TABLE credentials (
    credential_id   TEXT PRIMARY KEY,
    connector_id    TEXT NOT NULL UNIQUE,
    key_name        TEXT NOT NULL,
    encrypted_value TEXT NOT NULL,
    created_at      REAL NOT NULL,
    last_rotated    REAL NOT NULL
);

CREATE TABLE vault_audits (
    audit_id        TEXT PRIMARY KEY,
    credential_id   TEXT NOT NULL,
    action          TEXT NOT NULL, -- read|write|rotate
    performed_by    TEXT NOT NULL DEFAULT 'kernel',
    timestamp       REAL NOT NULL
);
```

---

## 2. Encryption & Audits

- **Reversible cipher**: Simulates key encoding to prevent raw text reads.
- **Auditing**: Every read or write log registers a row in the `vault_audits` table, recording the timestamp and operator identifier.

---

## 3. Rotation Schedule

- Secrets track the `last_rotated` real timestamp.
- Re-run `aios integrations connect <provider> <key> <val>` to overwrite credentials and rotate active keys in the database.
