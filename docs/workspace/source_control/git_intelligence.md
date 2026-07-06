# Git Intelligence Spec
**Sprint 10 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define core git execution wrappers, status parsing, and mapping of git object structures.
* **Scope**: Governs Git command executions, status caches, and object models.
* **Audience**: Systems Integrators, DBAs, and AI developers.
* **Related Documents**:
  * [docs/SOURCE_CONTROL_M1_REPORT.md](file:///Users/anzarakhtar/aios/docs/SOURCE_CONTROL_M1_REPORT.md) - Subsystem architecture report.
  * [workspace/source_control/README.md](file:///Users/anzarakhtar/aios/docs/workspace/source_control/README.md) - Source Control hub.

---

## 1. Local Git Execution Wrapper

The **Git Intelligence** subsystem uses the core **`LocalGitExecutor`** (defined in [docs/SOURCE_CONTROL_M1_REPORT.md](file:///Users/anzarakhtar/aios/docs/docs/SOURCE_CONTROL_M1_REPORT.md)) to run native Git shell commands securely.

```
[Agent: Git Tool Call] ===> GitIntelligenceService
                                    |
                        [Path containment Check] ===> Block if outside workspace root
                                    |
                         [LocalGitExecutor Sandbox] ===> Execute shlex subprocess (shell=False)
                                    |
                            [Output Parser] ===> Parse CLI text block to structured JSON
```

* **Command Containment**: All git processes are spawned inside the target repository path using path checks to block arguments referencing files outside workspace boundaries (e.g. `git add ../../../etc/passwd`).
* **Environment Scrubbing**: Git subprocesses are run with environment cleanups, stripping external token keys unless explicitly whitelisted.

---

## 2. Parsing Git Status Streams

To keep database records matching the physical disk state:
* **Null-Terminated Status Parsing**: The engine executes `git status -z --porcelain` to retrieve modified paths. Null-character separation prevents issues with spaces or special characters in file paths.
* **Status Mappings**:
  * `M `: Staged modifications (update metadata cache).
  * ` M`: Unstaged modifications (alert watcher queue).
  * `A `: Staged additions (register module in database).
  * `??`: Untracked files (evaluate ignore rules).

---

## 3. Git Object Model Mapping

Physical git structures are mapped to the local catalog database:
* **Blob (File Content)**: Mapped to standard Module hashes (`sha256`).
* **Tree (Directory Node)**: Mapped to database hierarchy folders (`directory_tree_cache`).
* **Commit (Version Hash)**: Mapped to Commit nodes in the history graph (`commit_history`).
