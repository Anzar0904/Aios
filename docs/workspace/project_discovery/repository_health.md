# Repository Health Metrics Spec
**Sprint 10 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define metrics, evaluation indexes, and formulas for calculating the health score of development repositories.
* **Scope**: Governs static analysis ratings, testing outputs, build health tracking, and version drift checks.
* **Audience**: Quality Assurance Auditors, Tech Leads, and AI agents.
* **Related Documents**:
  * [workspace/capabilities.md](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) - Capabilities domains.
  * [workspace/project_discovery/repository_metadata.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/repository_metadata.md) - Metadata specs.

---

## 1. Health Index Dimension Breakdown

The overall **Repository Health Index (RHI)** evaluates code quality, environment state, and compilation reliability out of 100.0 points.

```
+------------------------------------+------------------------------------+----------+
| Health Dimension                   | Target / Perfect Metric            | Weight   |
+------------------------------------+------------------------------------+----------+
| 1. Build & Compilation Health      | Zero build failures or warnings    | 30%      |
+------------------------------------+------------------------------------+----------+
| 2. Test Pass Ratio                 | 100% test suites passing           | 30%      |
+------------------------------------+------------------------------------+----------+
| 3. Code Coverage                   | > 85% statement/branch coverage    | 20%      |
+------------------------------------+------------------------------------+----------+
| 4. Static Code Quality (Lints)     | Zero critical errors or warnings   | 10%      |
+------------------------------------+------------------------------------+----------+
| 5. Dependency Freshness            | Zero out-of-date or insecure pkgs  | 10%      |
+------------------------------------+------------------------------------+----------+
```

---

## 2. Health Calculations & Formulas

The AI OS calculates health scores dynamically by query local build logs and static test runners:

### 2.1 Build & Compilation (30 Points)
* **Score**: 30 points if the last compiler run outputted zero errors or warnings.
* **Deductions**:
  * Build Failure: **-30 points** (RHI Build component drops to 0).
  * Build Warnings: **-3 points per distinct warning file** (capped at -15).

### 2.2 Test Pass Ratio (30 Points)
* **Formula**:
  $$\text{Score} = 30 \times \left( \frac{\text{Passed Tests}}{\text{Total Executed Tests}} \right)$$
* **Deductions**: If any test suite fails, it triggers an alert in the REPL console, and the score drops proportionally.

### 2.3 Code Coverage (20 Points)
* **Formula**:
  $$\text{Score} = 20 \times \left( \frac{\text{Branch Coverage \%}}{85\%} \right) \quad (\text{capped at 20})$$

### 2.4 Static Quality / Lints (10 Points)
* **Deductions**:
  * Lint Error: **-2 points per error** (capped at -10).
  * Lint Warning: **-0.5 points per warning** (capped at -5).

### 2.5 Dependency Freshness (10 Points)
* **Deductions**:
  * Vulnerable Package Detected: **-5 points per vulnerability**.
  * Out-of-date Major Version Package: **-1 point per package** (capped at -5).
