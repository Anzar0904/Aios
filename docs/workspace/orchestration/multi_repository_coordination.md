# Multi-Repository Coordination Spec
**Sprint 10 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical interfaces and dependency resolving logic for coordinating tasks across multiple repositories.
* **Scope**: Governs cross-repo dependency scans, concurrent builds, and atomic commits.
* **Audience**: Systems Integrators, DBAs, and Lead Developers.
* **Related Documents**:
  * [workspace/project_discovery/dependency_graph.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/dependency_graph.md) - Dependency schemas.
  * [workspace/source_control/change_impact.md](file:///Users/anzarakhtar/aios/docs/workspace/source_control/change_impact.md) - Change impact.

---

## 1. Cross-Repository Dependency Mapping

In large systems, codebases are often split across multiple repositories (e.g. `core-api` and `mobile-app`). The **Multi-Repository Coordinator** monitors these relationships:
* **Package References**: Scans lockfiles in the mobile app repository to detect dependency references to local package paths in the core API repository.
* **Cross-Repo Impact Trees**: When changes are made to `core-api`, the coordinator queries the global database to locate all dependent repositories, flagging them for rebuilds.

```
[Modify API in core-api]
          |
          v
[Trace Dependencies] ===> Finds dependent project 'mobile-app'
          |
          v
[Coordinate Actions]
          +---> Step 1: Run 'pytest' in core-api repository.
          +---> Step 2: Compile & run 'npm test' in mobile-app repository.
```

---

## 2. Parallel Builds Coordination

To speed up verification:
* **Concurrent Build Runners**: Spawns parallel processes to build and check separate repositories, scaling thread limits dynamically.
* **Stream Multiplexing**: Merges stdout/stderr streams from parallel builds, prefixing log lines with repository tags (e.g. `[core-api] error...`, `[mobile-app] pass...`) in database tables.

---

## 3. Coordinated Git Commits

When a task requires changes across multiple repositories (e.g. updating a shared schema):
1. **Atomic Staging**: Stages changes in all affected repositories.
2. **Commit Linking**: Commits changes across repositories in lockstep, using matching branch names and adding cross-references in commit messages (e.g. `feat(api): update schema (linked: mobile-app#c82614)`).
3. **Rollback Sync**: If committing in Repository B fails, the system rolls back changes in Repository A (`git reset --hard HEAD~1`) to maintain consistency.
