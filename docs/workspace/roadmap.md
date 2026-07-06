# Workspace Intelligence — Roadmap & Milestones
**Sprint 10 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the development milestones, dependency graphs, delivery schedule, and risk mitigation strategies for Workspace Intelligence.
* **Scope**: Governs Sprint 10 engineering goals and validation checklists.
* **Audience**: Product Managers, Development Leads, and QA Engineers.
* **Related Documents**:
  * [09_ROADMAP.md](file:///Users/anzarakhtar/aios/docs/09_ROADMAP.md) - Core system roadmap.
  * [workspace/README.md](file:///Users/anzarakhtar/aios/docs/workspace/README.md) - Navigation hub.

---

## 1. Development Milestones (Sprint 10)

```
   [M1: Foundation] ===> [M2: Git & Repos] ===> [M3: Build & Compilers]
                                                        |
                                                        v
   [M7: Certification] <=== [M6: Multi-Workspace] <=== [M4 & M5: LSP & CLI]
```

---

## 2. Milestone Details

### Milestone 1: Workspace Intelligence Foundation (Current)
* **Objective**: Establish the core product vision, technical architecture, and security guidelines. Define models for file ASTs, build tasks, and terminal streams.
* **Status**: **COMPLETE** ✅

### Milestone 2: Repository Discovery & Git State Integration
* **Objective**: Implement filesystem walkers that scan projects, read `.git` metadata, monitor staged/unstaged changes, and parse patch diffs.
* **Dependencies**: Milestone 1.

### Milestone 3: Compiler & Build System Integration
* **Objective**: Build integrations for package manager locks (`poetry`, `pip`, `npm`) and compiler log parsers. Construct dependency imports graph database.
* **Dependencies**: Milestone 2.

### Milestone 4: IDE Sync & LSP Integration
* **Objective**: Connect the AI OS to local language servers (LSP), allowing agents to query types, signatures, definition locations, and hover documentation.
* **Dependencies**: Milestone 3.

### Milestone 5: Terminal Stream Observability
* **Objective**: Implement the sandboxed shell wrapper and stdout/stderr stream monitors. Set up command timeouts and regex exit detectors.
* **Dependencies**: Milestone 3.

### Milestone 6: Multi-Workspace Coordination
* **Objective**: Build coordination interfaces that allow agents to manage multiple local repos simultaneously, tracing dependencies across directories.
* **Dependencies**: Milestones 4 and 5.

### Milestone 7: Workspace Intelligence Certification
* **Objective**: Conduct compliance audits of the workspace module, ensuring security, performance, and coverage metrics meet expectations.
* **Dependencies**: Milestone 6.

---

## 3. Risk Assessment & Mitigation Matrix

| Risk Event | Severity | Probability | Mitigation Strategy |
|------------|----------|-------------|---------------------|
| **Memory Footprint Exceeded** | High | Medium | Implement Qdrant batch uploading and limit symbol indexing to directories containing source code (ignore node_modules, dist, etc.). |
| **AST Compilation Overhead** | Medium | High | Cache file hashes (SHA-256) in SQLite. Re-parse files only when timestamps or content hashes change. |
| **Command Sandbox Escape** | Critical | Low | Strip all dangerous environment keys. Parse arguments into shlex arrays to bypass raw shell concatenations. |
| **Compiler Loop Lock** | High | Medium | Enforce strict subprocess timeouts. Kill any spawned task exceeding the liveness duration limits. |
