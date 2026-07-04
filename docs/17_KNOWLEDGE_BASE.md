# 17 — Knowledge Base (System Encyclopedia)
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata
* **Purpose**: Serve as the structured technical encyclopedia and data index for all concepts, modules, and structures of the Personal AI OS.
* **Scope**: Governs all structural dictionary mappings, file definitions, and component references.
* **Audience**: Systems Engineers, Architects, and AI agents querying database properties.
* **Related Documents**:
  * [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) - Constitutional core principles.
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) - Component systems design boundaries.
  * [15_SYSTEM_DESIGN.md](file:///Users/anzarakhtar/aios/docs/15_SYSTEM_DESIGN.md) - Subsystems sequence charts and data flows.
  * [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) - Low-level monorepo files mapping.
* **Future Extensions**: This knowledge database will be updated chronologically as new modules, schemas, or tools are merged into the monorepo.

---

## 1. Core Architecture Index

This section maps the essential runtime components of the operating system:

```
+-----------------------------------------------------------------------------------------------------------------------------------------+
|                                                      SYSTEM COMPONENT INDEX                                                             |
+-------------+----------------------+--------------------+--------------------+--------------------+--------------------+------------+
| Component   | Purpose              | Inputs             | Outputs            | Dependencies       | Related Docs       | Status     |
+-------------+----------------------+--------------------+--------------------+--------------------+--------------------+------------+
| Kernel      | Process boot &       | config.toml path,  | IntentResult       | ServiceRegistry,   | docs/02_           | Current    |
|             | lifecycle loops.     | Intent instances.  | structures.        | EventBusService.   | ARCHITECTURE.md    |            |
+-------------+----------------------+--------------------+--------------------+--------------------+--------------------+------------+
| Event Bus   | Typed synchronous    | Registered Event   | Callback handler   | None.              | docs/02_           | Current    |
|             | messaging.           | instances.         | dispatches.        |                    | ARCHITECTURE.md    |            |
+-------------+----------------------+--------------------+--------------------+--------------------+--------------------+------------+
| Brain       | Multi-step planner & | NL query strings,  | Structured plan    | ModelService,      | docs/12_PRD.md     | Current    |
|             | orchestrator.        | context models.    | steps payloads.    | CommandRegistry.   |                    |            |
+-------------+----------------------+--------------------+--------------------+--------------------+--------------------+------------+
| ToolManager | Executes whitelisted | Command name text, | Subprocess stdout  | EventBusService,   | docs/05_           | Current    |
|             | terminal subprocesses| parameter arrays.  | logs.              | security utility.  | SECURITY.md        |            |
+-------------+----------------------+--------------------+--------------------+--------------------+--------------------+------------+
| Action      | Safe file writes     | Planned mutating   | Reversible backups,| ToolService.       | docs/05_           | Current    |
| Engine      | and rollbacks.       | step metrics.      | diff reports.      |                    | SECURITY.md        |            |
+-------------+----------------------+--------------------+--------------------+--------------------+--------------------+------------+
| Memory      | Persists tiered      | Context Loaded     | Context memory     | EventBusService,   | docs/12_PRD.md     | Current    |
| Service     | records local.       | Event telemetry.   | blocks lists.      | LocalMemoryStorage.|                    |            |
+-------------+----------------------+--------------------+--------------------+--------------------+--------------------+------------+
| Knowledge   | External synchronization| KnowledgeDocument  | KnowledgeSyncResult| PersonalService,   |                    | Current    |
| Hub         | with Notion.         | models.            | details.           | NotionProvider.    |                    |            |
+-------------+----------------------+--------------------+--------------------+--------------------+--------------------+------------+
```

---

## 2. Directory Layout & File Schema Map

```text
/ (root)
├── .aios_conversations/    # Persistent multi-turn dialog logs stored as JSON.
│   └── [session_id].json   # Contains: id, active_agent, messages, and summary block.
├── .aios_tasks/            # Task execution progress and stderr logs.
│   └── [task_id].json      # Contains: objective, status, step details, stdout logs.
├── config/                 # Monorepo environment configurations.
│   └── config.toml         # Pinned models, active providers, and offline variables.
├── skills/                 # Custom domain capability packages.
│   └── [skill_id]/
│       ├── skill.toml      # Declarations: author, version, commands, tools.
│       └── commands.py     # register_commands() bind lambda handlers.
```

---

## 3. Data Structure Encyclopedic Definitions

### 3.1 WorkspaceContext
* **Purpose**: Represent the host workspace environment metrics.
* **Fields**:
  * `project_root` (str): Absolute file path to the project root directory.
  * `project_name` (str): Basename of the project root folder.
  * `git_branch` (Optional[str]): Active branch name (or None if git is missing).
  * `git_root` (Optional[str]): Path to git folder directory (or None).
* **Current Status**: Current.

### 3.2 ConversationMessage
* **Purpose**: Represent a single dialogue turn.
* **Fields**:
  * `role` (str): Role parameter (`"user"`, `"assistant"`).
  * `content` (str): Text payload content.
  * `timestamp` (float): Epoch seconds timestamp.
* **Current Status**: Current.

### 3.3 TaskStep
* **Purpose**: Represent a single execution step in a planned pipeline.
* **Fields**:
  * `step_id` (str): Unique UUID string.
  * `command` (str): CLI command string to execute.
  * `status` (str): State indicator (`"pending"`, `"running"`, `"completed"`, `"failed"`).
  * `stdout_log` (Optional[str]): Captured standard output stream.
  * `optional` (bool): If True, step failure does not abort the task run.
* **Current Status**: Current.

### 3.4 Career OS Data Models & Managers
* **Purpose**: Provide technical definitions and entry points for Career OS modules.
* **Managers & Components**:
  * `CareerProfileManager`: Manages target industry, target roles, and career goals.
  * `JobAnalyzer`: Extracts required skills, tech stack, and ATS keywords from job texts.
  * `ResumeOptimizer`: Reorders and tailors project/experience bullet points.
  * `ATSAnalyzer`: Compares resumes against jobs to predict match scores and recommendations.
  * `CoverLetterGenerator`: Formulates letters tailored to role requirements.
  * `PortfolioAnalyzer`: Ranks GitHub repositories and identifies README gaps.
  * `ApplicationTracker`: Saves tracking logs (company, role, status, dates, notes) in profile knowledge entries.
  * `InterviewCoach`: Generates custom behavioral/technical questions and study guides.
  * `CareerPlanner`: Uses reasoning heuristics to output milestones and estimated impact.
  * `JobMatcher`: Compares and ranks multiple job descriptions.
* **Current Status**: Current.

### 3.5 Knowledge Hub Data Models
* **Purpose**: Evolve external synchronization capability for synchronization with Notion.
* **Data Models & Components**:
  * `KnowledgeHubService`: Interface managing sync processes and registering providers.
  * `KnowledgeProvider`: Abstract interface for Notion, Obsidian, Google Drive, Confluence, etc.
  * `KnowledgeDocument`: Models synchronizable files featuring metadata and references.
  * `KnowledgeMetadata`: Tracks synced Page ID, Database ID, versions, hashes, status, and modifications.
  * `KnowledgeSyncResult`: Captures success/skip/failure sync status logs.
* **Current Status**: Current.

### 3.6 Intent Engine Data Models
* **Purpose**: Determine participating services and dependencies dynamically to achieve objectives.
* **Data Models & Components**:
  * `IntentEngine`: Conductor service managing classification, dependency analysis, planning, and evaluation.
  * `IntentClassifier`: Classifies queries into matched categories (Career, Project, Research, Learning, Automation, Planning, Coding, GitHub, Knowledge, Mission, Daily, Conversation, Hybrid).
  * `IntentAnalyzer`: Maps categories to registered service names and expected outputs.
  * `IntentResolver`: Resolves user objectives and context into structured `IntentPlan` execution graphs.
  * `IntentPlan`: Structured execution graph details (participating services, dependencies, expected outputs, context requirements).
  * `IntentContext`: Tracks contextual variables and retrieved memory snippets.
  * `IntentResult`: Contains process outcomes and resolved plans.
* **Current Status**: Current.

### 3.7 Workspace Intelligence Data Models
* **Purpose**: Provide full repository understanding, architecture observations, dependency relations, and health checks.
* **Data Models & Components**:
  * `WorkspaceIntelligenceService`: Central service managing analysis, memory backups, and Knowledge Hub publishing.
  * `RepositorySummary`: Formulates high-level architecture details, service graphs, design patterns, entrypoints, and observations.
  * `RepositoryHealth`: Formulates repository file statistics, test counts, docs counts, and coverage ratios.
  * `RepositoryAnalyzer`, `ArchitectureAnalyzer`, `DependencyAnalyzer`, `TechnologyAnalyzer`, `DocumentationAnalyzer`: Modular subcomponents.
* **Current Status**: Current.

### 3.8 Code Intelligence Data Models
* **Purpose**: Provide code-level structural understanding, AST-level symbol extraction, inheritance mapping, and call/dependency graph construction.
* **Data Models & Components**:
  * `CodeIntelligenceService`: Unified service managing codebase-level structural analysis, metadata persistence, and Knowledge Hub publishing.
  * `ASTAnalyzer`: Component responsible for parsing source files into syntax symbols.
  * `LanguageASTParser`: Extensible abstract parser interface supporting Python and TypeScript, designed to easily register Go, Rust, Java, C#, and C++ in the future.
  * `SymbolReference`: Models an extracted symbol (class, dataclass, function, method, interface, enum, module, import) featuring decorators, visibility, line ranges, and metadata.
  * `CodeStructureSummary`: Unifies the indexed symbols, module dependency graph, function call graph, inheritance map, and public API lists.
  * `SymbolIndexer`, `DependencyGraphBuilder`, `CallGraphBuilder`: Specialized subcomponents for querying, linking, and analyzing code relationships.
* **Current Status**: Current.

### 3.9 Engineering Intelligence Data Models
* **Purpose**: Provide structured code-change planning, architectural impact analysis, risk assessment, and complexity/effort estimation.
* **Data Models & Components**:
  * `EngineeringIntelligenceService`: Unified service managing engineering analyses, memory persistence, and report publishing.
  * `EngineeringAnalyzer`: Coordinated orchestrator managing change impact, complexity, risk, and implementation planning.
  * `ChangeImpactAnalyzer`: Identifies files and modules affected by a change objective.
  * `ComplexityEstimator`: Estimates effort and classifies task complexity (Low, Medium, High, Very High).
  * `RiskAnalyzer`: Analyzes safety risks (e.g. API breakages, circular dependencies, violations).
  * `ImplementationPlanner`: Generates ordered implementation steps, required services, execution orders, and validation strategies.
  * `AffectedFile`, `AffectedComponent`, `ChangeRecommendation`: Subcomponents representing change targets and suggestions.
  * `EngineeringPlan`: Captures the structured plan steps, dependencies, risks, and validation methods.
  * `EngineeringReport`: Unified final output document containing impact, complexity, risks, and plan.
* **Current Status**: Current.

### 3.10 AI Software Engineer Data Models
* **Purpose**: Converts engineering plans into detailed, dependency-ordered, validation-gated executable development plans without writing code.
* **Data Models & Components**:
  * `SoftwareEngineerService`: Unified service providing development plan creation, storage, and publishing.
  * `ImplementationPlanner`: Orchestrator that aggregates features, tasks, execution orders, testing, and docs into a unified plan.
  * `FeaturePlanner`: Formulates high-level implementation phases and validation steps.
  * `TaskDecomposer`: Breaks down objectives into prioritized tasks with criteria and effort estimates.
  * `ExecutionPlanner`: Calculates safest execution order, task dependencies, and rollback strategies.
  * `FilePlanner`: Identifies required files and setup/migration requirements.
  * `TestingPlanner`: Maps required tests, verification methods, and testing strategy.
  * `DocumentationPlanner`: Maps documentation and architectural guide updates.
  * `ImplementationTask`: Represents a development task (title, description, priority, effort, completion criteria).
  * `DevelopmentPhase`: Packages tasks and validation steps into logical release stages.
  * `ValidationStep`: Describes step name, terminal commands, and expected results.
  * `SoftwareEngineeringPlan`: Unified development plan containing phases, files, tests, documentation, and strategies.
* **Current Status**: Current.

### 3.11 Execution Engine Data Models
* **Purpose**: Manages execution lifetimes, pre-flight task validation, checkpoint recording, and rollback instructions generation for approved software engineering plans.
* **Data Models & Components**:
  * `ExecutionEngine`: Central engine orchestrating execution lifetimes, sessions, checkpoints, validations, and rollbacks.
  * `TaskExecutor`: Runs single tasks, prompting for explicit user permission gates.
  * `ExecutionValidator`: Validates repository status, dependencies, and execution sequences.
  * `ExecutionReporter`: Generates Markdown progress reports for publishing.
  * `ExecutionSession`: Tracks current, completed, failed, and skipped tasks.
  * `ExecutionStep`: Represents individual execution step results.
  * `ExecutionCheckpoint`: Captures modified files, validation status, and completion summary after each task.
  * `RollbackPlan`: Prepares git rollback instructions for reverting changes.
  * `ExecutionResult`: Represents the result payload for execution loop completions.
  * `ExecutionState`: Enum representing Lifecycle states (PENDING, RUNNING, PAUSED, COMPLETED, FAILED, CANCELLED).
* **Current Status**: Current.

### 3.12 AI Workspace Foundation Data Models
* **Purpose**: Creates and manages the isolated temporary filesystem environments (sandboxes) where development tasks run, tracking metadata-only snapshots and session states without modifying the main repository.
* **Data Models & Components**:
  * `AIWorkspaceService`: Central service managing workspace session states, sandboxes, and recovery operations.
  * `WorkspaceValidator`: Validates structural layouts, directory paths, and snapshot list compatibility.
  * `WorkspaceCleaner`: Deletes temporary build logs and purges workspaces recursively.
  * `WorkspaceMetadata`: Tracks sandbox configurations, original repo roots, and lifetime statuses.
  * `WorkspaceSession`: Lifecycle tracker for active workspace engineering sessions.
  * `WorkspaceSnapshot`: Captures file creation, modification, and deletion metadata.
  * `WorkspaceFile`: Models workspace file sizing and classification details.
  * `WorkspaceChange`: Logs a file change event history trace.
  * `WorkspaceRecovery`: Logs recovery metrics when restoring snapshot configurations.
  * `WorkspaceSandbox`: Tracks disk space allocation constraints.
* **Current Status**: Current.

### 3.13 Intelligent File Planner Data Models
* **Purpose**: Coordinates changes by evaluating exactly which files/folders must be created, modified, or deleted for an engineering objective, analyzing direct/indirect imports dependencies and estimating coupling risks.
* **Data Models & Components**:
  * `FilePlanner`: Central coordinating service providing planning results generation, storage, and publishing.
  * `FileImpactAnalyzer`: Identifies affected source files, modification types, target directories, and impact scopes.
  * `FileDependencyResolver`: Resolves import dependencies and transitively computes indirect imports and high-risk modules.
  * `ChangePlanner`: Sequences modifications, maps circular dependency risks, and establishes validation/testing checkpoints.
  * `ModificationType`: Enum mapping file modification actions (CREATE, MODIFY, DELETE, RENAME, MOVE, TEST, DOCUMENT).
  * `AffectedFile`: Models a single affected file featuring modification types, risk levels, and direct dependency lists.
  * `AffectedDirectory`: Models an affected directory mapping count of modified files.
  * `ImplementationScope`: Packs lists of affected files and directories within specific sandbox bounds.
  * `PlanningResult`: Unified outcome document capturing sequences, risk levels, and quality checkpoints.
* **Current Status**: Current.

### 3.14 Patch Generation Engine Data Models
* **Purpose**: Generates standard unified diff patches comparing isolated sandbox workspaces against origin repository roots, checking checksum compatibility, detecting file-level merge conflicts, and formatting review packages for developers.
* **Data Models & Components**:
  * `PatchGenerationService`: Central coordinating service providing review packages generation, memory summaries persistence, and report publishing.
  * `DiffGenerator`: Generates standard unified diff format strings comparing string line differences.
  * `PatchGenerator`: Creates patch bundles tracking lines modifications (added, removed) across files.
  * `PatchValidator`: Verifies header configurations and computes SHA-256 patch checksums validation.
  * `ConflictDetector`: Identifies merge collisions and planning inconsistencies.
  * `PatchSerializer`: Converts patch bundles to and from JSON format string representation.
  * `PatchMetadata`: Details patch size, checksum verification hash, timestamp, and author attributes.
  * `PatchStatistics`: Summarizes lines added/removed, files modified, and chunks count metrics.
  * `PatchPreview`: Represents human-readable previews of file changes.
  * `PatchBundle`: Packs mapping of file paths to unified diff contents.
  * `ReviewPackage`: Consolidates previews, statistics, conflict logs, and validation status.
* **Current Status**: Current.

### 3.15 AI Code Generation Engine Data Models
* **Purpose**: Manages code generation inside isolated workspace sandboxes using structured prompts and model routing options without modifying host project repositories, running syntactic/styling validations before patch generation.
* **Data Models & Components**:
  * `CodeGenerationService`: Primary coordinating service providing session state tracking, code generation execution, and reports synchronization.
  * `CodePlanner`: Evaluates development plans to schedule sequential file edits.
  * `ContextAssembler`: Formulates minimal codebase context including imports and interface indexes to avoid bloated prompt limits.
  * `PromptBuilder`: Structures LLM instructions mapping task metadata and policy modifiers.
  * `FileGenerator`: Handles sandbox file creation.
  * `FileEditor`: Handles sandbox file editing.
  * `SyntaxValidator`: Validates python syntax using compilers.
  * `StyleValidator`: Enforces formatting and layout constraints.
  * `ImportValidator`: Verifies target modules and package imports existence.
  * `GenerationValidator`: Aggregates syntactic/style/import checkers outcomes.
  * `GenerationPolicy`: Enum containing generation constraint modes (CONSERVATIVE, BALANCED, AGGRESSIVE).
  * `GeneratedArtifact`: Packages path details and SHA-256 hash checksums.
  * `GenerationReport`: Tracks artifacts list, verification logs, and confidence scoring.
  * `GenerationSession`: Lifecycle tracker for active workspace sessions.
* **Current Status**: Current.

### 3.16 AI Test Engineer Phase 1 Milestone 1: Test Planning Foundation
* **Purpose**: Performs test planning before tests are generated or executed. Analyzes objectives, strategies, scopes, and target files, ordering execution suites based on coupling values and dependencies risks.
* **Data Models & Components**:
  * `AITestEngineerService`: Central service managing test plans generation, memory caching, and report syncing.
  * `TestPlanner`: Core planning logic mapping goals and file impact scopes to test strategies.
  * `TestCategory`: Enum mapping test disciplines (UNIT, INTEGRATION, REGRESSION, API, DATABASE, SECURITY, PERFORMANCE, END_TO_END, SMOKE, SANITY, STATIC_ANALYSIS, STYLE_VALIDATION).
  * `TestPriority`: Enum ranking sequence priority weights (LOW, MEDIUM, HIGH, CRITICAL).
  * `TestStrategy`: Enum setting validation levels (MINIMAL, STANDARD, STRICT, MISSION_CRITICAL).
  * `TestRequirement`: Requirements criteria specifying validation targets.
  * `TestTarget`: Specific target files or classes/methods symbols.
  * `TestScope`: Outlines test targets, exclusions, and target coverage percentages.
  * `TestSuite`: Packaged test run definitions grouping targets.
  * `TestPlan`: Consolidated test execution plan specification.
  * `TestPlanningResult`: Execution sequence result mapping prioritized suites and checks.
* **Current Status**: Current.

### 3.17 Change Impact Analysis Data Models
* **Purpose**: Evaluates propagation paths for files edits, identifying directly/indirectly affected components, mapping testing prioritizations, identifying regression candidates, and calculating target coverages.
* **Data Models & Components**:
  * `ChangeImpactAnalyzer`: Central coordinating service managing change impact analysis, memory summaries, and reports publishing.
  * `ImpactGraph`: Propagation graph containing nodes and edges.
  * `ImpactNode`: Node element mapping file type and modified status.
  * `ImpactEdge`: Directed relation mapping import, call, or inheritance references.
  * `AffectedComponent`: Component directly or indirectly impacted by changes.
  * `AffectedTestSuite`: Priority testing target suite details.
  * `RegressionCandidate`: Module prone to indirect regressions due to inbound import dependencies.
  * `RiskAssessment`: Consolidates overall risk, api break risk, shared lib risk, dep chain risk, config risk, and data model risk.
  * `CoverageTarget`: Recommended statement and branch coverage targets.
  * `ImpactAnalysisResult`: Assembled result combining graphs, candidates list, and coverage goals.
* **Current Status**: Current.

### 3.18 Intelligent Test Generation Data Models
* **Purpose**: Discovers repository test patterns, formats boilerplate setups, parses execution test steps, validates python syntax compilability, and outputs test artifacts strictly within the sandbox workspace.
* **Data Models & Components**:
  * `TestGenerationService`: Coordinates test planning, workspace generation pipeline, memory reports caching, and Notion report publishing.
  * `TestGenerator`: Assembles test snippets into full test suites files.
  * `TestTemplateEngine`: Formats structural Python test skeletons.
  * `TestPatternAnalyzer`: Discovers layout, mock, fixture, and naming conventions.
  * `TestCaseBuilder`: Maps step-by-step target execution cases.
  * `AssertionGenerator`: Formulates assertions assertions checks.
  * `FixtureGenerator`: Creates Pytest fixture setup functions.
  * `MockGenerator`: Generates MagicMock setups.
  * `EdgeCaseGenerator`: Identifies exception boundaries test blocks.
  * `RegressionTestGenerator`: Generates regression checks.
  * `GeneratedTestArtifact`: Details file paths, compiled python code, and SHA-256 hashes.
  * `TestGenerationReport`: Aggregates warnings count, strategies, confidence, and generated artifacts lists.
* **Current Status**: Current.

### 3.19 Intelligent Test Execution Engine Data Models
* **Purpose**: Coordinates process execution of python tests inside the workspace sandbox, parsing summaries of results, capturing timing logs, and sync reporting metrics.
* **Data Models & Components**:
  * `TestExecutionService`: Coordinating service managing test executions runs, caching summaries in Memory, and publishing reports.
  * `TestExecutor`: Primary coordinator initiating runner commands.
  * `TestRunner`: Standard execution orchestrator.
  * `ExecutionSession`: Lifecycle state tracking session executions.
  * `ExecutionTarget`: Targeted test file, class, or method.
  * `ExecutionResult`: Single run outcome detailing error listings, success state, and duration metrics.
  * `ExecutionLog`: Single line telemetry logs captured during test runs.
  * `ExecutionMetrics`: Consolidates totals (passed, failed, skipped, duration).
  * `ExecutionSummary`: Aggregates summary outputs and execution list states.
  * `TestFrameworkAdapter`: Interface for pluggable framework execution (Jest, JUnit, Pytest).
  * `PytestAdapter`: Adapter wrapping subprocess runs.
* **Current Status**: Current.

### 3.20 Coverage & Regression Intelligence Data Models
* **Purpose**: Compares test execution outcomes against target coverage policies, flags code validation gaps, and calculates regression probability parameters based on import dependency density.
* **Data Models & Components**:
  * `AITestCoverageService`: Coordinating service triggering validation checks, caching report summaries in Memory, and publishing reports.
  * `CoverageAnalyzer`: Calculates simulated statement and branch coverages.
  * `RegressionAnalyzer`: Checks dependency charts to compute regression risks levels.
  * `CoverageMetrics`: Struct encapsulating statement, branch, class, and interface coverage totals.
  * `CoveragePolicy`: Threshold settings specifying minimum statement/branch coverage goals.
  * `CoverageSummary`: Overall calculated coverage metrics summary.
  * `CoverageReport`: Formulated coverage metrics evaluation record.
  * `RegressionRisk`: Risk ratings (Low, Medium, High, Critical) and probability indices.
  * `ValidationGap`: Actionable descriptions indicating missing suites or low test coverages.
* **Current Status**: Current.

### 3.21 Intelligent Failure Analysis Data Models
* **Purpose**: Analyzes test execution traceback outputs, clusters logs by exception class patterns, executes root cause correlations using call graphs, and recommends actionable adjustments.
* **Data Models & Components**:
  * `FailureAnalysisService`: Coordinating service executing analyses, caching reports in Memory, and publishing reports.
  * `FailureAnalyzer`: Classifies failure patterns and groups trace signatures.
  * `RootCauseAnalyzer`: Isolates origins of failures in codebase graphs.
  * `FailureSignature`: Traced log details for single exceptions.
  * `FailurePattern`: Matches error families (e.g. assertion, import, runtime).
  * `FailureCluster`: Collections of signatures sharing similar patterns.
  * `FailureRecommendation`: Direct tips outlining resolution steps.
  * `FailureSeverity`: Severity metrics classifications (LOW, MEDIUM, HIGH, CRITICAL).
  * `FailureConfidence`: Confidence metrics levels (LOW, MEDIUM, HIGH, CERTAIN).
  * `FailureAnalysisReport`: Diagnostic report containing clusters lists, recommendations, and ratings.
* **Current Status**: Current.

### 3.22 Unified Validation Report Data Models
* **Purpose**: Compiles test execution metrics, coverage calculations, and diagnostic failure records into a single authoritative validation artifact used across other AI OS components.
* **Data Models & Components**:
  * `ValidationService`: Unified validation service compiling gates and decisions.
  * `ValidationStatus`: Evaluated gate results (PASS, WARNING, FAIL).
  * `ValidationDecision`: High-level quality release decision (APPROVED, REJECTED, MANUAL_REVIEW).
  * `ValidationFinding`: Flagged discovery detailing file errors.
  * `ValidationRecommendation`: Recommended adjustments to address failing gates.
  * `ValidationEvidence`: Telemetry snippets validating gates.
  * `ValidationGate`: Quality gates checking execution counts, coverage, and severity.
  * `ValidationMetrics`: Consolidated summary metrics (passed gates count, total tests, coverages).
  * `ValidationScore`: Raw score and confidence deduction penalty records.
  * `ValidationSummary`: Aggregated report summary tracking release decisions.
  * `ValidationReport`: Assembled unified report package.
* **Current Status**: Current.

---




## 4. Planned & Future Subsystems

### 4.1 Web UI Renderer
* **Purpose**: Renders visual dashboards displaying task steps and memory trees.
* **Status**: Planned (Phase 3).
* **Dependencies**: Node.js, Next.js, React, TypeScript.
* **Related Documents**: [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md).

### 4.2 Local Daemon (`aiosd`)
* **Purpose**: Run background monitoring services and unix socket listeners.
* **Status**: Planned (Phase 3).
* **Dependencies**: Python standard daemon libraries, system watchdog.
* **Related Documents**: [15_SYSTEM_DESIGN.md](file:///Users/anzarakhtar/aios/docs/15_SYSTEM_DESIGN.md).

### 4.3 Project Intelligence Skill
* **Purpose**: Scopes project milestones, tracks velocity, and estimates timelines.
* **Status**: Future (Phase 4).
* **Dependencies**: Git history tracker tool, memory service.
* **Related Documents**: [12_PRD.md](file:///Users/anzarakhtar/aios/docs/12_PRD.md).

---

## 5. Technical Glossary Reference
* **OmniRoute**: Dynamic routing selector that evaluates token size, context limits, and offline parameters.
* **Composition Root**: Centralized bootstrap wiring (`bootstrap.py`) where concrete classes are injected into interfaces.
* **Protected Core**: High-risk system directories isolated from dynamic plugin alterations.
* **History Compression**: Automated dialog summarization triggered when conversation turns exceed 10.
* **Containment Check**: Path traversal validation ensuring canonical paths remain inside active workspace roots.
* **Reverse Rollback**: Restoring cached file contents in reverse order when step executions fail.
* **Closed-World Commands**: Restricting executions to whitelisted command keywords registered in the `CommandRegistry`.
* **SemVer**: Semantic Versioning rules (`MAJOR.MINOR.PATCH`) applied to releases.
