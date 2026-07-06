# Code Coverage Requirements & Auditing
**Engineering Bible — Milestone 4**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Statement & Branch Coverage Targets

To ensure that logical paths in the codebase are systematically verified, the Personal AI OS enforces strict coverage minimums:

* **Codebase-wide Coverage**: The overall coverage target for the codebase is at least **85%**.
* **Branch Coverage Enforcement**: Tests must verify branch paths (like `if`/`else` structures) in addition to statement lines. Code paths must handle both success and error conditions.
* **Code Modification Gate**: Any modified or newly created files must meet the **85%** coverage requirement before they can be merged.

---

## 2. Coverage Exclusions

Some files and code paths are excluded from coverage calculations because they contain minimal business logic or are verified through manual checks.

### Permitted Exclusions
* **CLI Interactivity Loops**: Code inside `cli.py` that handles terminal keyboard input and visual display elements.
* **Visual Rendering Widgets**: Component rendering methods that do not contain business logic.
* **Raw Config Loading**: Configuration parsing and type definitions (`config.py`).
* **Auto-generated Stubs**: Auto-generated API wrappers or interface definitions.

### How to Exclude Paths
* **Pragma Annotations**: Use the `# pragma: no cover` comment inline to exclude specific lines or blocks from coverage reports.
  
  ```python
  if __name__ == "__main__":  # pragma: no cover
      # Boot script execution path
      main()
  ```

* **Configuration Rules**: Path exclusions are defined in `pyproject.toml` under the `[tool.coverage.run]` section.

---

## 3. How to Run Coverage Checks

To run coverage audits locally:

```bash
# Run pytest with coverage reporting
PYTHONPATH=. pytest --cov=core --cov-branch --cov-report=term-missing
```

The command line parameters:
* `--cov=core`: Computes coverage for modules inside the `core/` package.
* `--cov-branch`: Evaluates branch execution metrics.
* `--cov-report=term-missing`: Lists uncovered line numbers in the console output.

---

*Engineering Bible Testing Standards · Personal AI OS · Sprint 8 M4 · Governed by [06_TESTING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/06_TESTING_GUIDELINES.md)*
