# Notion Intelligence — Conflict Resolution
**Sprint 9 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define collision boundaries, write concurrency rules, conflict resolution policies, and lock integrations.
* **Scope**: Governs concurrency handlers, merge utility classes, and transaction locking mechanisms.
* **Audience**: DBAs, Backend Developers, and Integration Architects.
* **Related Documents**:
  * [notion/search/sync_indexing.md](file:///Users/anzarakhtar/aios/docs/notion/search/sync_indexing.md) - Transaction boundaries.
  * [docs/reference/interfaces.md](file:///Users/anzarakhtar/aios/docs/notion/reference/interfaces.md) - Lock lease managers.

---

## 1. Concurrency Conflicts

Because the Personal AI OS is local-first, users can edit files locally while other collaborators modify corresponding pages on Notion. This leads to **Concurrency Conflicts**:

```
        [Common Ancestor State (V1)]
             /             \
            v               v
    Local Modifies (V2L)  Remote Modifies (V2R)
            \               /
             v             v
       [Write Collision / Conflict State]
```

To prevent data loss, the system uses the **`LockLeaseManager`** (interface defined in [docs/reference/interfaces.md](file:///Users/anzarakhtar/aios/docs/notion/reference/interfaces.md)) to coordinate write transactions.

---

## 2. Lock Lease Coordination

Before modifying a page locally or pushing updates to Notion:
1. **Acquire Lease**: Request a temporary write lock for the page ID from the `LockLeaseManager`:
   ```python
   # Acquire lease to prevent concurrent writes during sync runs
   lock_acquired = lock_manager.acquire_lease(
       lock_type="notion_sync",
       lock_id=page_id,
       owner_id="NotionSyncEngine",
       policy=LockPolicy.FAIL_FAST,
       lease_duration=10.0 # 10-second lease
   )
   ```
2. **Execute Sync**: Push/pull the document payload.
3. **Release Lease**: Release the lock upon transaction completion. If the lease expires before the sync completes, the transaction is aborted.

---

## 3. Conflict Resolution Policies

When the system detects that both the local cache and the remote Notion page have changed since the last synchronization:

### 3.1 Policy A: Local-Wins (Overwrite Remote)
* **Strategy**: The local cache is treated as the source of truth. The remote page is overwritten with the local version.
* **Use Case**: Best for automated logs, build reports, and compiler metrics.

### 3.2 Policy B: Remote-Wins (Discard Local)
* **Strategy**: Discard local changes and overwrite the local cache with the remote page data.
* **Use Case**: Best for workspaces where tasks and comments are managed primarily in the browser.

### 3.3 Policy C: Three-Way Merge (Interactive)
* **Strategy**: Compare the local version and the remote version against their common ancestor using a line-by-line diff.
* **Flow**:
  * If changes occur in non-overlapping blocks, they are merged automatically.
  * If changes overlap (e.g. both modified the same paragraph block), the sync halts, and the conflict is displayed in the REPL console:
    ```
    [Notion Sync Conflict]
    Conflict detected on page 'Notion Integration Design':
    <<< Local Changes
    - Sync scheduler runs every 15 minutes.
    === Remote Changes
    - Sync scheduler runs every 30 minutes.
    >>>
    
    Select option: [L]ocal wins, [R]emote wins, [M]anual edit: 
    ```
  * The system blocks further operations until the user makes a selection.
  * If running in non-interactive batch mode, the operation is skipped, the page status is marked as `CONFLICT`, and a warning is logged.
