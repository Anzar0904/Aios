# Deployment History & Version Ledger Spec
**Sprint 13 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define deployment history tables, version control ledgers, and database schemas.
* **Scope**: Governs history tables, version records, and metadata schemas.
* **Audience**: DBAs, Systems Architects, and Lead Developers.
* **Related Documents**:
  * [vercel/deployments/deployment_analysis.md](file:///Users/anzarakhtar/aios/docs/vercel/deployments/deployment_analysis.md) - Deployment analysis.
  * [vercel/deployments/rollback_strategy.md](file:///Users/anzarakhtar/aios/docs/vercel/deployments/rollback_strategy.md) - Rollback strategy.

---

## 1. Version History Database Schema

The system tracks deployment histories by querying Vercel APIs and saving records to the local SQLite database:

```sql
CREATE TABLE IF NOT EXISTS project_deployments_ledger (
    ledger_id INTEGER PRIMARY KEY AUTOINCREMENT,
    deployment_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    version_number TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    environment TEXT CHECK(environment IN ('production', 'preview', 'development')) NOT NULL,
    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES vercel_projects(project_id) ON DELETE CASCADE
);
```

This version ledger allows agents to identify stable historical versions for rollbacks.
