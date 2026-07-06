# Vercel Intelligence — Architecture Specification
**Sprint 13 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the technical architecture, interfaces, and database schemas for the Vercel Intelligence module.
* **Scope**: Governs Python service classes, deploy adapters, and local metadata databases.
* **Audience**: Systems Architects, Lead Developers, and AI coding agents.
* **Related Documents**:
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) - Dependency Injection and registry rules.
  * [vercel/vercel_intelligence.md](file:///Users/anzarakhtar/aios/docs/vercel/vercel_intelligence.md) - Conceptual vision.

---

## 1. High-Level Architecture

Following the **Dependency Inversion Principle (DIP)** established in [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md), the `VercelIntelligenceService` interacts with remote Vercel instances using abstract adapters:

```
                  +-----------------------------------+
                  |        ServiceRegistry            |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |      VercelIntelligenceService    |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |        VercelClientAdapter        | (Abstract Interface)
                  +-----------------------------------+
                                    ^
                                    |
                  +-----------------------------------+
                  |       BaseVercelClientAdapter     | (Concrete Implementation)
                  +-----------------------------------+
                    /                |                \
                   v                 v                 v
       +---------------+     +---------------+     +---------------+
       |   Projects    |     |  Deployments  |     | Log Streams   |
       |    Adapter    |     |    Adapter    |     |    Adapter    |
       +---------------+     +---------------+     +---------------+
               |                     |                     |
               v                     v                     v
       +---------------+     +---------------+             |
       | Qdrant Vector |     | SQLite Cache  |             v
       | (Vercel DB)   |     | (SQLCipher)   |     [Remote Vercel API]
       +---------------+     +---------------+
```

---

## 2. Component Deep Dive

### 2.1 VercelIntelligenceService
* **Namespace**: `aios.services.vercel`
* **Responsibility**: Coordinates project inspections, build dry-runs, environment variables syncs, and log watchdogs.
* **Interface**:
  ```python
  class VercelIntelligenceService(ABC):
      @abstractmethod
      def inspect_project(self, project_name: str) -> VercelProject:
          """Inspect project settings, domains, and active deployment states."""
          pass

      @abstractmethod
      def trigger_deployment(self, build_files: List[LocalFile]) -> DeploymentResult:
          """Trigger deployment of build files to the remote Vercel project."""
          pass

      @abstractmethod
      def watch_logs(self, deployment_id: str) -> LogStreamObserver:
          """Subscribe to realtime execution logs for serverless/edge functions."""
          pass
  ```

### 2.2 VercelClientAdapter
* **Namespace**: `aios.providers.vercel.adapters`
* **Responsibility**: Abstract client contract for executing Vercel API queries, uploading envs, and managing domains.
* **Interface**:
  ```python
  class VercelClientAdapter(ABC):
      @abstractmethod
      def create_deployment(self, project_id: str, files: dict) -> dict:
          """Deploy files to target project using Vercel APIs."""
          pass

      @abstractmethod
      def set_environment_variable(self, project_id: str, key: str, value: str, target: List[str]) -> dict:
          """Update environment variables on the remote Vercel project."""
          pass
  ```

### 2.3 VercelStateStore
* **Namespace**: `aios.providers.vercel.storage`
* **Responsibility**: Manages the local SQLite database containing cached projects, deployments metadata, and domain logs.
* **Schema**:
  ```sql
  CREATE TABLE IF NOT EXISTS vercel_projects (
      project_id TEXT PRIMARY KEY,
      project_name TEXT NOT NULL UNIQUE,
      framework TEXT NOT NULL,
      cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS project_deployments (
      deployment_id TEXT PRIMARY KEY,
      project_id TEXT NOT NULL,
      url TEXT NOT NULL,
      status TEXT NOT NULL,                -- READY, ERROR, BUILDING
      created_at TIMESTAMP NOT NULL,
      FOREIGN KEY(project_id) REFERENCES vercel_projects(project_id) ON DELETE CASCADE
  );
  ```

---

## 3. Operations Flow

When a developer agent processes a deployment:
1. **Workspace Check**: Verifies build files and packages configurations locally.
2. **Local Testing**: Runs test scripts locally to verify code quality.
3. **Approval Gate**: Intercepts deployments, prompting the developer for confirmation.
4. **Execution**: Deploys code to Vercel via the API.
5. **Monitoring**: Subscribes to realtime logs to monitor deployment status.
6. **Caching**: Updates local SQLite and indexes deployment details in Qdrant.
