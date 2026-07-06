# AI Database Orchestration — Navigation Hub
**Sprint 12 · Milestone 6** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory houses the **AI Database Orchestration** specifications for the Personal AI OS.
> It builds upon the [Supabase Foundation](file:///Users/anzarakhtar/aios/docs/supabase/README.md), [Database Intelligence](file:///Users/anzarakhtar/aios/docs/supabase/database/README.md), [Security Intelligence](file:///Users/anzarakhtar/aios/docs/supabase/security/README.md), [Platform Intelligence](file:///Users/anzarakhtar/aios/docs/supabase/platform/README.md), and [Operations Intelligence](file:///Users/anzarakhtar/aios/docs/supabase/operations/README.md) documents.
>
> In accordance with local-first system design guidelines, all infrastructure reasoning, execution planning, autonomous workflows, and governance controls are processed locally, keeping the AI OS kernel as the central director.

---

## Documents

| Document | Purpose |
|---|---|
| [database_orchestration.md](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/database_orchestration.md) | High-level director specifications, Event Bus integration, and execution control loops |
| [infrastructure_reasoning.md](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/infrastructure_reasoning.md) | Analyzing table schemas, tracing cascade dependencies, and evaluating RLS policies |
| [schema_planning.md](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/schema_planning.md) | DAG task planners, execution tracking, lock failovers, and rollback planning |
| [migration_workflows.md](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/migration_workflows.md) | Standard pipelines (Deploy schema migrations, audit RLS rules, deploy Deno edge scripts) |
| [autonomous_operations.md](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/autonomous_operations.md) | Background maintenance cron scheduling, backup validation, and query lock evictions |
| [approval_workflows.md](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/approval_workflows.md) | Approval Engine integration, user prompt challenges, and bypass constraints |
| [infrastructure_governance.md](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/infrastructure_governance.md) | SQL query AST filters, key encryption vaults, and access controls |

---

## Reading Order

1. **[`database_orchestration.md`](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/database_orchestration.md)**: Start here to study the orchestration engine architecture.
2. **[`infrastructure_reasoning.md`](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/infrastructure_reasoning.md)** & **[`schema_planning.md`](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/schema_planning.md)**: Explore database reasoning and DAG plans.
3. **[`migration_workflows.md`](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/migration_workflows.md)** & **[`autonomous_operations.md`](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/autonomous_operations.md)**: Learn about schema pipelines and background tasks.
4. **[`approval_workflows.md`](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/approval_workflows.md)** & **[`infrastructure_governance.md`](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/infrastructure_governance.md)**: Review approvals and governance.
