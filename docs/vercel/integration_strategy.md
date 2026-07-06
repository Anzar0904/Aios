# Vercel Integration & Caching Strategy
**Sprint 13 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define synchronization loops, deployment builders, vector mappings, and local caching parameters.
* **Scope**: Governs project checkers, deployment runners, and database caches.
* **Audience**: DBAs, Search Engineers, and Quality Auditors.
* **Related Documents**:
  * [workspace/integration_strategy.md](file:///Users/anzarakhtar/aios/docs/workspace/integration_strategy.md) - System workspace synchronization.
  * [vercel/capabilities.md](file:///Users/anzarakhtar/aios/docs/vercel/capabilities.md) - Mapped capabilities.

---

## 1. Local Verification & Deployment Loops

To safely deploy applications, the system runs local verification steps before uploading assets:

```
[Local Workspace Code]
          |
          v
[Run Local Tests & Build] <===> [Verify Package Lockfiles]
          |
          +---> Compiles static assets and runs Deno tests
          |
          v
[Trigger Deployment] ===> Upload to Vercel ---> Subscribe to realtime logs
```

1. **Local Compilation**: Compiles static assets and verifies dependency configurations locally.
2. **Dependency Validation**: Scans lockfiles (`package-lock.json`, `pnpm-lock.yaml`) to ensure dependency integrity.
3. **Deployment Upload**: Packages verified files and uploads them to Vercel via API.
4. **Log Observation**: Subscribes to Vercel's realtime log streams to track build and runtime execution.

---

## 2. Qdrant Vector Collection Mappings

Hosting configurations and deployment records are embedded and saved to the **`vercel_memory`** collection in Qdrant:
* **Dimensions**: 384 dimensions.
* **Payload Fields**:
  ```json
  {
    "workspace_id": "profile_hash_value",
    "source": "vercel",
    "project_id": "remote_project_id",
    "project_name": "next-frontend",
    "deployment_id": "dep_id_value",
    "url": "https://next-frontend.vercel.app",
    "text_content": "Project next-frontend deployed successfully, active at https://next-frontend.vercel.app."
  }
  ```
* **Payload Indices**: `project_id`, `project_name`, and `deployment_id` are indexed in Qdrant, enabling sub-10ms semantic searches.

---

## 3. Local SQLite Deployment Cache

* **Cache Lookup**: The inspection engine queries the local SQLite `vercel_projects` table. If the cached project metadata has not expired, it returns results directly, avoiding network latency.
* **Expiration TTLs**:
  * Active projects & deployments: **3600 seconds (1 hour)**.
  * Environment variables configurations: **1800 seconds (30 minutes)**.
  * Deployment logs: **Permanent (Never expire)**.
