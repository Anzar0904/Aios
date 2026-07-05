# Query Analysis Architecture

This document describes the intent classification heuristics, search domain detection rules, and retrieval strategy parameters.

---

## 1. Intent Classification

Queries are classified using keywords:
* **`code_search`**: Triggered by keywords: `def `, `class `, `import `, `code`, `fn`, `function`.
* **`conversation_history`**: Triggered by keywords: `who`, `what`, `how`, `why`, `chat`, `msg`.
* **`automation_workflow`**: Triggered by keywords: `automation`, `trigger`, `workflow`, `run`.
* **`general_knowledge`**: Default classification if no other keywords match.

---

## 2. Domain & Scope Detection

* **Search Domains**: Maps intent to target collections (e.g. `code_search` maps to `engineering` and `documentation` domains).
* **Workspace/Project Scope**: Parsed from context metadata to construct filter arguments.
* **Complexity Estimation**: Queries containing more than 6 words are marked as `complex`, prompting larger candidate recall sizes.
