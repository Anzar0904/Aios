# Engineering Memory Migration Report (Sprint 4 Milestone 3)

## 1. Current Runtime Memory Locations

Operational metadata across engineering subsystems is currently held in volatile runtime variables:

### 1.1 Approval Engine
- `LocalApprovalEngineService._sessions`: Holds active `ApprovalSession` mapping session IDs to requests, evaluation packages, and outcomes.
- `LocalApprovalEngineService._histories`: Holds `ApprovalHistory` objects tracking summaries for each workspace.
- `LocalApprovalHistoryService._entries`: Caches state transitions (`ApprovalHistoryEntry`) per session.
- `LocalApprovalHistoryService._records`: Caches finished `ApprovalDecisionRecord` entries.

### 1.2 Documentation Intelligence
- `DocumentationRegistry._artifacts`: Holds in-memory `DocumentArtifact` details, including file checksums, locations, and authors.
- `DocumentationRegistry._templates`: Caches assembled structure layout templates (`DocumentTemplate`).

### 1.3 AI Software Engineer & AI Test Engineer
- Currently rely on transient in-memory objects generated on-demand (e.g. `SoftwareEngineeringPlan`, `TestPlanningResult`). There is no persistent layer preserving software implementation tasks, planning decision graphs, test sessions, or historical test outcomes.

---

## 2. Existing Repositories
The following repositories are currently registered in `PersistenceRegistry`:
- `workspaces` -> `WorkspaceRepositoryImpl`
- `workspace_sessions` -> `WorkspaceSessionRepositoryImpl`
- `projects` -> `ProjectRepositoryImpl`
- `engineering_profiles` -> `EngineeringProfileRepositoryImpl`
- `configuration_profiles` -> `ConfigurationRepositoryImpl`

---

## 3. Migration Plan & New Repository Structures

We will implement new repository classes returning `PersistenceResult` wrappers:

1. **`EngineeringTaskRepository`**: Persists tasks generated during software engineering loops into the `engineering_tasks` table.
2. **`PlanningRepository`**: Stores development execution plans, version targets, and decision graphs in the `planning_sessions` table.
3. **`ApprovalRepository`**: Stores quality gate approvals and metadata in the `approval_sessions` table.
4. **`ReviewRepository`**: Handles review entries and state transitions in the `review_sessions` table.
5. **`DocumentationMetadataRepository`**: Tracks published documents and checksums in the `documentation_metadata` table.
6. **`TestSessionRepository`**: Caches overall test session outcomes in the `test_sessions` table.
7. **`TestResultRepository`**: Records specific test suite results and execution coverages in the `test_results` table.

A central coordinating `EngineeringMemoryService` will wrap these repositories and expose `Record()`, `Update()`, `Archive()`, `Restore()`, `History()`, `Statistics()`, and `SearchMetadata()` APIs.
All persistence storage internals in the corresponding engines will be refactored to consume these repositories.
