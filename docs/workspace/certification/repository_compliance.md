# Workspace Intelligence — Repository Discovery Compliance
**Sprint 10 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Verify compliance of directory scanning, VCS root detection, project classification heuristics, and database schema mappings.
* **Scope**: Governs VCS walkers, classification tags, and catalog databases.
* **Audience**: Quality Auditors, Systems Architects, and AI developers.
* **Related Documents**:
  * [workspace/project_discovery/README.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/README.md) - Project Discovery hub.
  * [workspace/project_discovery/workspace_catalog.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/workspace_catalog.md) - SQL catalog schema.

---

## 1. Compliance Audit Objectives

This audit verifies that the **Repository Discovery & Project Classification** layer locates repository boundaries, detects project stacks, and indexes metadata correctly.

---

## 2. Repository Verification Matrix

```
+------------------------------------+------------------------------------+----------+
| Repository Requirement             | Verification Check                 | Status   |
+------------------------------------+------------------------------------+----------+
| 1. Boundary Walkers                | Locates version control root       | PASS     |
|                                    | directories (.git) and nested      |          |
|                                    | submodules.                        |          |
+------------------------------------+------------------------------------+----------+
| 2. Classification Heuristics       | Classifies project languages,      | PASS     |
|                                    | frameworks, and build setups using |          |
|                                    | config triggers.                   |          |
+------------------------------------+------------------------------------+----------+
| 3. SQLite/PostgreSQL Mappings      | Table schemas match the structural | PASS     |
|                                    | hierarchy from Workspace to        |          |
|                                    | Symbols with foreign key cascades. |          |
+------------------------------------+------------------------------------+----------+
| 4. Directory Traversal Guards      | Symlink resolution verifies targets | PASS     |
|                                    | are within workspace roots.        |          |
+------------------------------------+------------------------------------+----------+
```

---

## 3. Compliance Verification Details

### 3.1 Boundary Walker & Symlinks
* Traversal tests verify that nested git submodules are registered as separate child repositories.
* Path validation checks confirm that symlinks pointing outside the workspace root are skipped, preventing path traversal.

### 3.2 SQL Catalog Verification
* The database blueprints verify that deleting a workspace cascade-deletes all child projects, repositories, modules, and symbols, preventing orphaned database records.
* Heuristic check traces verify that projects containing `Cargo.toml` are correctly classified as Rust/Cargo projects, and projects containing `package.json` are classified as JS/TS projects.
