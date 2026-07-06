# Research Planning & Replanning Spec
**Sprint 11 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define DAG planner generation, execution tracking, and error-driven replanning rules for research tasks.
* **Scope**: Governs execution step graphs, crawler checks, and fallback triggers.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [workspace/orchestration/execution_planning.md](file:///Users/anzarakhtar/aios/docs/workspace/orchestration/execution_planning.md) - Workspace planning.
  * [research/source_discovery/crawler_architecture.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/crawler_architecture.md) - Crawler structures.

---

## 1. DAG Research Planner

The **Research Planner** converts high-level objectives (e.g. "research JWT validation rules") into a Directed Acyclic Graph (DAG) of task steps ($G_{plan} = (V_{steps}, E_{dependencies})$):

```
       [Step 1: Search provider links]
                |
                v
      [Step 2: Scrape raw content]
                |
                v
       [Step 3: Parse to Markdown]
         /             \
    (Success)        (Failure)
       /                 \
      v                   v
[Step 4: Verify facts]   [Step 5: Retry Scrape] ===> Link back to Step 2
```

* **Nodes ($V_{steps}$)**: Custom tool executions (e.g. `QuerySearch`, `ScrapeURL`, `ExtractConcepts`, `VerifyClaims`).
* **Dependencies ($E_{dependencies}$)**: Execution orders (e.g. Step 3 cannot run until Step 2 completes).

---

## 2. Error-Driven Replanning Loop

When a step fails (e.g. hitting a rate limit or DNS block):
1. **Analyze Failure**: The planner captures stderr outputs, HTTP status codes, and connection logs.
2. **Diagnose**: Identifies the cause of the failure (e.g. HTTP 429 Rate Limit, HTTP 404 Missing page).
3. **Generate Fix**:
   * If rate-limited: Appends a wait step and schedules a retry with exponential back-off.
   * If the page is missing (404): Removes the target URL and schedules queries targeting alternative search providers.
4. **Mutate DAG**: Updates the execution graph to continue the task.
