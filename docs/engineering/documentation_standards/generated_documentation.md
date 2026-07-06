# Generated Documentation & Verification
**Engineering Bible — Milestone 5**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Automated Documentation Generators

To provide detailed code references without manual overhead:
* **Sphinx API Compiler**: System manuals are compiled using Sphinx and the `sphinx-apidoc` tool.
* **Docstring Validation**: Public modules must pass docstring style checks (using `pydocstyle`) to ensure arguments, return values, and exceptions are documented consistently.
* **Typing Checks**: Code is run through type checkers (`mypy`) to verify typing annotations on public APIs before doc compilation.

---

## 2. Automated Hyperlink Verification

To prevent broken links across documentation files:
* **Link Verification Sweep**: Runs before releases using link checker tools (e.g. `markdown-link-check` or custom regex scanners).
* **Link Checking Rules**:
  * All `file:///` paths must resolve to valid files inside the workspace.
  * Markdown anchors (like `#1-the-test-pyramid`) must map to actual heading strings in target files.
  * Local image assets (located in `assets/` or `design/`) must resolve to valid image files.

---

## 3. Pre-Release Documentation Checklist

Before staging code changes for commit, developers and AI agents must run documentation validation checks:

```bash
# Run pydocstyle docstring checks
pydocstyle core/src/aios/

# Run mypy typing verification
mypy core/src/aios/

# Execute local link checker checks
python core/src/aios/docgen/check_links.py
```

Code changes are not ready for merge if docstring styling checks fail, type definitions are missing, or documentation links are broken.

---

*Engineering Bible Documentation Standards · Personal AI OS · Sprint 8 M5 · Governed by [07_DOCUMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/07_DOCUMENTATION_GUIDELINES.md)*
