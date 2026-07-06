# Regression Testing Standards
**Engineering Bible — Milestone 4**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Regression Testing Philosophy

A regression test ensures that a fixed bug does not return during future updates. To guard against regressions, developers and AI agents must follow a strict bug-fix verification loop.

---

## 2. Bug Reproduction Rule

Code corrections are prohibited until a failing test case has been written that reproduces the issue.

### The Bug-Fix Verification Loop
1. **Reproduce**: Write a test case that triggers the reported defect. Run the test and verify that it fails with the expected error.
2. **Commit Test (Optional)**: Commit the failing test to a branch to document the regression.
3. **Correct**: Apply the code change to fix the defect.
4. **Verify**: Run the test case again to ensure it now passes.
5. **Full Run**: Execute the entire test suite to verify that the fix has not introduced new regressions.

---

## 3. Capture & Replay Workflows

For issues related to LLM prompt routing or execution planning:
* **Plan Mocking**: Replay the bug using recorded model output files. Save the model's json response structures as test fixtures and verify that the parsing, tool-binding, and execution engines handle the input correctly.
* **Trace Logging**: Parse past execution trace files to extract arguments that caused failures, using them to construct regression test inputs.

---

## 4. Organizing the Regression Suite

To keep test execution organized, regression tests must be tagged using pytest decorators:
* **Decorator Tagging**: Add `@pytest.mark.regression` to regression tests.
* **Run Regression Separately**: You can run the regression suite independently using the command line:

```bash
# Run regression tests only
pytest -m regression
```

* **Include in Main Test Run**: All regression tests must be included in the main `pytest` suite execution and run locally on every commit.

---

*Engineering Bible Testing Standards · Personal AI OS · Sprint 8 M4 · Governed by [06_TESTING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/06_TESTING_GUIDELINES.md)*
