# Supabase Intelligence — Database Compliance
**Sprint 12 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Verify compliance of database metadata queries, relation mapping checkers, index evaluators, and EXPLAIN query plan parsers.
* **Scope**: Governs catalog queries, relationship models, and performance logs.
* **Audience**: Quality Auditors, Systems Architects, and AI developers.
* **Related Documents**:
  * [supabase/database/README.md](file:///Users/anzarakhtar/aios/docs/supabase/database/README.md) - Database Intelligence hub.
  * [supabase/database/schema_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/database/schema_intelligence.md) - Schema discovery.

---

## 1. Compliance Audit Objectives

This audit verifies that the **Database & Schema Intelligence** layer queries remote database catalogs, extracts relationship parameters, audits index configurations, and evaluates query performance.

---

## 2. Database Verification Matrix

```
+------------------------------------+------------------------------------+----------+
| Database Requirement               | Verification Check                 | Status   |
+------------------------------------+------------------------------------+----------+
| 1. Metadata Schema Scanner         | Queries namespaces, views, and DDL | PASS     |
|                                    | catalog details correctly.         |          |
+------------------------------------+------------------------------------+----------+
| 2. Relationship cascading          | Maps key connections and checks    | PASS     |
|                                    | for cyclic dependencies.           |          |
+------------------------------------+------------------------------------+----------+
| 3. Index Usage Evaluator           | Checks index statistics and flags  | PASS     |
|                                    | unused index configurations.       |          |
+------------------------------------+------------------------------------+----------+
| 4. EXPLAIN JSON Plan Audits        | Analyzes queries costs and         | PASS     |
|                                    | detects sequential scans.          |          |
+------------------------------------+------------------------------------+----------+
```

---

## 3. Compliance Verification Details

### 3.1 Metadata & Relationship Mapping
* Schema discovery tests verify that schemas namespaces, table definitions, and views are retrieved from PostgreSQL catalogs.
* Relationship mapping checks verify that foreign key cascading rules are extracted and cyclic dependencies are detected.

### 3.2 Indexes & Query Performance
* Index audit logs verify that pg_stat statistics are analyzed, flagging unused indexes for cleanup.
* Query tests confirm that explain plans are evaluated, checking query costs and flagging sequential scans.
