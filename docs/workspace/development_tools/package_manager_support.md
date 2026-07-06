# Package Managers & Dependencies Spec
**Sprint 10 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define metadata extraction structures and validation check loops for tracking dependencies.
* **Scope**: Governs lockfiles, drift monitoring, license checks, and vulnerability scanners.
* **Audience**: Systems Integrators, DBAs, and Lead Developers.
* **Related Documents**:
  * [workspace/project_discovery/dependency_graph.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/dependency_graph.md) - Graph specifications.
  * [workspace/development_tools/build_systems.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/build_systems.md) - Build systems.

---

## 1. Package Manager Support Matrix

The system tracks package files to coordinate local runtimes:
* **Python**: Poetry (`poetry.lock`), Pip (`requirements.txt`, `constraints.txt`), Pipenv (`Pipfile.lock`).
* **JavaScript / TypeScript**: Npm (`package-lock.json`), Yarn (`yarn.lock`), Pnpm (`pnpm-lock.yaml`).
* **Rust**: Cargo (`Cargo.lock`).

---

## 2. Lockfile Integrity & Drift Detection

* **Lock Integrity Checks**: Computes SHA-256 hashes of configuration files (e.g. `pyproject.toml`) and checks them against lockfile headers.
* **Environment Drift Auditing**: Scans active libraries installed in virtual environments (e.g., via `pip list` or `npm list`) and flags mismatching or missing packages.
* **Resolution Prompts**: If drift is detected, the AI OS prints a warning:
  ```
  [Dependency Drift Warning]
  Local dependencies do not match poetry.lock.
  Missing packages: 'qdrant-client >= 1.9.0'
  Would you like the AI OS to run 'poetry install'? [y/N]
  ```

---

## 3. License Auditing & Vulnerability Scans

To maintain project compliance:
* **Vulnerability Scanning**: Integrates with local vulnerability checkers (e.g. `safety` for Python, `npm audit` for JS, `cargo audit` for Rust) to scan lockfiles in background loops.
* **License Blacklist Checks**: Evaluates package licenses against a blacklist (e.g., blocking GPL-3.0 libraries in proprietary workspaces).
* **Alert Trigger**: If an agent attempts to install a package that violates security or license policies, the AI OS blocks the action and prompts the user for approval.
