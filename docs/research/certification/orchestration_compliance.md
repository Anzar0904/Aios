# Research Intelligence — Orchestration Compliance
**Sprint 11 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Verify compliance of research planners, context compilers, background walkers, and approvals.
* **Scope**: Governs planners, context, and approvals.
* **Audience**: AI Engineers, Quality Auditors, and System Architects.
* **Related Documents**:
  * [research/orchestration/README.md](file:///Users/anzarakhtar/aios/docs/research/orchestration/README.md) - Research Orchestration hub.
  * [research/orchestration/research_orchestration.md](file:///Users/anzarakhtar/aios/docs/research/orchestration/research_orchestration.md) - Coordinator.

---

## 1. Compliance Audit Objectives

This audit verifies that the **AI Research Orchestration** layer manages research plans, compresses prompt contexts, runs background walkers, and prompts the user for approvals.

---

## 2. Orchestration Verification Matrix

```
+------------------------------------+------------------------------------+----------+
| Orchestration Requirement          | Verification Check                 | Status   |
+------------------------------------+------------------------------------+----------+
| 1. DAG Research Planner            | Resolves execution steps (Search,  | PASS     |
|                                    | Fetch, Parse) and handles failures.|          |
+------------------------------------+------------------------------------+----------+
| 2. Context Compiler (OmniRoute)    | Summarizes text and filters out    | PASS     |
|                                    | boilerplate when over token limit. |          |
+------------------------------------+------------------------------------+----------+
| 3. Governance Approval Gates       | Outbound scrapers block / prompt   | PASS     |
|                                    | before running high-volume tasks.  |          |
+------------------------------------+------------------------------------+----------+
| 4. Background Walkers              | Walk sitemaps and parse new RFCs   | PASS     |
|                                    | in the background.                 |          |
+------------------------------------+------------------------------------+----------+
```

---

## 3. Compliance Verification Details

### 3.1 Planners & Context
* Planner checks verify that scraping errors (e.g. HTTP 404) trigger replanning steps targeting alternative links.
* Context compilers use signature extractions and relevance filtering to fit research context into token windows.

### 3.2 Governance & Approvals
* Governance tests confirm that high-volume downloads (e.g. > 50 pages) trigger user approval challenges.
* Web scraper adapters encrypt API keys in the database using SQLCipher, preventing key leaks.
