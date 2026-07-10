# CLI & UX Architecture Guide

This document describes the design architecture, modules, and data flow of the CLI.

---

## 1. System Overview
```mermaid
graph TD
    CLI[aios Entry Point] --> UX[UX Polish Modules]
    CLI --> CMD[Command Registry]
    UX --> Boot[Boot Experience]
    UX --> Progress[Progress Engine]
    UX --> Err[Error Reporter]
    UX --> Diagnostics[Diagnostics telemetry]
    UX --> Session[Session Manager]
```

---

## 2. Component Flows
- **Centralized Middleware Integration**: Intercepts command runs to check validation rules.
- **Persistent Cache States**: Saves session info to `.agent/session.json`.
- **Keyboard Hook bindings**: Bind `Ctrl+K` and `Ctrl+L` in `cli.py` to trigger palette and clear operations.
