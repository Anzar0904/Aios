# Repository Metadata Spec
**Sprint 10 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define metadata schemas and extraction tools for mapping version control logs and histories.
* **Scope**: Governs Git commit structures, contributor histories, and status flags.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [workspace/capabilities.md](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) - Capabilities domains matrix.
  * [workspace/project_discovery/repository_discovery.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/repository_discovery.md) - Root boundary specs.

---

## 1. Metadata Schema Definition

When the Workspace Intelligence module processes a version control repository, it builds a metadata object summarizing active branches, remotes, status changes, and history indicators.

```python
@dataclass
class RepositoryMetadata:
    repository_root: str
    vcs_type: str  # 'git', 'hg'
    active_branch: str
    is_dirty: bool
    remote_url: Optional[str]
    latest_commit_hash: str
    latest_commit_author: str
    latest_commit_date: datetime
    ahead_behind_upstream: Tuple[int, int]  # (ahead_count, behind_count)
    staged_files: List[str]
    unstaged_files: List[str]
    untracked_files: List[str]
```

---

## 2. Contributor Mappings

To help agents coordinate development plans, Workspace Intelligence compiles contributor metrics from historical commit logs:
* **Contributor Index**: Runs local logs queries (e.g. `git shortlog -sn --all`) to parse developer emails and names.
* **Impact Areas**: Maps authors to file subtrees based on commit frequencies (e.g. Developer A owns 80% of changes inside `core/src/aios/services/`, Developer B owns 90% of `docs/`). This enables agents to intelligently recommend co-authors or code reviewers.

---

## 3. Remote Tracking & Status Indicators

The metadata collector reads Git config parameters to track remote synchronization statuses:
* **Upstream Delta**: Executes non-blocking updates (`git fetch` in background) to compute how many commits the local branch is ahead or behind its remote counterpart.
* **Stash Counts**: Tracks local stashed modifications to prevent code loss when agents perform branch changes.
* **Ignored Status**: Counts untracked files that are not excluded by `.gitignore` rules, alerting developers when temporary build caches are cluttering the workspace.
