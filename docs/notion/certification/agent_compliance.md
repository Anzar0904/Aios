# Notion Intelligence — AI Agent Compliance
**Sprint 9 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Verify compliance of AI agent integrations, context routing protocols, Research and Documentation Agent templates, workload checks, and approval loops.
* **Scope**: Governs tool registrations, agent prompt contexts, workload warning mechanisms, and comment-driven consensus state transitions.
* **Audience**: AI Engineers, Quality Auditors, and System Architects.
* **Related Documents**:
  * [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) - Core system guidelines.
  * [notion/ai_agent_integration/agent_integration.md](file:///Users/anzarakhtar/aios/docs/notion/ai_agent_integration/agent_integration.md) - Agent framework overview.
  * [notion/ai_agent_integration/research_agent.md](file:///Users/anzarakhtar/aios/docs/notion/ai_agent_integration/research_agent.md) - Research Agent specs.
  * [notion/ai_agent_integration/documentation_agent.md](file:///Users/anzarakhtar/aios/docs/notion/ai_agent_integration/documentation_agent.md) - Doc Agent specs.
  * [notion/ai_agent_integration/project_intelligence.md](file:///Users/anzarakhtar/aios/docs/notion/ai_agent_integration/project_intelligence.md) - PM workload mapping.
  * [notion/ai_agent_integration/approval_workflows.md](file:///Users/anzarakhtar/aios/docs/notion/ai_agent_integration/approval_workflows.md) - Approval Consensus.

---

## 1. Compliance Audit Objectives

This audit verifies that the **AI Agent Integration** layer safely exposes workspace tools, processes agent inputs without resource exhaustion, calculates developer workloads against profile capacities, and operates consensus verification loops via comment parsing on Notion pages.

---

## 2. AI Agent Verification Matrix

```
+------------------------------------+------------------------------------+----------+
| AI Agent Requirement               | Verification Check                 | Status   |
+------------------------------------+------------------------------------+----------+
| 1. OmniRoute Context Limits        | Pages exceeding context limits are | PASS     |
|                                    | compressed using semantic search   |          |
|                                    | to top 3 sections.                 |          |
+------------------------------------+------------------------------------+----------+
| 2. Dynamic Tool Registration       | Agent tools (`query_search`,       | PASS     |
|                                    | `get_document`, `update_row`) must |          |
|                                    | register under `ToolService`.      |          |
+------------------------------------+------------------------------------+----------+
| 3. Research Template Structure     | Research reports must follow standard| PASS     |
|                                    | Markdown templates (Summary, Spec, |          |
|                                    | Analysis, Citations).              |          |
+------------------------------------+------------------------------------+----------+
| 4. Targeted Wiki Patching          | Documentation Agent updates tables  | PASS     |
|                                    | using block ID edits, preventing   |          |
|                                    | overwrites of custom human text.   |          |
+------------------------------------+------------------------------------+----------+
| 5. PM Workload Calculations        | Warn user in REPL when open tasks  | PASS     |
|                                    | exceed weekly capacity in profile. |          |
+------------------------------------+------------------------------------+----------+
| 6. Approval Consensus Loop         | Scans Notion comments for LGTM/    | PASS     |
|                                    | Reject to transition release states|          |
|                                    | to Approved / Changes Requested.   |          |
+------------------------------------+------------------------------------+----------+
```

---

## 3. Compliance Verification Details

### 3.1 Context Optimization & Routing
* Execution traces confirm that when pages exceed the target token threshold, OmniRoute limits incoming text by querying the local semantic vector store to inject only the top 3 high-cosine similarity chunks.
* Verification of `offline_mode` confirms that agent workspace calls are successfully rerouted to local SQLite databases and Qdrant replicas without throwing unhandled network exceptions.

### 3.2 Workspace Automation & Wiki Preservation
* The Documentation Agent parser locates the `[DOC_AGENT_SECTION]` marker block inside Notion pages and issues precise `PATCH` requests. This prevents full-page overwrites, keeping user discussion boards and custom headers safe.
* Research Agent runs publish structured Markdown to the research namespace according to specifications, matching metadata and source URL reference tables.

### 3.3 Task Allocation & Consensus Transitions
* Profile workload tests verify that task tickets assigned to a profile are extracted and matched against weekly hour limits in `personal_profiles.json`, printing warnings to the REPL when overload occurs.
* Approval Engine evaluations check active pages, parses comments for approval keywords, and correctly signs off on releases by updating the `Consensus Date` and setting the status to `Approved` once the consensus threshold is met.
