# Pull Request Intelligence Guide

The PR Analyzer monitors files changed, calculates risk levels, and registers review states.

---

## 1. Database Schema

Stored in `~/.aios_github_intel.db`:

```sql
CREATE TABLE pull_requests (
    pr_id           TEXT PRIMARY KEY,
    pr_number       INTEGER NOT NULL,
    repository_id   TEXT NOT NULL,
    title           TEXT NOT NULL,
    author          TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'open', -- open|closed|merged
    files_changed   INTEGER NOT NULL DEFAULT 0,
    risk_score      INTEGER NOT NULL DEFAULT 10,
    review_state    TEXT NOT NULL DEFAULT 'pending', -- approved|changes_requested
    created_at      REAL NOT NULL,
    UNIQUE(repository_id, pr_number)
);
```

---

## 2. Risk Scoring

- **Low Risk (0-30)**: Minimal changes, documentation updates, standard templates.
- **Medium Risk (31-60)**: Modifies core service modules, interfaces, or command loops.
- **High Risk (61-100)**: Modifies critical security vaults, database schemas, or migration paths.

---

## 3. CLI Management

```bash
# Browse open pull requests
aios github prs
```
