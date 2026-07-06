# Source Control & Engineering Metrics Spec
**Sprint 10 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define engineering metrics, calculation queries, and classifications for source control analytics.
* **Scope**: Governs Git commit churn metrics, lead time calculations, and size divisions.
* **Audience**: Product Managers, Tech Leads, and AI agents.
* **Related Documents**:
  * [workspace/project_discovery/repository_health.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/repository_health.md) - Repository health.
  * [workspace/source_control/commit_analysis.md](file:///Users/anzarakhtar/aios/docs/workspace/source_control/commit_analysis.md) - Commit parsing.

---

## 1. Engineering Metrics Dashboard

The **Source Control Metrics** module extracts repository metrics to evaluate team velocity, code stability, and process bottlenecks:

```
+------------------------------------+------------------------------------+----------+
| Source Control Metric              | Calculation Methodology            | Purpose  |
+------------------------------------+------------------------------------+----------+
| 1. Commit Frequency                | Count commits per active developer | Velocity |
|                                    | profile per week.                  |          |
+------------------------------------+------------------------------------+----------+
| 2. Code Churn                      | Sum of lines added and deleted      | Quality  |
|                                    | over 7-day windows.                |          |
+------------------------------------+------------------------------------+----------+
| 3. Mean Time to Merge (MTTM)       | Time elapsed from branch creation  | Process  |
|                                    | to merge commit DAG integration.   |          |
+------------------------------------+------------------------------------+----------+
| 4. Lead Time for Changes           | Time elapsed from local commit     | Delivery |
|                                    | to production release tagging.     |          |
+------------------------------------+------------------------------------+----------+
```

---

## 2. Commit Churn & Size Classifications

* **Code Churn**: Tracks code churn metrics. High churn in a single file indicates code instability or incomplete requirements.
* **Commit Size Classifications**:
  * **Small (S)**: **< 50 lines changed**. Recommended size for rapid reviews.
  * **Medium (M)**: **50–250 lines changed**. Normal feature commits.
  * **Large (L)**: **> 250 lines changed**. Flagged by the AI OS with warnings advising splitting the changes to ease reviews:
    ```
    [Source Control Warning]
    Proposed commit size is Large (320 lines changed).
    Please consider splitting modifications into smaller, scoped commits.
    ```

---

## 3. Delivery Performance Calculations

The metrics engine runs background calculations:
* **MTTM Formula**:
  $$\text{MTTM} = \frac{\sum (\text{Merge Commit Timestamp} - \text{Branch Start Commit Timestamp})}{\text{Total Merged Branches}}$$
* **Lead Time**: Computes the duration between the earliest commit on a branch and the release tag applied to that branch, helping identify delivery delays.
* **Active Profile Matching**: Maps all metrics to profile records in `personal_profiles.json` to monitor user development metrics.
