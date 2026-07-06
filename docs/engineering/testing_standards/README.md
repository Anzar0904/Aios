# Testing Standards
**Engineering Bible — Milestone 4**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

> [!IMPORTANT]
> This directory defines the **Testing Standards** of the Personal AI OS.
> It outlines the verification methodologies, framework configurations, and quality gates that protect the codebase.
> If any rule here conflicts with the Engineering Bible Foundation layer, the Foundation wins.

---

## Purpose

`docs/engineering/testing_standards/` provides the technical criteria, mock boundaries, and quality targets to ensure that the software remains reliable, secure, and regression-free during automated code edits. It answers:

> **How must I write, mock, organize, and measure tests in this system?**

Every developer and AI agent is required to follow these guidelines before submitting code.

---

## Document Map

```
docs/engineering/testing_standards/
├── README.md                  ← This file — navigation hub
├── testing_standards.md       ← Core playbook, pyramid, and verification gates
├── unit_testing.md            ← Isolated module verification and boundaries
├── integration_testing.md     ← Multi-service collaboration and state isolation
├── regression_testing.md      ← Reproduction workflows and regression guards
├── performance_testing.md     ... Latency targets, capacity limits, and benchmarks
├── mocking_guidelines.md      ← unittest.mock rules, factories, and traps
└── coverage_requirements.md   ← Coverage thresholds, exclusions, and checks
```

---

## Reading Order

| Step | Document | When to Read |
|------|----------|--------------|
| 1 | [testing_standards.md](testing_standards.md) | First — to understand the testing philosophy and gates |
| 2 | [unit_testing.md](unit_testing.md) | Before writing unit tests for isolated utilities |
| 3 | [integration_testing.md](integration_testing.md) | Before verifying multi-service or database transactions |
| 4 | [regression_testing.md](regression_testing.md) | When fixing bugs or creating regression test cases |
| 5 | [performance_testing.md](performance_testing.md) | When testing service latency or optimization loops |
| 6 | [mocking_guidelines.md](mocking_guidelines.md) | Before mocking dependencies or vendor LLM clients |
| 7 | [coverage_requirements.md](coverage_requirements.md) | To audit code coverage before merging changes |

---

## Quick Reference — Testing Constraints

These rules are checked during local pre-release verification runs:

| Metric / Rule | Requirement | Reference Document |
|---------------|-------------|--------------------|
| **Minimum Coverage** | 85% statement and branch coverage | [coverage_requirements.md](coverage_requirements.md) |
| **Execution Dependency** | Zero remote network or host socket dependencies | [testing_standards.md](testing_standards.md) |
| **Pytest Duration** | Suite must execute under 5 seconds | [testing_standards.md](testing_standards.md) |
| **Mocking Boundary** | Dependency injection mock via constructor arguments | [mocking_guidelines.md](mocking_guidelines.md) |
| **Path Isolations** | Use `tmp_path` fixture for all database/file operations | [integration_testing.md](integration_testing.md) |
| **Execution Latency** | Kernel boot & registry lookup < 200ms | [performance_testing.md](performance_testing.md) |
| **Bug Fix Workflow** | Failing regression test written before applying fix | [regression_testing.md](regression_testing.md) |

---

## Relationship to the Engineering Bible Foundation

```
docs/engineering/               ← Foundation (Milestone 1)
     │
     ├── architecture_standards/ ← Architecture Standards (Milestone 3)
     │
     └── testing_standards/     ← YOU ARE HERE (Milestone 4)
              │
              ├── Implements ──▶  engineering_principles.md §2.2 (Verification)
              ├── Enforces   ──▶  06_TESTING_GUIDELINES.md (pytest execution rules)
              └── Validates  ──▶  01_ENGINEERING_GUIDELINES.md (Definition of Done)
```

---

*Engineering Bible Testing Standards · Personal AI OS · Sprint 8 M4 · Governed by [06_TESTING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/06_TESTING_GUIDELINES.md)*
