# Project Discovery & Repository Intelligence — Navigation Hub
**Sprint 10 · Milestone 2** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory houses the **Project Discovery & Repository Intelligence** specifications for the Personal AI OS.
> It builds upon the [Development Workspace Foundation](file:///Users/anzarakhtar/aios/docs/workspace/README.md) and maps the physical project structures to the system-wide hierarchy:
> **Workspace → Project → Repository → Package → Module → File → Symbol**.
>
> In accordance with the system guidelines, all scanning, classification, dependency mapping, and cataloging procedures are executed locally, maintaining the AI OS as the central reasoning and orchestration core.

---

## Documents

| Document | Purpose |
|---|---|
| [repository_discovery.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/repository_discovery.md) | Automatic discovery of version control roots (`.git`, `.hg`) and VCS adapters |
| [workspace_scanning.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/workspace_scanning.md) | Workspace filesystem walkers, path exclusions, debouncing, and schedules |
| [project_classification.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/project_classification.md) | Mappings classifying projects by languages, frameworks, build tools, and package configs |
| [repository_metadata.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/repository_metadata.md) | Extraction of git histories, commit authors, remote branches, and status diffs |
| [dependency_graph.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/dependency_graph.md) | Generating multi-project and package-level static dependency graphs and import hierarchies |
| [workspace_catalog.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/workspace_catalog.md) | SQLite catalog schema mapping the Workspace-to-Symbol structural hierarchy |
| [repository_health.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/repository_health.md) | Metrics and indices evaluating code coverage, build health, lints, and dependency drift |

---

## Reading Order

1. **[`repository_discovery.md`](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/repository_discovery.md)**: Start here to understand how repository boundaries are identified.
2. **[`workspace_scanning.md`](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/workspace_scanning.md)**: Learn how filesystems are traversed and cached.
3. **[`project_classification.md`](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/project_classification.md)**: Explore framework and build tool metadata mappings.
4. **[`workspace_catalog.md`](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/workspace_catalog.md)**: Review the core SQLite schemas modeling the codebase hierarchy.
5. **[`dependency_graph.md`](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/dependency_graph.md)**: Learn how package and import dependency links are parsed.
6. **[`repository_metadata.md`](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/repository_metadata.md)** & **[`repository_health.md`](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/repository_health.md)**: Deep dive into version control extraction and health indexes.
