# Vercel Intelligence — Architecture Specification

This document details the high-level architecture, service interfaces, data flows, and secure storage implementation of the Vercel Intelligence module.

---

## 1. High-Level Architecture

The Vercel Intelligence subsystem decoupled framework fits cleanly into the AI OS DI container boundary:

```
                  +-----------------------------------+
                  |        ServiceRegistry            |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |          VercelService            | (Abstract Interface)
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |   LocalVercelIntelligenceService  | (Concrete Implementation)
                  +-----------------------------------+
                     /              |              \
                    v               v               v
             +-------------+  +-------------+  +-------------+
             | Secure Cred |  | Local Cache |  | Vercel REST |
             |   Storage   |  |   System    |  |     API     |
             |   (0600)    |  |  (TTL 5m)   |  |  (httpx)    |
             +-------------+  +-------------+  +-------------+
```

---

## 2. Component Design

### 2.1 VercelService & LocalVercelIntelligenceService
* **Namespace:** `aios.services.vercel` & `aios.services.vercel_impl`
* **Lifecycle:** Integrates with the `ServiceLifecycle` container, starting and booting as the system starts.
* **Caches:** Writes local JSON caches scoped to `.agent/vercel/cache_{project_id}.json` using a 5-minute time-to-live (TTL) to avoid exceeding Vercel API rate limits.

### 2.2 Credentials Store
* **Location:** `.agent/vercel/credentials.json`
* **Security:** Restricts permissions on creation to `0600` (read/write only by owner) to safeguard tokens.

### 2.3 Build Diagnostics Engine
* Evaluates logs and messages retrieved from Vercel API `/events` endpoints.
* Categorizes common failures (missing dependencies, syntax errors, framework command failures) to present explanations without invoking remote models on basic checks.
