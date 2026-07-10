# Business Intelligence — Architecture Specification

This document details the architecture, integrations, data flows, and secure storage design of the Business Intelligence module.

---

## 1. High-Level Architecture

Business Intelligence serves as the top-level operational and business execution layer of AI OS. It orchestrates Project Intelligence and individual platform subsystems.

```
                           +----------------------------+
                           |     Business Registry      |
                           |  (.agent/business/*.json)  |
                           +----------------------------+
                                         |
                                         v
                  +----------------------------------------------+
                  |         BusinessIntelligenceService          |
                  +----------------------------------------------+
                         |                              |
                         v                              v
           +---------------------------+  +----------------------------+
           |     Project Intelligence  |  |      n8n Integration       |
           +---------------------------+  +----------------------------+
             /       |         \              /          |          \
            v        v          v            v           v           v
         [GitHub] [Supabase] [Vercel]   [Workflows]  [Execution]  [Runtime]
```

---

## 2. Component Design

### 2.1 Secure Data Stores
* **Location:** `.agent/business/`
  * `organizations.json`
  * `clients.json`
  * `leads.json`
  * `proposals.json`
  * `workflows.json`
  * `tasks.json`
* **Security:** Permissions restricted on creation to `0600` (read/write only by owner).

### 2.2 Integration Interfaces
* **Project Portfolio:** Connects directly with `ProjectIntelligenceService` to map repository profiles to client accounts.
* **Workflow Ownership:** Bridges the gap between n8n workflow deployment records and client-owned business automation contracts.
