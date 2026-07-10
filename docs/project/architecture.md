# Project Intelligence — Architecture Specification

This document details the architecture, integrations, data flows, and secure storage design of the Project Intelligence module.

---

## 1. High-Level Architecture

Project Intelligence serves as the centralized aggregator pattern over all specialized subsystem intelligence services.

```
                           +----------------------------+
                           |       Project Registry     |
                           |  (.agent/project/projs)    |
                           +----------------------------+
                                         |
                                         v
                  +----------------------------------------------+
                  |          ProjectIntelligenceService          |
                  +----------------------------------------------+
                    /       |              |            \      \
                   v        v              v             v      v
            +-----------+ +-----------+ +-----------+ +------+ +-----------+
            | Workspace | |  GitHub   | | Supabase  | |Vercel| |    n8n    |
            |   Intel   | |   Intel   | |   Intel   | |Intel | |   Intel   |
            +-----------+ +-----------+ +-----------+ +------+ +-----------+
```

---

## 2. Component Design

### 2.1 ProjectProfileStore
* **Location:** `.agent/project/projects.json`
* **Security:** Permissions restricted to `0600`. Contains registered project profiles and their metadata (ID, framework, path, etc.).

### 2.2 Caching Layer
* **Location:** `.agent/project/cache_{project_id}_{key}.json`
* **TTL:** 5 minutes (300 seconds). Prevents double calculation and high AST parsing costs.

### 2.3 Knowledge Graph Integration
* Integrates file layouts, database entities, deploy states, and commit branches into unified graphs representation.
