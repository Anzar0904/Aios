# Codebase Quality & Health Metrics
**Sprint 10 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define metrics, evaluation logic, and scoring formulas for calculating code quality indices.
* **Scope**: Governs complexity ratings, docstring coverage checks, and code duplication analysis.
* **Audience**: Quality Auditors, Tech Leads, and AI agents.
* **Related Documents**:
  * [workspace/capabilities.md](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) - Capabilities domains.
  * [workspace/project_discovery/repository_health.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/repository_health.md) - Repository health.

---

## 1. Codebase Quality Score (CQS)

The **Codebase Quality Score (CQS)** evaluates structural code clarity, formatting consistency, duplication ratios, and documentation completeness out of 100.0 points.

```
+------------------------------------+------------------------------------+----------+
| Quality Dimension                  | Evaluation Criteria                | Weight   |
+------------------------------------+------------------------------------+----------+
| 1. Cognitive Complexity            | Low cyclomatic/cognitive nested    | 30%      |
|                                    | structures inside modules.         |          |
+------------------------------------+------------------------------------+----------+
| 2. Documentation Coverage          | Docstrings present on all classes, | 30%      |
|                                    | methods, and exports.              |          |
+------------------------------------+------------------------------------+----------+
| 3. Code Duplication Ratio          | Zero copy-pasted blocks of text    | 20%      |
|                                    | exceeding threshold.               |          |
+------------------------------------+------------------------------------+----------+
| 4. Lint Warning Density            | Standard coding standards pass     | 20%      |
|                                    | (Ruff/ESLint).                     |          |
+------------------------------------+------------------------------------+----------+
```

---

## 2. Metrics & Evaluation Rules

### 2.1 Cognitive Complexity (30 Points)
* **Objective**: Evaluate nesting levels of loops, conditions, and branch conditions using the AST:
  * For each control flow node (`if`, `for`, `while`, `try`, nested function), increment complexity count.
  * Target: Average complexity per method ≤ **10**.
* **Formula**:
  $$\text{Score} = 30 \times \left( 1 - \frac{\text{Methods exceeding limit}}{\text{Total Methods}} \right)$$

### 2.2 Documentation Coverage (30 Points)
* **Objective**: Check that public class definitions and exported functions contain valid docstrings:
* **Formula**:
  $$\text{Score} = 30 \times \left( \frac{\text{Symbols with Docstrings}}{\text{Total Symbols}} \right)$$

### 2.3 Code Duplication (20 Points)
* **Objective**: Identify matching code structures (using token hashes rather than raw text spacing):
  * Blocks of code matching exactly for 6 or more lines are flagged.
* **Formula**:
  $$\text{Score} = 20 \times \left( 1 - \frac{\text{Duplicated Lines}}{\text{Total Codebase Lines}} \right)$$

### 2.4 Lint Warning Density (20 Points)
* **Objective**: Count formatting issues and code quality rules alerts:
* **Formula**:
  $$\text{Score} = 20 - (2 \times \text{Errors}) - (0.2 \times \text{Warnings}) \quad (\text{capped at 0 to 20})$$
