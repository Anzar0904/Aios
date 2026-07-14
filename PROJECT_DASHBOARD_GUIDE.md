# Project Dashboard Guide

The Project Dashboard (`aios project dashboard`) provides a rich, unified terminal user interface presenting real-time health metrics, active sprints, pending tasks, recent memory logs, and integration statuses.

## Dashboard Sections

### 1. Project Identification & Health Header
Presents core metadata, current sprint/phase, and an automatically calculated health score:

```
  AI OS   Personal AI Operating System — core intelligence and workflow engine

  Type: software  Priority: critical  Status: active
  Phase: Phase 5: Project Intelligence   Sprint: Sprint 32
  Health: 100%   Last active: 0d ago
```

**Health Score Formula:**
- Base value starts at `100`.
- Dropped to `60` if status is `paused`.
- Dropped to `40` if status is `planning`.
- Penalized by `-20` points if `last_active` is greater than 7 days ago.

### 2. Integration Adapters
Tracks live connection and tracking status for external hooks:
- **GitHub**: Target tracking repository name and status.
- **Notion**: Status of task database synchronization.
- **n8n**: Number of associated automation workflows.
- **Knowledge Graph**: Registry Entity ID linking the project into the global graph.

### 3. Open Tasks
Lists the top 5 pending or active tasks.
```
Open Tasks
Task                             Status
Write Phase 5 tests              Pending
Refactor registry               In Progress
```

### 4. Recent Memory Log
Lists the three most recently created project memory entries:
```
Recent Memory
Category     Title                        Date
decisions    Use SQLite for Project Reg   2026-07-14
meetings     Sprint Sync                  2026-07-14
```

---

## Interacting with the Dashboard

```bash
# Render dashboard for the active project
aios project dashboard

# Render dashboard for a specific project
aios project dashboard Agency
```
