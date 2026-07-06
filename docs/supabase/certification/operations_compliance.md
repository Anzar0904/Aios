# Supabase Intelligence — Operations Compliance
**Sprint 12 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Verify compliance of realtime publications, migration managers, backup verification loops, and disaster recoveries.
* **Scope**: Governs WebSocket checks, backup verification, and failovers.
* **Audience**: Quality Auditors, Systems Architects, and AI developers.
* **Related Documents**:
  * [supabase/operations/README.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/README.md) - Operations Intelligence hub.
  * [supabase/operations/backup_restore.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/backup_restore.md) - Backup and restore.

---

## 1. Compliance Audit Objectives

This audit verifies that the **Realtime, Migrations & Operations** layer monitors replication states, validates migration sequences, performs backup verifications, and schedules failovers.

---

## 2. Operations Verification Matrix

```
+------------------------------------+------------------------------------+----------+
| Operations Requirement             | Verification Check                 | Status   |
+------------------------------------+------------------------------------+----------+
| 1. Realtime Publication Auditing   | Verifies publication tables and    | PASS     |
|                                    | client connections.                |          |
+------------------------------------+------------------------------------+----------+
| 2. Migration Ordering Checks       | Verifies migration sequences,      | PASS     |
|                                    | preventing out-of-order schema runs.|          |
+------------------------------------+------------------------------------+----------+
| 3. Logical pg_dump Backups         | Schedules database snapshots and   | PASS     |
|                                    | verifies WAL archiving.            |          |
+------------------------------------+------------------------------------+----------+
| 4. Disaster Recovery Failovers     | Restores backups to containers     | PASS     |
|                                    | and tests failover promotion.      |          |
+------------------------------------+------------------------------------+----------+
```

---

## 3. Compliance Verification Details

### 3.1 Migrations & Realtime
* Migration verifiers confirm that timestamp checks block out-of-order migration applications.
* Realtime audits verify that table publications and client connection counts are monitored.

### 3.2 Backups & Disaster Recovery
* Backup verifications confirm that database snapshots are restored to test containers weekly, checking schema integrity.
* Failover tests verify that replicas are promoted to primary instances if simulated responsiveness checks fail.
