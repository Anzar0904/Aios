# Research Memory Health & Diagnostics Spec
**Sprint 11 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define memory diagnostic checks, database integrity tests, and index repair tasks.
* **Scope**: Governs database checkers, vacuum routines, and data repair scripts.
* **Audience**: Quality Auditors, DBAs, and Systems Engineers.
* **Related Documents**:
  * [workspace/project_discovery/repository_health.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/repository_health.md) - Repository health.
  * [research/memory/forgetting_strategy.md](file:///Users/anzarakhtar/aios/docs/research/memory/forgetting_strategy.md) - Forgetting strategy.

---

## 1. Memory Health Metrics

To maintain database integrity, the **Memory Health** module calculates the following metrics:

```
+------------------------------------+------------------------------------+----------+
| Health Indicator                   | Target Range                       | Priority |
+------------------------------------+------------------------------------+----------+
| 1. SQLite Database Fragmentation    | < 10% page fragmentation           | Medium   |
+------------------------------------+------------------------------------+----------+
| 2. Orphaned Facts Ratio            | 0 orphaned FactNodes in graph      | High     |
+------------------------------------+------------------------------------+----------+
| 3. Broken Relationships Count      | 0 relations with missing target    | High     |
+------------------------------------+------------------------------------+----------+
| 4. Vector-Database Mismatch        | 100% parity (Qdrant vs SQLite IDs) | High     |
+------------------------------------+------------------------------------+----------+
```

---

## 2. Automated Diagnostic Checks

The health monitor runs background diagnostics periodically:
* **Orphan Finder**: Scans `concept_evidences` for rows where the parent `concept_id` is missing.
* **Relation Validator**: Scans `concept_relationships` to identify links pointing to missing target concept IDs.
* **Parity Checker**: Compares active document IDs in SQLite with vector point payloads in Qdrant, flagging any missing records.

---

## 3. Database Repair & Vacuum Sequences

If diagnostics detect errors:
1. **Clean Orphaned Rows**: Runs clean-up queries (`DELETE FROM concept_relationships WHERE target_concept_id NOT IN (SELECT concept_id FROM research_concepts)`).
2. **Re-Index Vectors**: Regenerates missing vector points by re-indexing the corresponding SQLite text.
3. **Database Rebuild**: Executes a database `VACUUM` and re-indexes the FTS5 tables to restore search speed.
