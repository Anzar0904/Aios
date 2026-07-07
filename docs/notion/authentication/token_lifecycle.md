# Notion Intelligence — Token Lifecycle Management
**Sprint 9 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define token lifetime validation checks, expiration detections, refresh operations, and revocation sequences.
* **Scope**: Governs credentials cleanup, token expiry handlers, and HTTP authorization checkers.
* **Audience**: Systems Integrators, Quality Assurance, and Security Engineers.
* **Related Documents**:
  * [notion/authentication/authentication.md](file:///Users/anzarakhtar/aios/docs/notion/authentication/authentication.md) - Authentication state machines.
  * [notion/authentication/credential_storage.md](file:///Users/anzarakhtar/aios/docs/notion/authentication/credential_storage.md) - Encrypted credential stores.

---

## 1. Token Lifetime & Expiration

The Notion API supports two types of integration access keys:
1. **Internal Integration Tokens**: Generated manually by the user in the Notion developer portal. These tokens do not expire automatically and remain valid until explicitly deleted in Notion.
2. **Public Integration OAuth Tokens**: Exchanged via the OAuth 2.0 authorization code flow. While Notion OAuth access tokens do not expire by default, the Personal AI OS manages tokens with a **Session Verification Lifecycle** to verify active session validity.

---

## 2. Session Validation Workflow (Heartbeat)

To prevent connection failures during runtime operations, the `NotionAuthManager` performs periodic token validation checks.

```
 [Action Engine/Trigger] ===> Check Session Age
                                     |
                          [Is Age > 12 Hours?]
                                    / \
                                  No   Yes
                                  /     \
                                 v       v
                     [Use Cached Token]  [Verify Token Check (GET /v1/users/me)]
                                                  / \
                                                200 401
                                                /     \
                                               v       v
                                        [Valid Sync]  [Transition state to TOKEN_EXPIRED]
                                                               |
                                                               v
                                                      [Initiate Re-auth Flow]
```

### Validation Procedure
* **Interval**: Verification checks occur at boot, and subsequently on a **12-hour interval** before any scheduled batch sync.
* **Endpoint Query**: The system queries Notion's User retrieval endpoint (`GET https://api.notion.com/v1/users/me`).
  * **Success (200 OK)**: The token is valid. The local `last_synced_at` timestamp is updated.
  * **Authorization Error (401 Unauthorized)**: The session is flagged as `TOKEN_EXPIRED`. All queued writes and reads are paused.

---

## 3. Token Refresh and Re-Authorization

Notion does not use OAuth refresh tokens. When an OAuth access token is invalid or expired:
1. The OS transitions the workspace's state to `TOKEN_EXPIRED`.
2. The `NotionAuthManager` triggers a local notification:
   ```
   [Notion Sync Warning]
   Connection to workspace 'Personal Space' has expired or has been revoked on Notion.
   Please re-authenticate to restore synchronization.
   > notion workspace reauthorize
   ```
3. Running this command launches the OAuth code exchange flow (see [oauth_flow.md](file:///Users/anzarakhtar/aios/docs/notion/authentication/oauth_flow.md)), replacing the expired token in the encrypted credentials cache.

---

## 4. Revocation Sequence

The user can revoke workspace access at any time, either via Notion's settings dashboard or directly from the local REPL console.

### Local Revocation Flow (Initiated by CLI)
When the user executes `notion workspace disconnect <workspace_id>`:
1. **API Notification**: Send a termination request to the Notion workspace if supported, or log a disconnection event.
2. **Purge Credentials**: The `NotionAuthManager` calls `credential_storage` to delete matching credentials in the macOS Keychain or decrypt and delete the row in the `notion_credentials` SQLCipher table.
3. **Delete State Cache**: The local SQLite replica pages for the workspace are purged.
4. **Transition State**: Set the workspace status to `REVOKED` and then `UNAUTHENTICATED`.
5. **Log Event**: Log a security event to `logs/notion_security_audit.log`:
   ```
   [2026-07-06T18:49:00Z] [REVOCATION] Workspace '8f8bca12-efd8-4ba3-bfd0-cd1712a4501a' credentials purged by user command.
   ```
