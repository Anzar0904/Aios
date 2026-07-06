# Deployment Intelligence — Navigation Hub
**Sprint 13 · Milestone 2** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory houses the **Deployment Intelligence** specifications for the Personal AI OS.
> It builds upon the [Vercel Intelligence Foundation](file:///Users/anzarakhtar/aios/docs/vercel/README.md) and maps the physical hosting configurations to the hierarchy:
> **Infrastructure → Vercel Project → Deployment → Environment → Service → Resource → Metadata → KnowledgeNode**.
>
> In accordance with local-first system design guidelines, all deployment analyses, build trackers, artifact checks, history logs, rollback schedules, and health diagnostics are executed locally, keeping the AI OS kernel as the central director.

---

## Documents

| Document | Purpose |
|---|---|
| [deployment_analysis.md](file:///Users/anzarakhtar/aios/docs/vercel/deployments/deployment_analysis.md) | Deployment inspecting rules, status checkers, and the Deployment Resource state schema |
| [build_pipeline.md](file:///Users/anzarakhtar/aios/docs/vercel/deployments/build_pipeline.md) | Remote build task monitors, compiler diagnostics parsers, and error checkers |
| [artifact_management.md](file:///Users/anzarakhtar/aios/docs/vercel/deployments/artifact_management.md) | Bundle size audits, JavaScript chunk checks, and local build asset caches |
| [deployment_history.md](file:///Users/anzarakhtar/aios/docs/vercel/deployments/deployment_history.md) | Querying deployment logs, version histories, and mapping metadata in SQLite catalogs |
| [rollback_strategy.md](file:///Users/anzarakhtar/aios/docs/vercel/deployments/rollback_strategy.md) | Stable snapshot selectors, rollback API calls, and domains routing updates |
| [deployment_health.md](file:///Users/anzarakhtar/aios/docs/vercel/deployments/deployment_health.md) | SSL handshake status logs, CDN error gateway monitors, and routing verifiers |
| [deployment_metrics.md](file:///Users/anzarakhtar/aios/docs/vercel/deployments/deployment_metrics.md) | Web vital metric metrics, page speed latency logs, and server stats |

---

## Reading Order

1. **[`deployment_analysis.md`](file:///Users/anzarakhtar/aios/docs/vercel/deployments/deployment_analysis.md)**: Start here to study deployment payloads and the Resource state schema.
2. **[`build_pipeline.md`](file:///Users/anzarakhtar/aios/docs/vercel/deployments/build_pipeline.md)** & **[`artifact_management.md`](file:///Users/anzarakhtar/aios/docs/vercel/deployments/artifact_management.md)**: Explore build trackers and bundle checks.
3. **[`deployment_history.md`](file:///Users/anzarakhtar/aios/docs/vercel/deployments/deployment_history.md)** & **[`rollback_strategy.md`](file:///Users/anzarakhtar/aios/docs/vercel/deployments/rollback_strategy.md)**: Learn about deployment histories and rollback strategies.
4. **[`deployment_health.md`](file:///Users/anzarakhtar/aios/docs/vercel/deployments/deployment_health.md)** & **[`deployment_metrics.md`](file:///Users/anzarakhtar/aios/docs/vercel/deployments/deployment_metrics.md)**: Review deployment health diagnostics and performance metrics.
