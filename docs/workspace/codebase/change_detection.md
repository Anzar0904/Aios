# Change Detection & Index Invalidation Spec
**Sprint 10 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define file change delta verification, incremental compiles, and multi-database cache invalidation.
* **Scope**: Governs sha256 checksums, AST incremental checks, and index updates.
* **Audience**: DBAs, Backend Developers, and System Architects.
* **Related Documents**:
  * [workspace/codebase/filesystem_intelligence.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/filesystem_intelligence.md) - Filesystem events.
  * [workspace/codebase/symbol_index.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/symbol_index.md) - Database symbol indexes.

---

## 1. Incremental Hash Verifications

To avoid wasting CPU cycles re-compiling large unchanged codebases, the change detection engine uses a two-stage delta check:
1. **Timestamp Check**: filesystem watcher matches file paths and modification timestamps.
2. **SHA-256 Checksum**: If the timestamp has changed, the engine calculates a SHA-256 checksum on the file content and compares it against the `workspace_metadata` table. If the checksum matches the database record, the file contents are unchanged (e.g. metadata-only edits), and AST parsing is skipped.

---

## 2. Line-Range Delta Calculations

When a file modification is verified:
* **Diff Parsing**: The engine runs a local diff parser (comparing SQLite cached code with active file lines).
* **Target Line Identification**: Isolates the exact line ranges that changed (e.g. Lines 45–56 modified).
* **Symbol Matching**: Cross-references these line offsets with the `codebase_symbols` table coordinates:
  * If the changed lines fall inside the boundaries of `class LocalKnowledgeHub -> def sync_document`, only that specific symbol is flagged for AST validation and re-embedding.
  * Surrounding unchanged symbols are preserved, skipping re-embedding and conserving local CPU cycles.

---

## 3. Cache & Vector Invalidation Sequence

When a symbol modification is verified, the invalidation engine runs the following pipeline:

```
[Verify Symbol Change]
          |
          +---> 1. SQLite: Update codebase_symbols table metadata & timestamps.
          |
          +---> 2. Redis: Issue DEL keys matching the symbol namespace.
          |
          +---> 3. Qdrant: Delete old point ID matching the symbol coordinates.
          |
          +---> 4. Qdrant: Upload fresh 384d vector embedding point.
          |
          v
[Clear Task Plan Cache] ===> Purge agent task caches to trigger re-planning
```
