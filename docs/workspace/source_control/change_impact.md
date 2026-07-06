# Change Impact Analysis Spec
**Sprint 10 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define impact estimation metrics, downstream dependency queries, and risk rating calculations.
* **Scope**: Governs static analysis risk engines, test failures models, and import ripple checks.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Lead Developers.
* **Related Documents**:
  * [workspace/codebase/dependency_analysis.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/dependency_analysis.md) - Module dependency analysis.
  * [workspace/source_control/commit_analysis.md](file:///Users/anzarakhtar/aios/docs/workspace/source_control/commit_analysis.md) - Commit mapping.

---

## 1. Downstream Impact Tracker

Before an agent commits code changes, the **Change Impact** engine trace dependencies to identify downstream modules affected by the modifications:

```
[Target Code Modification] (e.g. Modify Class X in Module A)
             |
             v
[Parse Class X Usage] ===> Query codebase_symbols index
             |
             v
[Trace Import Chains] ===> Scan IMPORTS edges in dependency graph
             |
             +---> Module B imports Module A -> Flag Module B
             +---> Module C imports Module B -> Flag Module C
             |
             v
[Compile Impact List] ===> Identify affected tests and modules
```

1. **Usage Resolution**: Resolves where modified classes or functions are referenced across the codebase.
2. **Import Tree Traversal**: Recursively traverses `IMPORTS` edges in the dependency graph to compile an impact list of affected files.

---

## 2. Test Execution Mapping

To speed up verification runs, the engine maps code files to corresponding test suites:
* **Test Classifiers**: Identifies test modules associated with changed files (e.g. modifications to `aios/services/knowledge_hub_impl.py` map to `core/tests/test_knowledge_hub.py`).
* **Targeted Verification Runs**: Instead of executing the entire test suite, the AI OS runs only the tests in direct import paths, conserving CPU time.

---

## 3. Commit Risk Metrics

The system calculates a **Commit Risk Index** (Low, Medium, High) for proposed changes:
* **Formula Indicators**:
  * **Number of files changed**: More files increase risk.
  * **Cognitive complexity delta**: Large increases in complexity raise risk.
  * **Downstream Dependency count**: Modifications to highly imported modules (e.g. `config.py`, `registry.py`) are flagged as **High Risk**, requiring stricter test validation and manual user confirmation before pushing.
