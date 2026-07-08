# Architectural Rules Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Address the final Task 3 reviewer's spec compliance findings regarding architectural layering and validation.

**Architecture:** Update `ArchitectureRuleEngine.validate` to filter out test files from index data first, change the check preventing Layer 4 engines from importing Layer 5 skills to block it (from `<=` 3 to `<=` 4), and add an explicit check to block Layer 3 (Service) from importing Layer 4 (Execution Engine). Update test cases in `core/tests/test_engineer_rules.py` accordingly.

**Tech Stack:** Python 3.14, pytest, ruff

## Global Constraints
- Do not mutate objects where immutability is expected.
- Maintain test coverage targets (80%+).
- Format commit message correctly using Conventional Commits.

---

### Task 1: Update Architecture Rules Validation and Add Test Cases

**Files:**
- Modify: `core/src/aios/services/engineer/rules.py`
- Modify: `core/tests/test_engineer_rules.py`

**Interfaces:**
- `ArchitectureRuleEngine.validate()` -> Returns List of violations.

- [ ] **Step 1: Write the failing tests**
Add/update the following tests in `core/tests/test_engineer_rules.py`:
- Update `test_core_to_skill_scope_constraints` to assert that Layer 4 importing Layer 5 is a violation.
- Add `test_service_to_engine_layering_violation` to verify that Service (Layer 3) importing Execution Engine (Layer 4) is a violation.
- Add `test_skip_test_files_validation` to verify test files are excluded from validation.

- [ ] **Step 2: Run tests to verify they fail**
Run: `.venv/bin/pytest core/tests/test_engineer_rules.py`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**
Modify `core/src/aios/services/engineer/rules.py`:
- Filter `idx_data` at the start of `validate()` to exclude files where `"tests/" in filepath` or `os.path.basename(filepath).startswith("test_")`.
- Update the check `if source_layer <= 3 and target_layer == 5:` to `if source_layer <= 4 and target_layer == 5:`.
- Add check:
```python
                # Rule: Service Layer (Layer 3) must never import Execution Engine (Layer 4)
                if source_layer == 3 and target_layer == 4:
                    violations.append({
                        "type": "layering_violation",
                        "description": (
                            f"Layering violation: Service module "
                            f"'{os.path.basename(filepath)}' (Layer {source_layer}) "
                            f"imports Execution Engine module '{imp}' (Layer {target_layer})."
                        )
                    })
```

- [ ] **Step 4: Run tests to verify they pass**
Run: `.venv/bin/pytest core/tests/test_engineer_rules.py`
Expected: PASS

- [ ] **Step 5: Run ruff check**
Run: `.venv/bin/ruff check core/src/aios/services/engineer/rules.py core/tests/test_engineer_rules.py`
Expected: PASS with no issues.

- [ ] **Step 6: Commit**
Run git commit with:
`git add core/src/aios/services/engineer/rules.py core/tests/test_engineer_rules.py`
`git commit -m "fix(engineer): refine architectural rules validation and skip tests"`
