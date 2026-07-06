# Branch Management & Delta Spec
**Sprint 10 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define data structures, metrics, and tools for monitoring local/remote branches and tracking stale states.
* **Scope**: Governs branch status checks, ahead/behind calculations, and cleanup tasks.
* **Audience**: Systems Integrators, DBAs, and Lead Developers.
* **Related Documents**:
  * [workspace/project_discovery/repository_metadata.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/repository_metadata.md) - Repository metadata.
  * [workspace/source_control/commit_analysis.md](file:///Users/anzarakhtar/aios/docs/workspace/source_control/commit_analysis.md) - Commit parsing.

---

## 1. Branch Metrics & Metadata Schema

The **Branch Management** module monitors local and remote branch topologies, caching branch states inside the repository database.

```python
@dataclass
class BranchState:
    branch_name: str
    is_remote: bool
    tracking_upstream: Optional[str]
    commits_ahead: int
    commits_behind: int
    last_commit_date: datetime
    last_commit_author: str
    is_active: bool  # True if currently checked out
```

---

## 2. Commit Delta & Merge Distance Calculations

The system computes ahead/behind commit quantities against the tracking upstream or base branch (e.g., `main`):
* **Ahead Counter**: Executes `git rev-list --count [upstream]..[branch]` to count local modifications that have not been pushed.
* **Behind Counter**: Executes `git rev-list --count [branch]..[upstream]` to track outstanding updates.
* **Alert Thresholds**: If a developer's active branch falls more than **15 commits behind** upstream, the AI OS prints a REPL warning suggesting a rebase/merge to prevent conflict debt.

---

## 3. Stale Branch Tracking

To maintain repository hygiene:
* **Stale Branch Checks**: The branch monitor parses the latest commit timestamps across all branches.
* **Classification**:
  * **Stale**: Branches with no commits for **> 30 days**.
  * **Obsolete**: Branches marked as "Stale" whose code has already been merged into the main tracking branch.
* **Cleanup Prompts**: The AI OS lists obsolete branches in weekly reports and prompts developers via the REPL to clean them up:
  ```
  [Branch Cleanup Prompt]
  The following branch is obsolete and has been merged: 'feature/s9-notion-auth'.
  Would you like the AI OS to delete this local and remote branch? [y/N]
  ```
