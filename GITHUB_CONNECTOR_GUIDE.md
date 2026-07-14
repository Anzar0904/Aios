# GitHub Connector Guide

The GitHub Connector links repositories, pull requests, issues, and releases to AI OS context engines.

---

## 1. Capabilities

- **Repository Discovery**: Scans target Git namespaces to map repositories (e.g. `Anzar0904/Aios`).
- **PR Monitoring**: Listens for pull requests, checking statuses and logs.
- **Issue Tracking**: Polls active repository issues.
- **Release Monitoring**: Tracks tag creations.

---

## 2. CLI Invocation

To authenticate and trigger discoveries:

```bash
# Connect using GitHub token
aios integrations connect github oauth_token ghp_my_github_token_val

# Trigger discovery sync
aios integrations sync github
```
