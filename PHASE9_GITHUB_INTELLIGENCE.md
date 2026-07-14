# Phase 9: GitHub Intelligence

> **Status:** ✅ Production — 20/20 Tests passing

## Overview

Phase 9 establishes the **GitHub Intelligence Layer** for the AI OS, transforming it into an engineering command center. It unifies repo management, branches, commits history, PR reviewers risk profiles, open issue priority analysis, actions workflows builds, and release versions.

All GitHub nodes (`Repository`, `Branch`, `Commit`, `PullRequest`, `Issue`, `Release`, `Workflow`) and relations (`CONTAINS`, `CREATED_BY`, `REFERENCES`, `MERGES`, `DEPENDS_ON`, `RELATED_TO`, `GENERATED_FROM`) are integrated natively with the Universal Knowledge Graph.

---

## Subsystems

1. **Repository Registry**: A centralized SQLite directory cataloging repo namespaces, stars, open issue counts, default branches, and overall health scores.
2. **Pull Request Analyzer**: Scans code changes, assesses PR risk factors, and provides review state tracking.
3. **Issue Intelligence**: Classifies open issues and ranks priorities (1 to 5).
4. **CI Workflow Auditor**: Tracks actions run statuses, run durations, failure rates, and suggests repair steps.
5. **Releases Catalog**: Logs tag updates, features log checklists, and assets.
6. **Repository Health Engine**: Computes overall health ratings by applying point deductions for open issues, failed builds, and PR risk averages.

---

## Database Schemas

See [REPOSITORY_REGISTRY_GUIDE.md](file:///Users/anzarakhtar/aios/REPOSITORY_REGISTRY_GUIDE.md) for full SQLite specifications.

---

## CLI Command Summary

```bash
aios github                          # Render the engineering command center dashboard
aios github repos                    # List all registered repositories namespaces
aios github branches                 # Browse branches listed for the default repo
aios github commits                  # View commits author timelines and messages
aios github prs                      # Audit pull requests files changed and risk scores
aios github issues                   # Inspect issues priority score ranks and assignees
aios github actions                  # Audit actions builds workflows execution statuses
aios github releases                 # Browse version releases features lists
aios github analytics                # Print commit velocity graphs and growth metrics
aios github health                   # Run health scoring algorithms and print scores
```
