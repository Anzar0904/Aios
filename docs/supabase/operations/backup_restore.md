# Backup & Restoration Spec
**Sprint 12 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define database backup parameters, pg_dump variables, and verification scripts.
* **Scope**: Governs backup configs, storage copies, and verification tasks.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [supabase/platform/bucket_analysis.md](file:///Users/anzarakhtar/aios/docs/supabase/platform/bucket_analysis.md) - Storage buckets.
  * [supabase/operations/realtime_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/operations/realtime_intelligence.md) - State abstraction.

---

## 1. Backup Execution Pipeline

The backup engine manages database snapshots to prevent data loss:
* **pg_dump Backups**: Schedules daily logical backups (`pg_dump`) to capture table structures and data.
* **WAL Archiving**: Verifies that Write-Ahead Logging (WAL) archiving is active, enabling Point-in-Time Recovery (PITR).
* **Backup Storage**: Uploads compressed backup files (`.sql.gz`) to secure, isolated storage buckets.

---

## 2. Restoration Verification Tests

To verify backup integrity:
1. **Restore Snapshot**: Automatically restores backup snapshots to a local PostgreSQL container once per week.
2. **Schema Verification**: Runs checks to verify that tables, columns, and indexes match desired schemas.
3. **Data Parity Checks**: Performs row count checks to verify data consistency.
4. **Log Results**: Writes test results to `docs/supabase/scratch/backup_tests.log`.
