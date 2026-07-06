# Supabase Intelligence — Documentation Hub
**Sprint 12 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory defines the **Supabase Intelligence Foundation** for the Personal AI OS.
> All documents in this section are subordinate to and derived from
> [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) (the OS Constitution) and 
> [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) (the Engineering Bible).
>
> In accordance with system guidelines, this module operates under a local-first, offline-first paradigm, keeping the AI OS kernel as the central execution and reasoning core while managing Supabase as a local or remote infrastructure target.

---

## Purpose

`docs/supabase/` is the canonical home for the architectural specifications, functional capabilities, integration strategies, security models, and development roadmap of the Supabase Intelligence subsystem.

This subsystem provides the AI OS with a comprehensive framework to inspect, query, modify, validate, and synchronize Supabase resources—including databases, schemas, tables, views, postgres functions, RLS (Row-Level Security) policies, authentication systems, storage buckets, realtime channels, edge functions, and schema migrations. It treats Supabase as a target infrastructure provider while keeping the local database as the primary system of record.

---

## Document Map

```
docs/supabase/
├── README.md                    ← This file — navigation hub
├── supabase_intelligence.md      ← Conceptual vision and product framework
├── architecture.md              ← Structural components, classes, and databases
├── capabilities.md              ← Infrastructure objects and capabilities matrix
├── integration_strategy.md      ← Synchronizations, local indexes, and caching rules
├── security_model.md            ← Credentials vault, SQL injection guards, and RLS checks
├── roadmap.md                   ← Sprint 12 milestones, timeline, and risk matrix
├── database/                    ← Milestone 2: Schema discovery, foreign key mapping, and index scans
├── security/                    ← Milestone 3: Auth configs, RLS validations, and compliance drift
├── platform/                    ← Milestone 4: Deno edge scripts, storage buckets, and platform health
├── operations/                  ← Milestone 5: WebSockets replication, WAL backups, and failovers
├── orchestration/               ← Milestone 6: Planning DAGs, DDL checkers, and User Approvals
└── certification/               ← Milestone 7: Compliance audits and Supabase Health scorecard
```

---

## Reading Order

| Step | Document / Directory | When to Read |
|------|----------------------|--------------|
| 1 | [`supabase_intelligence.md`](file:///Users/anzarakhtar/aios/docs/supabase/supabase_intelligence.md) | First — Establish the conceptual vision, design tenets, and system paradigms. |
| 2 | [`architecture.md`](file:///Users/anzarakhtar/aios/docs/supabase/architecture.md) | Before reviewing or implementing class models, API clients, or database schemas. |
| 3 | [`capabilities.md`](file:///Users/anzarakhtar/aios/docs/supabase/capabilities.md) | Before writing SQL query wrappers, migration executors, or RLS validators. |
| 4 | [`integration_strategy.md`](file:///Users/anzarakhtar/aios/docs/supabase/integration_strategy.md) | Before coding schema diff loops, Qdrant indexing syncs, or offline buffers. |
| 5 | [`security_model.md`](file:///Users/anzarakhtar/aios/docs/supabase/security_model.md) | Mandatory reading before handling service role tokens, validating policies, or running migrations. |
| 6 | [`roadmap.md`](file:///Users/anzarakhtar/aios/docs/supabase/roadmap.md) | To review sprint tasks, milestones, and mitigation plans. |
| 7 | [Database Hub →](file:///Users/anzarakhtar/aios/docs/supabase/database/README.md) | To study schema inspections, foreign key mapping, and query explain checks. |
| 8 | [Security Hub →](file:///Users/anzarakhtar/aios/docs/supabase/security/README.md) | To study GoTrue auth config audits, RLS tests, and compliance drift. |
| 9 | [Platform Hub →](file:///Users/anzarakhtar/aios/docs/supabase/platform/README.md) | To study Deno edge function bundles, bucket access rules, and platform monitoring. |
| 10 | [Operations Hub →](file:///Users/anzarakhtar/aios/docs/supabase/operations/README.md) | To study WebSocket publications, pg_dump backups, and disaster failovers. |
| 11 | [Orchestration Hub →](file:///Users/anzarakhtar/aios/docs/supabase/orchestration/README.md) | To study planning DAGs, DDL constraint checkers, and User Approvals. |
| 12 | [Certification Hub →](file:///Users/anzarakhtar/aios/docs/supabase/certification/README.md) | To review compliance verification sheets and health scorecards. |

---

## Core System Integration

The Supabase Intelligence subsystem directly integrates with several existing services defined in the [Engineering Bible](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md):

* **Knowledge Hub Service**: Expands the `KnowledgeHubService` to index and search remote databases schemas, tables descriptions, and pg functions locally.
* **Tiered Memory System**: Maps parsed infrastructure schemas and migration histories into local vector storage (Qdrant) inside the `supabase_memory` collection to enable semantic queries.
* **Action Engine & Task Executor**: Equips database agents with tools for schema inspections, migration writing, and safe query executions.
* **Notion Intelligence**: Publishes database schema reports and architecture updates directly to Notion workspaces.
* **Development Workspace Intelligence**: Connects code-level SQL migrations and ORM models to active database configurations.
* **Research Intelligence**: Feeds database error diagnostics into the research agent's query pipelines.
