# Release Notes — Personal AI OS v1.0.0 (Release Candidate)

We are thrilled to present the first stable production release of the Personal AI OS!

This release transitions the system from independent subsystems into a unified, secure, polished, and production-grade terminal operating system.

---

## 🌟 Key Highlights

### 1. Unified Operating System Shell (`aios`)
- Launches a premium startup boot loading experience with active health status checks.
- Connects an interactive shell with auto-completion (Tab), Ctrl+K fuzzy command palette, Ctrl+L screen clear, and multi-line modes.
- Supports 16 slash commands (e.g., `/project`, `/status`, `/models`, `/clear`, `/exit`) to inspect and configure subsystems.

### 2. Approval Engine & Governance Middleware (Sprint 30)
- Guardrails all high-impact actions (deletes, deploys, merges) behind a centralized middleware gateway.
- Enforces scoped security policies (`Action -> Project -> Client -> Global`) configured in `.agent/approval/policies.json`.
- Restricts queue file permissions securely to owner-only (`0600`).

### 3. Business & Project Intelligence (Sprint 28-29)
- Registers all workspaces, scans file dependencies, and assesses technical project risks.
- Manages client agencies portfolios, budgets, timelines, and n8n workflow task allocations.

---

## 🚀 Getting Started
```bash
# 1. Install local packages
pip install -e .

# 2. Run the onboarding setup wizard
aios setup

# 3. Start the interactive shell
aios
```
