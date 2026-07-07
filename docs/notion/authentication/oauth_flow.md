# Notion Intelligence — OAuth 2.0 Flow Specification
**Sprint 9 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Specify the OAuth 2.0 authorization code flow, browser redirection mechanics, and local HTTP loopback server configuration.
* **Scope**: Dictates the network sequencing, token exchange payloads, and loopback socket lifecycles.
* **Audience**: Backend Engineers, Systems Architects, and Integration Testers.
* **Related Documents**:
  * [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) - Security guidelines and local server policy.
  * [notion/authentication/authentication.md](file:///Users/anzarakhtar/aios/docs/notion/authentication/authentication.md) - High-level auth subsystem.

---

## 1. OAuth 2.0 Interaction Flow

Because the Personal AI OS is a local command-line REPL application, it utilizes the **OAuth 2.0 Authorization Code Flow with a Local Loopback Redirect URI**. This allows the user to grant access in their default web browser, redirecting the auth code back to a temporary port monitored by the OS.

```
 [Personal AI OS]           [Web Browser]           [Notion Auth Server]
        |                         |                         |
        |-- 1. Start Loopback ---->|                         |
        |-- 2. Open Consent URL ->|                         |
        |                         |-- 3. Render Page ------>|
        |                         |<-- 4. User Consents ----|
        |                         |                         |
        |                         |-- 5. Redirect w/ Code ->|
        |<-- 6. Capture Code -----|                         |
        |      (localhost:8080)   |                         |
        |                         |                         |
        |-- 7. Exchange Code (POST /v1/oauth/token) ------->|
        |<- 8. Access Token JSON Response ------------------|
        |                         |                         |
```

---

## 2. Step-by-Step Execution Sequence

### Step 1: Initialize Local Loopback Server
The `NotionAuthManager` binds a temporary HTTP listener to a random high-numbered local port (e.g., `http://localhost:8080/oauth/callback`) to receive the authorization code.
* The listener is configured with a **120-second timeout** to prevent orphaned sockets if the user cancels the operation.

### Step 2: Open Browser Consent URL
The OS prints the consent URL in the REPL console and attempts to open the user's default browser automatically using Python's standard `webbrowser` library:
* **Authorization Request Format**:
  ```
  https://api.notion.com/v1/oauth/authorize?
    client_id=76fa35bc-1f5e-4b62-a279-d5910faaea7b&
    response_type=code&
    owner=user&
    redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Foauth%2Fcallback&
    state=d93bc184a27e4e1a
  ```
  * `state`: A cryptographically secure random string (UUID or SHA-256 hash) to prevent cross-site request forgery (CSRF) attacks.

### Step 3: Consent and Redirect
The user selects which Notion pages and databases the integration can access, and submits. Notion redirects the browser to the loopback URL:
* **Callback URI Format**:
  ```
  GET http://localhost:8080/oauth/callback?code=b838c01c-e747-49d7-8e6f-54bf9e16bc82&state=d93bc184a27e4e1a
  ```

### Step 4: Token Exchange
The loopback server extracts the `code` and verifies that the `state` parameter matches the original request. The server displays a "Success" message to the user and shuts down.
* The OS issues a secure `POST` request to Notion's token endpoint:
  * **Endpoint**: `https://api.notion.com/v1/oauth/token`
  * **Headers**:
    * `Content-Type: application/json`
    * `Authorization: Basic [BASE64_ENCODED_CLIENT_ID_AND_SECRET]`
  * **Payload**:
    ```json
    {
      "grant_type": "authorization_code",
      "code": "b838c01c-e747-49d7-8e6f-54bf9e16bc82",
      "redirect_uri": "http://localhost:8080/oauth/callback"
    }
    ```

### Step 5: Process Access Token Response
Notion responds with the access token and workspace metadata.
* **Success Payload**:
  ```json
  {
    "access_token": "secret_abc123XYZ...",
    "token_type": "bearer",
    "bot_id": "9a38c11a-0fd7-4bca-8eb1-59da10faaea1",
    "workspace_name": "Personal Space",
    "workspace_icon": "https://example.com/icon.png",
    "workspace_id": "8f8bca12-efd8-4ba3-bfd0-cd1712a4501a",
    "owner": {
      "type": "user",
      "user": {
        "object": "user",
        "id": "c71a39f1-ef07-4bc2-af8b-59da10fa22b1",
        "name": "Anzar Akhtar",
        "avatar_url": null,
        "type": "person",
        "person": {
          "email": "anzarakhtar@example.com"
        }
      }
    }
  }
  ```

* **Storage**: The OS extracts the `access_token` and writes it to the local encrypted vault, tagging the workspace ID as registered.
