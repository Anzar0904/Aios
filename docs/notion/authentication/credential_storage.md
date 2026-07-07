# Notion Intelligence — Credential Storage Specification
**Sprint 9 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the data encryption mechanisms, SQLite schema schemas, and OS Keychain integrations for storing Notion access tokens.
* **Scope**: Dictates the cryptographic algorithms, secret storage interfaces, and key derivation standards.
* **Audience**: Cryptographers, Security Auditors, and Database Engineers.
* **Related Documents**:
  * [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) - Project security guidelines.
  * [notion/security_model.md](file:///Users/anzarakhtar/aios/docs/notion/security_model.md) - Security model.

---

## 1. Storage Strategy & Keyring Integration

Access tokens must never be written to disk in plain text. The Personal AI OS uses a **Dual-Layered Credential Storage Strategy**:

```
+-----------------------------------------------------------------------------------+
|                           CREDENTIAL DISCOVERY PIPELINE                           |
+----------------------------------------+------------------------------------------+
| Layer 1: macOS Keychain (Primary)     | Access tokens are written directly to the|
|                                        | macOS Keychain using python-keyring,     |
|                                        | backed by OS-enforced credentials check. |
+----------------------------------------+------------------------------------------+
| Layer 2: SQLCipher SQLite (Fallback)   | If Keychain is unavailable, tokens are   |
|                                        | encrypted via AES-256-GCM and stored inside|
|                                        | the local SQLCipher encrypted SQLite cache|
+----------------------------------------+------------------------------------------+
```

### Keyring Service Details
* **Service Name**: `PersonalAIOSNotion`
* **Account Name**: `<workspace_id>`
* **Secret**: Access Token (e.g. `secret_abc123...`)

---

## 2. SQLCipher Encrypted Cache Schema

When storing credentials locally in the SQLite configuration database (used as a fallback or cache), the `notion_credentials` table is encrypted using SQLCipher:

```sql
CREATE TABLE IF NOT EXISTS notion_credentials (
    workspace_id TEXT PRIMARY KEY,
    encrypted_access_token BLOB NOT NULL,
    encryption_iv BLOB NOT NULL,
    encryption_tag BLOB NOT NULL,
    auth_type TEXT CHECK(auth_type IN ('OAUTH_TOKEN', 'INTERNAL_INTEGRATION_TOKEN')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Encryption Specification (AES-256-GCM)
* **Algorithm**: AES-256-GCM (Galois/Counter Mode).
* **Key Derivation Function (KDF)**: PBKDF2 with SHA-256, 100,000 iterations.
* **Salt**: A cryptographically secure random 16-byte salt, stored in the database's header or configuration block.
* **Initialization Vector (IV)**: A cryptographically secure random 12-byte initialization vector, regenerated on every write.
* **Tag**: A 16-byte authentication tag ensuring ciphertext integrity.

---

## 3. Cryptographic Operations Sequence

### Token Write Sequence (Encryption)
1. Generate a random 12-byte IV.
2. Query the derived master encryption key from the OS security subsystem.
3. Encrypt the raw token using AES-256-GCM, producing the ciphertext and the 16-byte authentication tag.
4. Save the `workspace_id`, `encrypted_access_token` (ciphertext), `encryption_iv`, `encryption_tag`, and metadata properties to the `notion_credentials` table.
5. Wipe the plaintext token string from memory.

### Token Read Sequence (Decryption)
1. Query the `notion_credentials` table for the matching `workspace_id`.
2. Extract the ciphertext, IV, and authentication tag.
3. Retrieve the master key.
4. Decrypt the token, validating the authentication tag.
5. Route the decrypted token directly to the API Client memory space. Plaintext token strings must not be saved to global variables or written to disk logs.
