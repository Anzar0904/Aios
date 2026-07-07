# Notion Intelligence — Approval Workflows
**Sprint 9 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the integration patterns between the Approval Engine and Notion databases, tracking consensus status states and review logs.
* **Scope**: Governs approval state machines, database trackers, and status update callbacks.
* **Audience**: Backend Developers, Integration Engineers, and QA Architects.
* **Related Documents**:
  * [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md) - Approval Engine Service data structures.
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - Comments and databases mappings.

---

## 1. Approval Engine Integration

The **`ApprovalEngineService`** (documented in [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md)) coordinates code releases and quality evaluations. 

The service updates database states and writes consensus summaries to Notion:

```
 [Code Ready / PR Opened] ===> Spawns Approval Evaluation
                                    |
                        [Create Approval Report Row] ===> Writes to Notion database
                                    |
                         [Initiate Review Cycle] ===> Syncs comment threads
                                    |
                         [Evaluate Consensus] ===> Checks votes / reviews
                                    |
                           [Update Status Board]
                           /                 \
                     Consensus             Rejected
                        /                       \
                       v                         v
              [Status: "Approved"]       [Status: "Changes Requested"]
```

---

## 2. Database Approval Schema

The database tracker table on Notion uses specific columns to monitor and process approval states:

```
+------------------+------------------------+---------------------------------------+
| Column Name      | Notion Property Type   | Purpose                               |
+------------------+------------------------+---------------------------------------+
| Release Version  | Title                  | Target version tag (e.g. `v1.0.0`).   |
+------------------+------------------------+---------------------------------------+
| Evaluator Score  | Number                 | Compiled quality metric score.        |
+------------------+------------------------+---------------------------------------+
| Status           | Select                 | `Pending`, `Changes Requested`,       |
|                  |                        | `Approved`.                           |
+------------------+------------------------+---------------------------------------+
| Voters           | Multi-select           | Team profile IDs participating.       |
+------------------+------------------------+---------------------------------------+
| Consensus Date   | Date                   | Timestamp when approval consensus is  |
|                  |                        | completed.                            |
+------------------+------------------------+---------------------------------------+
```

---

## 3. Consensus Evaluation Loop

The integration service runs a periodic check loop to evaluate and update approval states:
1. **Query Pending**: Retrieve all database rows marked as `Pending`:
   ```python
   pending_releases = database_service.query_approvals(
       filter={"property": "Status", "select": {"equals": "Pending"}}
   )
   ```
2. **Retrieve Reviews**: For each pending release page, query the comments API to fetch the conversation thread history.
3. **Parse Consensus**: Evaluate team member comments:
   * If a comment contains `LGTM` or `Approve`, count it as an affirmative vote.
   * If any comment contains `Block` or `Reject`, update the row status to `Changes Requested` and alert the developer.
4. **Update Status**: When affirmative votes meet the threshold set in the project configuration:
   * Update the status property to `Approved`.
   * Set the `Consensus Date` value.
   * Append a summary comment outlining the approval decision and testing metrics.
