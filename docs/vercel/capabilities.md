# Vercel Intelligence — Capabilities Matrix
**Sprint 13 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical mappings, domain hierarchies, and processing rules for Vercel infrastructure components.
* **Scope**: Governs resource types, hosting mappings, and orchestration schemas.
* **Audience**: Systems Integrators, QA Engineers, and AI developers.
* **Related Documents**:
  * [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md) - System definitions repository.
  * [vercel/architecture.md](file:///Users/anzarakhtar/aios/docs/vercel/architecture.md) - Technical architecture.

---

## 1. Canonical Infrastructure Hierarchy

To model Vercel resources consistently, the AI OS maps all infrastructure objects to a system-wide hierarchy:

**Infrastructure → Vercel Project → Deployment → Environment → Service → Resource → Metadata → KnowledgeNode**

```
  +----------------------+
  |    Infrastructure    | (e.g. "Hosting providers")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |    Vercel Project    | (e.g. "ai-os-next-frontend")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |      Deployment      | (e.g. "dep_xyz789_production")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |     Environment      | (e.g. "production", "preview", "development")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |       Service        | (e.g. "Serverless Runtime", "CDN Edge Gateway")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |       Resource       | (e.g. "Deno Script", "PostgreSQL database hook")
  +----------------------+
            | (1-to-1)
            v
  +----------------------+
  |       Metadata       | (Env vars, build settings, domains, SSL records)
  +----------------------+
            | (1-to-1)
            v
  +----------------------+
  |    KnowledgeNode     | (Local system memory representation)
  +----------------------+
```

---

## 2. Infrastructure Capabilities Matrix

The system classifies and manages Vercel resources across ten dimensions:

### 2.1 Projects
* **Targets**: Project configurations, build settings, root directories.
* **Operations**: Inspects settings, configures frameworks, and maps directories.

### 2.2 Deployments
* **Targets**: Deployment URL structures, status monitors, commit records.
* **Operations**: Triggers deployments, tracks progress, and promotes versions.

### 2.3 Builds
* **Targets**: Local build tasks, remote build logs, build timeouts.
* **Operations**: Triggers local builds, dry-runs scripts, and parses logs.

### 2.4 Serverless Functions
* **Targets**: Node.js/Python serverless scripts, execution timeouts, memory limits.
* **Operations**: Inspects functions, bundles dependencies, and deploys scripts.

### 2.5 Edge Functions
* **Targets**: Deno edge runtimes, middleware scripts, geo-routing configurations.
* **Operations**: Compiles scripts, validates import maps, and deploys logic.

### 2.6 Environment Variables
* **Targets**: Project secrets, environment variables (`production`, `preview`, `development`).
* **Operations**: Inspects configurations, updates variables, and synchronizes keys.

### 2.7 Domains
* **Targets**: DNS records, SSL certificates, redirect configurations.
* **Operations**: Inspects domains, configures redirects, and verifies DNS.

### 2.8 Analytics
* **Targets**: Web vitals, visitor metrics, performance scores.
* **Operations**: Inspects performance metrics and evaluates vitals.

### 2.9 Logs
* **Targets**: Realtime API Gateway logs, Deno runtime logs, error tracking.
* **Operations**: Subscribes to log streams and parses logs.

### 2.10 Observability
* **Targets**: CPU/memory statistics, serverless usage limits, invocation counts.
* **Operations**: Monitors system metrics, logs warnings, and schedules maintenance.
