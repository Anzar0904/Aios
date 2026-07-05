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
| Source      | Unified Git and      | Repository name,   | Local status,      | LocalGitExecutor,  | docs/source_control| Current    |
| Control     | GitHub integrations. | action commands.   | report documents.  | GitHubProvider.    | /                  |            |
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

### 3.23 Engineering Profiles Foundation Data Models
* **Purpose**: Provides a single source of strongly-typed configuration settings managing coding style parameters, testing targets, execution configurations, release methods, and automation intervals.
* **Data Models & Components**:
  * `EngineeringProfileService`: Coordinating service managing engineering profile registries.
  * `EngineeringProfile`: Consolidated configuration profile mapping nested categories.
  * `ProjectProfile`: General project identity details (name, version, descriptors).
  * `CodingProfile`: Language style limits and lint mappings.
  * `TestingProfile`: Execution frameworks preferences and coverage policies.
  * `ExecutionProfile`: Sandbox constraints and execution timeout limits.
  * `DocumentationProfile`: Documentation templates formats.
  * `GitHubProfile`: Repository coordinates, branches, and organization tags.
  * `ReleaseProfile`: Automated versioning policies and release settings.
  * `AutomationProfile`: Cron trigger intervals and retry counts.
  * `WorkspaceProfile`: Active workspace locations and file exclude definitions.
  * `ProfileSerializer`: Serializes configurations to/from dictionaries.
  * `ProfileLoader`: Loads profile configs from files.
  * `ProfileManager`: Deep merges and validates profiles.
  * `ProfileRegistry`: In-memory thread-safe profile store registry.
* **Current Status**: Current.

### 3.24 Documentation Intelligence Foundation Data Models
* **Purpose**: Manages global template structures and layout plans for generating code specifications, API registries, and release validation documentation.
* **Data Models & Components**:
  * `DocumentationService`: Coordinating service managing documentation planning sessions and indexes.
  * `DocumentationPlanner`: Assembles lists of recommended document templates.
  * `DocumentationRegistry`: In-memory index caching registered templates and documents.
  * `DocumentationProfileAdapter`: Adapts general style rules to document-specific layouts.
  * `DocumentTemplate`: Layout settings containing target headings lists.
  * `DocumentArtifact`: Generated/registered documentation file record.
  * `DocumentMetadata`: Tag fields detailing document category and source.
  * `DocumentCategory`: Enum for document types (README, API_DOC, RELEASE_NOTES).
  * `DocumentSource`: Enum denoting originating system component sources.
  * `DocumentationWorkspace`: Context directory targets configurations.
  * `DocumentationSession`: Session tracking state metrics.
  * `DocumentationResult`: Summary of generated/registered documents lists.
* **Current Status**: Current.

### 3.25 README Intelligence Data Models
* **Purpose**: Compares repository structures against documentation guidelines, formats planned README sections lists, validates internal links structures, and updates README markdown content.
* **Data Models & Components**:
  * `READMEIntelligenceService`: Coordinating service managing README analysis and generation sessions.
  * `READMEAnalyzer`: Compares existing headers to highlight missing/outdated standard sections.
  * `READMEPlanner`: Sequences layout blocks according to formatting guidelines.
  * `READMEValidator`: Flag formatting inconsistencies or duplicate headings.
  * `READMEGenerator`: Concat planned sections list into markdown content.
  * `READMEUpdater`: Selectively merges updates to existing README files.
  * `READMESection`: Individual document section model (heading, content, priority).
  * `READMETemplate`: Section ordering and style constraint configurations.
  * `READMEArtifact`: Constructed README markdown file object.
  * `READMESummary`: Registry metadata tracker (status, section count).
  * `READMEReport`: Analysis outcome report outlining recommendations.
* **Current Status**: Current.

### 3.26 API Documentation Data Models
* **Purpose**: Discovers project REST/GraphQL endpoint structures via AST parses, plans missing reference docs, validates schemas parameters formatting, and saves API references markdown files.
* **Data Models & Components**:
  * `APIDocumentationService`: Coordinating service managing API specs generation and registries.
  * `APIAnalyzer`: Scans AST code layouts to check missing parameters and routes.
  * `APIDocumentationPlanner`: Configures endpoints mock schemas matching formatting conventions.
  * `APIDocumentValidator`: Flags OpenAPI format structural mismatches or duplicate endpoints.
  * `APIRegistry`: Thread-safe registry cataloging registered endpoints.
  * `APIEndpoint`: Details REST coordinates (path, method, deprecated state).
  * `APISchema`: Defines request/response structure fields mappings.
  * `APIParameter`: Details path or query parameters constraints.
  * `APIResponse`: Details status codes specs, request models, and examples.
  * `APIExample`: Mock request/response payload examples.
  * `APIDocumentArtifact`: Generated API specs markdown file.
  * `APIReport`: Discrepancies report tracking undocumented endpoints list.
* **Current Status**: Current.

### 3.27 Architecture Documentation Data Models
* **Purpose**: Analyses codebase decoupling layer bounds, checks imports patterns to prevent circular dependencies, and formats Mermaid flowcharts depicting components.
* **Data Models & Components**:
  * `ArchitectureDocumentationService`: Coordinating service generating Mermaid flowchart layouts and architecture reports.
  * `ArchitectureAnalyzer`: Inspects codebase dependencies list to find layer violations or cycles.
  * `ArchitectureDocumentPlanner`: Selects subsystems components requiring structural descriptions.
  * `ArchitectureValidator`: Checks that Mermaid diagram connections references match active components.
  * `ArchitectureRegistry`: Catalogues resolved subsystems components, relationships, and decisions.
  * `ArchitectureComponent`: Single structural node type block details.
  * `ArchitectureLayer`: Structural layering divisions tracking member components.
  * `ArchitectureRelationship`: Coupling links connecting two systems blocks.
  * `ArchitectureDiagram`: Formatted diagram output data (Mermaid code blocks).
  * `ArchitectureDecision`: Decision records reference mapping status context.
  * `ArchitectureSummary`: Summary counts metrics detailing discovered elements.
  * `ArchitectureReport`: Health reports identifying circular imports.
* **Current Status**: Current.

### 3.28 Engineering Documentation Data Models
* **Purpose**: Generates Architecture Decision Records (ADRs), formats implementation reports and technical timelines, and validates document completeness checks.
* **Data Models & Components**:
  * `EngineeringDocumentationService`: Coordinating service managing ADR creations and implementations reporting.
  * `EngineeringDocumentPlanner`: Selects technical decisions or implementation phases requiring documenting.
  * `ADRGenerator`: Formats context, consequences, and trade-offs into markdown files.
  * `EngineeringReportGenerator`: Combines timelines, validation scores, and risk assessments into summaries.
  * `EngineeringDocumentValidator`: Flags empty ADR context sections or duplicate identifiers.
  * `DecisionRecord`: ADR record detailing context, choices, and consequences.
  * `ImplementationSummary`: List of added features and modified files.
  * `EngineeringTimeline`: Technical step timeline detailing phase durations.
  * `ChangeSummary`: Metrics tracking lines addition and deletion changes counts.
  * `ValidationSummary`: Summarizes test execution runs and coverage stats.
  * `RiskSummary`: Tag tags designating risk levels and impacted boundaries.
  * `EngineeringDocumentArtifact`: Formatted output artifact (ADR or report markdown).
  * `EngineeringDocumentationReport`: Executive summary report tracking recommendations.
* **Current Status**: Current.

### 3.29 Release Documentation Intelligence Data Models
* **Purpose**: Compiles, plans, validates, and generates release notes, changelogs, migration guides, and upgrade guides for version releases inside isolated workspace environments.
* **Data Models & Components**:
  * `ReleaseDocumentationService`: Central coordinating service implementing notes, changelogs, migration, and upgrade guides creation pipelines.
  * `ReleaseNotesGenerator`: Formats ReleaseSummary details and facets into standard Markdown Release Notes.
  * `ChangelogGenerator`: Parses lists of commits into Keep a Changelog standard format.
  * `MigrationGuideGenerator`: Formats breaking changes instructions into step-by-step migration checklists.
  * `UpgradeGuideGenerator`: Compiles deployment steps checklists into standard upgrade guides.
  * `ReleaseSummary`: Consolidated metrics summary of features, fixes, and breaking changes.
  * `ReleaseArtifact`: Output artifact containing the generated documentation content.
  * `ReleaseValidator`: Validates semantic versioning consistency, broken references, duplicate release entries, and markdown structures.
  * `ReleaseDocumentPlanner`: Compiles release scope metrics and plans the required documentation based on workspace metadata.
  * `ReleaseDocumentationReport`: Validation check report output detailing validation errors or warnings.
* **Current Status**: Current.

### 3.30 Approval Engine Data Models
* **Purpose**: Serves as the central decision layer evaluating aggregated engineering, validation, and documentation evidence to produce structured approval decisions without modifying files or running commands.
* **Data Models & Components**:
  * `ApprovalEngineService`: Conductor service managing approval requests, evaluations, history records, and Notion reporting.
  * `ApprovalManager`: Orchestrates session instantiation, evidence compilation, and policy evaluation.
  * `ApprovalSession`: Lifecycle tracker for active evaluation processes.
  * `ApprovalRequest`: Intake request containing target versions, policy selections, and collected evidence.
  * `ApprovalDecision`: Result status carrying reasoning parameters and reviewer notes.
  * `ApprovalStatus`: Enum mapping gate states (`PENDING`, `APPROVED`, `APPROVED_WITH_CONDITIONS`, `PARTIALLY_APPROVED`, `MANUAL_REVIEW`, `CHANGES_REQUESTED`, `REJECTED`).
  * `ApprovalPolicy`: Configurable parameters grouping custom evaluation rules.
  * `ApprovalRule`: Extensible gating check class evaluating coverage ratios, validation scores, risk thresholds, and documentation states.
  * `ApprovalEvidence`: Input telemetries aggregated from validation, testing, readme, or architectural analyzers.
  * `ApprovalSummary`: Memory-only metadata record saved to the Project Memory store.
  * `ApprovalHistory`: Collection list of all previous validation runs per workspace.
  * `ApprovalReport`: Report payload structured for external Notion databases syncs.
  * `ApprovalValidator`: Package checker verifying structural completeness, duplicate requests, and decision consistency.
  * `AutomationIntelligenceService`, `GitHubAutomationService`, `ExecutionPlanService`, `ApplyEngineService`, `ReleaseIntelligenceService`: Exposed future subsystem integration points.
* **Current Status**: Current.

### 3.31 Review Engine Data Models
* **Purpose**: Performs code and engineering review analyses on Approval Packages to produce structured, categorized, and severity-ranked findings without modifying files.
* **Data Models & Components**:
  * `ReviewEngine`: Coordinating service managing quality reviews, history logs, and Notion reporting.
  * `ReviewSession`: Lifecycle tracker for active quality review runs.
  * `ReviewFinding`: Detailed code review diagnostic issue containing category, severity, confidence, related components/files, and recommendations.
  * `ReviewCategory`: Enum mapping review domains (`ARCHITECTURE`, `MAINTAINABILITY`, `PERFORMANCE`, `SECURITY`, `RELIABILITY`, `TESTING`, `DOCUMENTATION`, `COMPLEXITY`, `DEPENDENCY_RISK`, `BACKWARD_COMPATIBILITY`, `OPERATIONAL_READINESS`, `FUTURE_SCALABILITY`).
  * `ReviewSeverity`: Enum mapping finding impacts (`INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
  * `ReviewRecommendation`: Remediation recommendations carrying actionable step checklists.
  * `ReviewSummary`: Consolidated executive metrics summarizing overall review findings, health parameters, strengths, weaknesses, blocking lists, and confidence rating.
  * `ReviewEvidence`: Telemetry records backing individual findings.
  * `ReviewAnalyzer`: Evaluation engine auditing approval package properties.
  * `ReviewValidator`: Structural check class verifying duplicate findings, completeness, severity consistency, and reviewer confidences.
  * `ReviewReport`: Review payload packaged for Knowledge Hub syncs.
* **Current Status**: Current.

### 3.32 Collaboration Engine Data Models
* **Purpose**: Manages structured reviewer discussions, file/artifact comments, threads resolving/reopening workflows, immutable timeline logs, and reviewer votes for approval package gates.
* **Data Models & Components**:
  * `ReviewCollaborationService`: Main coordinator managing comments, threads, timeline tracing, voting, and Notion sync.
  * `Reviewer`: Profile data representing human code reviewers.
  * `ReviewerRole`: Enum mapping configurable reviewer roles (`OWNER`, `MAINTAINER`, `REVIEWER`, `ARCHITECT`, `SECURITY`, `QA`, `OBSERVER`).
  * `ReviewComment`: Individual reviewer comment containing replies, statuses, and linked engineering artifacts.
  * `ReviewThread`: Discussion thread nesting comment replies.
  * `ReviewVote`: Reviewer gate vote decision (`approve`, `approve_with_conditions`, `request_changes`, `reject`).
  * `ReviewAction`: Enum mapping timeline logs action categories (`CREATE`, `COMMENT`, `REPLY`, `RESOLVE`, `REOPEN`, `VOTE`, `STATUS_CHANGE`).
  * `ReviewAuditLog`: Struct representing append-only, immutable logs entries.
  * `ReviewTimeline`: Immutable chronological log of review session events.
  * `ReviewCheckpoint`: Summary snapshot tracking active votes and thread statuses.
  * `ReviewResolution`: Final gate resolution summary details.
  * `ReviewFeedback`: Reviewer satisfaction feedback rating notes.
  * `ReviewCollaborationReport`: Report container encapsulating threads, timelines, and audit logs.
* **Current Status**: Current.

### 3.33 History Engine Data Models
* **Purpose**: Manages decision history logs, state machine transitions, statistical aggregations, trend slope tracking, and historical recommendations audits.
* **Data Models & Components**:
  * `ApprovalHistoryService`: Core coordinator managing transitions, recording decisions, running historical audits, and notion reporting.
  * `ApprovalHistoryManager`: Internal coordinator managing state machines transitions and decision queries.
  * `ApprovalHistoryEntry`: Immutable log containing state transitions for an individual session.
  * `ApprovalDecisionRecord`: Summary record containing validation scores, coverage values, and final states.
  * `ApprovalState`: Enum mapping state machine states (`DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `CHANGES_REQUESTED`, `UPDATED`, `APPROVED`, `APPROVED_WITH_CONDITIONS`, `PARTIALLY_APPROVED`, `REJECTED`, `EXPIRED`, `ARCHIVED`).
  * `ApprovalStateTransition`: Immutable transition trace recording source state, destination state, actor, and rationale.
  * `ApprovalStatistics`: Statistical summaries detailing averages (validation, coverage, confidence) and count ratios.
  * `ApprovalTrend`: Chronological metric trend lines (`improving`, `declining`, `stable`).
  * `ApprovalPattern`: Identified recurring blockers or quality gaps (`repeated_blocker`, `frequent_changes_requested`, `documentation_gap`).
  * `ApprovalRecommendationHistory`: Actionable recommendation compiled from historical patterns audits.
  * `ApprovalHistoryReport`: Compilation report containing stats, trends, patterns, and recommendations.
  * `ApprovalHistoryValidator`: Gating class checking state transitions validity and report schemas.
  * `ApprovalHistoryAnalyzer`: Compiler calculating averages, metrics slopes, and patterns.
* **Current Status**: Current.

### 3.34 Automation Foundation Data Models
* **Purpose**: Abstract layer between the AI OS and various third-party automation platforms, managing topological graph flows independent of specific provider execution details.
* **Data Models & Components**:
  * `AutomationService`: Central conductor service coordinating provider registries, execution runs, memory caching, and Notion report publishing.
  * `AutomationManager`: Internal coordinator creating sessions and routing workflows executions to matching runners.
  * `AutomationRegistry`: catalog repository saving platform-independent workflow definitions.
  * `WorkflowDefinition`: Container organizing graphs, triggers, actions, conditions, variables, credential references, and execution policies.
  * `WorkflowGraph`: Node-edge structure modeling the workflow's topological dependency.
  * `WorkflowNode` & `WorkflowEdge`: Element components defining execution points and directions.
  * `WorkflowTrigger`, `WorkflowAction`, `WorkflowCondition`: Sub-elements defining execution starters, operations, and branches.
  * `WorkflowVariable`: State parameters carrying schema types and defaults.
  * `WorkflowCredentialReference`: Secure index pointer linking actions to specific vault keys.
  * `WorkflowExecutionPolicy`: Retry boundaries, delays, timeouts, and concurrency constraints.
  * `WorkflowMetadata` & `WorkflowArtifact`: Descriptive tag properties and generated output files list.
  * `AutomationSession`: Active workflow session lifecycle tracker.
  * `AutomationResult`: Consolidated execution result status, diagnostics output, and times.
  * `AutomationValidator`: Validator checking cycles, disconnected nodes, duplicate IDs, and policy constraints.
  * `AutomationProvider`: Abstract provider interface subclassed by platform stubs (`N8NProvider`, `GitHubActionsProvider`, `TemporalProvider`).
  * `AutomationProviderRegistry`: Registry holding active executor provider objects.
  * `AutomationReport`: Execution report payload formatted for Knowledge Hub updates.
* **Current Status**: Current.

### 3.35 Workflow Intelligence Data Models
* **Purpose**: Transforms engineering intents (e.g., deployments, tests runs, notifications) into provider-independent, optimized workflow graphs and schedules.
* **Data Models & Components**:
  * `WorkflowPlanner`: Central coordinator service creating sessions, generating plans, compiling reports, and caching summaries.
  * `WorkflowIntentAnalyzer`: Analysis engine mapping text expressions to templates and tags.
  * `WorkflowTemplateRegistry`: Registry hosting parameterized templates (CI/CD, Backups, Reviews).
  * `WorkflowTemplate`: Structural prototype holding nodes, edges, parameters, and descriptions.
  * `WorkflowComposer`: Hydration logic composing WorkflowDefinitions from templates and configs.
  * `WorkflowDependencyResolver`: Topological sorting engine ordering nodes based on graph edges.
  * `WorkflowOptimizer`: Graph optimizer merging duplicates, removing unreachable nodes, and pruning cycles.
  * `WorkflowSuggestionEngine`: Template selection helper matching intents to registry IDs.
  * `WorkflowConstraint`: Gate rule detailing conditions and validation severity thresholds.
  * `WorkflowPlanningSession`: Planning session lifecycle tracker.
  * `WorkflowPlanningReport`: Output report payload containing resolved dependencies, suggestion IDs, and optimizations compiled.
* **Current Status**: Current.

### 3.36 n8n Translation Engine Data Models
* **Purpose**: Compiles provider-independent Workflow IR schemas into native JSON structures compatible with self-hosted n8n instances.
* **Data Models & Components**:
  * `WorkflowTranslator`: Central coordinating service driving translation runs, logging report markdown files, caching summaries, and publishing notion database pages.
  * `WorkflowIR`: Canonical Intermediate Representation containing schemas for variables, nodes, and policies.
  * `WorkflowCompiler`: Translator compiling high-level workflow definitions to IR.
  * `WorkflowSerializer`: Serializer printing output structures as pretty JSON files.
  * `N8NTranslationEngine`: Engine driving translation runs by coordinating mappers.
  * `N8NWorkflowBuilder`: Final builder organizing connection blocks, default settings, and metadata tags.
  * `N8NNodeMapper`: Abstract mapper interface subclassed by `LocalN8NNodeMapper` (mapping triggers, actions, HTTP calls, scripts, and Slack notifies).
  * `N8NConnectionMapper`: Connection builder formatting DAG edges into n8n's connection routing map.
  * `N8NExpressionBuilder`: Logic expressions translator converting evaluation logic into JS expression blocks.
  * `N8NCredentialMapper`: Credential parser referencing named vault tags to secure API nodes.
  * `TranslationContext`: Class tracking local error lists and variables mappings.
  * `TranslationReport`: Translation summary containing connection counts, node counts, errors, and output JSON paths.
  * `TranslationValidator`: Schema and broken edges validator.
* **Current Status**: Current.

### 3.37 self-hosted n8n Integration Data Models
* **Purpose**: Coordinates communication, REST API integrations, auth configurations, session tokens, uploads, and health audits with self-hosted n8n servers.
* **Data Models & Components**:
  * `N8NIntegrationService`: Central conductor service coordinating client uploads, metadata tracking, status reports, and notion database publishing.
  * `N8NClient`: Concrete REST API client executing HTTP requests to `http://localhost:5678` with linear retry backoffs.
  * `N8NConnectionManager`: Builds configured HTTP clients and attaches authorization headers.
  * `N8NSessionManager`: Handles user email/password login session cookie establishment, reuse, and automatic renewal.
  * `N8NAuthenticationManager`: Resolves API keys, Bearer tokens, or session headers from configuration and environment variables.
  * `N8NWorkflowManager`: Coordinates workflow uploads (`POST /api/v1/workflows`), updates, deletions, activation patches, exports, and imports.
  * `N8NExecutionManager`: Triggers workflow executions (`POST /api/v1/workflows/{id}/run`), lists execution history, polls execution details, and handles cancellation or retry.
  * `N8NCredentialManager`: Manages creation and registration of external credential vault pointers.
  * `N8NWorkspaceManager`: Maps workflows ownership to active user workspace sessions.
  * `N8NHealthMonitor`: Polls `/healthz` and `/rest/settings` endpoints and records latency averages and P95 latency profiles.
  * `N8NVersionDetector` (aliases `N8NVersionManager`): Probes and detects the running version of the self-hosted n8n instance.
  * `N8NCapabilityDetector` (aliases `N8NCapabilityManager`): Dynamically discovers supported n8n capability lists (e.g. webhooks, variables, sticky-notes).
  * `N8NTelemetryCollector`: Compiles failure rates, execution latencies, and transaction metrics.
  * `N8NEventMonitor`: Records real-time workflow activation and run events.
  * `N8NValidator`: Validates URL patterns and connection profile parameters.
  * `N8NDiagnostics`: Runs credential, session, and network connection diagnostic checks with actionable remediations.
  * `N8NReportGenerator`: Outputs markdown status reports (`N8N_RUNTIME_STATUS.md`, `N8N_HEALTH.md`, etc.) inside the workspace `docs/n8n/` folder.
* **Current Status**: Production Integrated (Sprint 2A Complete).

### 3.38 Workflow Monitoring & Telemetry Data Models
* **Purpose**: Records, tracks, validates, and analyzes workflow execution telemetry traces and performance aggregates.
* **Data Models & Components**:
  * `WorkflowMonitoringService`: Central conductor registering execution traces, generating alerts, writing workspace files, and syncing Notion records.
  * `WorkflowExecutionTracker`: Memory registers recording run telemetry sessions.
  * `WorkflowExecutionRecord`: Single run details containing execution IDs, start/end stamps, metrics parameters, and error status messages.
  * `WorkflowExecutionState`: Outcome enums mapping states: SUCCESS, FAILED, TIMEOUT, CANCELLED, SKIPPED.
  * `WorkflowExecutionMetrics`: Duration details, CPU pcts, and memory usage MB counts.
  * `WorkflowTelemetry`: Set of execution records for a workflow.
  * `WorkflowPerformanceAnalyzer`: Aggregate stats calculations (success ratios, median delays, and P95 latency rates).
  * `WorkflowFailureAnalyzer`: Fail patterns identifier highlighting recurring errors.
  * `WorkflowRetryAnalyzer`: Ratios tracker counting retry loops and frequencies.
  * `WorkflowAlert`: Configure-triggered run warning structs.
  * `WorkflowHealthScore`: Struct scoring workflow health status out of 100.0.
  * `WorkflowStatistics`: Compiled performance aggregates object.
  * `WorkflowMonitoringReport`: Consolidated telemetry report payload.
  * `WorkflowMonitoringValidator`: Trace validator checking sequences and timing ordering logic.
* **Current Status**: Current.

### 3.39 Workflow Optimization Engine Data Models
* **Purpose**: Analyzes execution telemetries and graph structures to generate performance, latency, caching, parallelization, cost, and reliability optimization recommendations.
* **Data Models & Components**:
  * `WorkflowOptimizationService`: Conductor initiating workspace optimizations, exporting reports, caching summaries, and publishing Notion records.
  * `WorkflowOptimizationPlanner`: Central coordinator coordinating analyzers to construct optimization plans.
  * `WorkflowOptimizationAnalyzer`: Coordinates cost, latency, parallelization, redundancy, scheduling, and resource analyzers to construct optimization plans.
  * `WorkflowOptimizationKnowledgeBase`: Catalog of pre-defined reusable optimization patterns.
  * `WorkflowOptimizationPattern`: Pre-defined knowledge pattern definition.
  * `WorkflowOptimizationPlan`: Detailed plans carrying recommendations lists, expected score gains, time and cost savings.
  * `WorkflowOptimizationRecommendation`: Concrete recommendations detailing categories, confidence metrics, reasoning, supporting evidence, rollback considerations, and implementation difficulty.
  * `WorkflowOptimizationCategory`: Enums mapping optimization scopes (PERFORMANCE, COST, RELIABILITY, CACHING, parallelization).
  * `WorkflowOptimizationPriority` & `WorkflowOptimizationImpact`: Enums mapping priority and impact levels (HIGH, MEDIUM, LOW).
  * `WorkflowCostAnalyzer`: Scans for expensive nodes to suggest token cache and request reduction optimizations.
  * `WorkflowLatencyAnalyzer`: Tracks slow steps to suggest branch timeouts.
  * `WorkflowParallelizationAnalyzer`: Identifies independent sequential tasks to parallelize.
  * `WorkflowRedundancyAnalyzer`: Scans for duplicate nodes to merge actions.
  * `WorkflowSchedulingAnalyzer`: Optimizes cron schedules.
  * `WorkflowResourceAnalyzer`: Monitors excessive CPU or memory usage.
  * `WorkflowComplexityAnalyzer`: Measures graph complexity.
  * `WorkflowOptimizationValidator`: Validates recommendation unique IDs, evidence completeness, pattern references, and confidence limits.
  * `WorkflowOptimizationReport`: Consolidated report payload.
* **Current Status**: Current.

### 3.40 Workflow Versioning & Evolution Data Models
* **Purpose**: Manages immutable workflow version nodes, tracks history timelines, compares differences, validates semver rules, and outlines migration or rollback plans.
* **Data Models & Components**:
  * `WorkflowVersionService`: Central conductor registering version snapshots, diffing states, writing reports, and updating Notion pages.
  * `WorkflowVersion`: Dataclass containing references to IR schemas, translations, optimizations, approvals, and previous parent pointers.
  * `WorkflowVersionGraph`: DAG structure mapping parent-child version branches.
  * `WorkflowVersionHistory`: Chronological ordering of a workflow's versions.
  * `WorkflowVersionMetadata`: Metadata containing author details, tags, semantic versions, and status.
  * `WorkflowVersionDiff`: Immutable difference object mapping added, removed, and modified nodes or parameters.
  * `WorkflowSnapshot`: Full backup snapshot of workflow IR content.
  * `WorkflowEvolutionPlan`: Outline of steps required to upgrade to a target semantic version.
  * `WorkflowRollbackPlan`: Outline of steps, checklist, and downtime estimated to safely roll back to a prior version.
  * `WorkflowCompatibilityAnalyzer`: Evaluates compatibility (e.g. checking major version breaking bump rules).
  * `WorkflowMigrationPlanner`: Compiles upgrading steps and rollback targets checklists.
  * `WorkflowVersionValidator`: Checks version semver formatting and author completeness.
  * `WorkflowVersionReport`: Workspace-wide versioning summary payload.
  * `WorkflowVersionRegistry`: Registry containing version models and timelines.
* **Current Status**: Current.

### 3.41 Source Control Intelligence Platform Data Models
* **Purpose**: Coordinates local Git operations, manages remote provider integrations (e.g. GitHub REST and CLI), records telemetry metrics, and generates comprehensive markdown status reports inside the workspace.
* **Data Models & Components**:
  * `SourceControlRegistry`: Dynamic container saving registered repository host providers.
  * `ProviderDiscovery`: Environment scanner discovering active providers (e.g. GitHub) and registering them.
  * `ProviderConfigurationService`: Manages configuration properties, strategies (e.g. branch, commit, merge strategies), and credentials.
  * `ProviderHealthMonitor`: Polls host latencies, rate limits, and failure statistics.
  * `ProviderDiagnostics`: Runs local audits verifying git installations, gh CLI credentials, and token availability.
  * `ProviderValidator`: Validates repository name naming conventions and URLs.
  * `SourceControlService`: Central orchestrator delegating commands to active providers.
  * `LocalGitExecutor`: Low-level wrapper executing native shell commands within the workspace (checkout, stage, commit, reset, log, etc.).
  * `RepositoryManager`, `BranchManager`, `CommitManager`, `TagManager`, `MergeManager`, `DiffManager`, `WorkspaceRepositoryManager`: Managers coordinating local Git operations.
  * `PullRequestManager`, `IssueManager`, `ReleaseManager`, `WorkflowManager`, `WebhookManager`: Managers coordinating remote host operations.
  * `SourceControlTelemetry`: Compiles execution times, counts, and success rates.
  * `SourceControlStatistics`: Aggregates repository, branch, PR, issue, release, and workflow totals.
  * `SourceControlReportGenerator`: Outputs markdown status documents (`SOURCE_CONTROL_STATUS.md`, `REPOSITORY_REPORT.md`, `BRANCH_REPORT.md`, `PULL_REQUEST_REPORT.md`, `RELEASE_REPORT.md`, `WORKFLOW_REPORT.md`, `DIAGNOSTICS.md`) to `docs/source_control/`.
* **Current Status**: Current (Sprint Complete).

### 3.42 Persistence & Workspace Platform Data Models
* **Purpose**: Coordinates database connection pooling, transaction savepoint rollbacks, schema migrations, and exposes durable repositories mapping workspaces, sessions, projects, profiles, and configurations to SQL.
* **Data Models & Components**:
  * `PersistenceConfigurationService`: Loads database configuration properties (host, port, credentials, pool limits, active policy).
  * `PersistenceRegistry`: Registry cataloging and resolving registered pluggable PersistenceProviders.
  * `RepositoryRegistry`: Centralized container registering data repositories.
  * `PersistenceService`: Core unified service orchestrating database operations.
  * `PersistencePolicy`: Enum class declaring enforcement constraints (`STRICT`, `BEST_EFFORT`, `READ_ONLY`, `MANUAL_RECOVERY`).
  * `PersistenceStatus`: Enum class tracking status outcomes (`SUCCESS`, `AWAITING_RUNTIME_CONFIGURATION`, `PERSISTENCE_UNAVAILABLE`, `READ_ONLY_MODE`, `VALIDATION_FAILED`, `TRANSACTION_ABORTED`, `TIMEOUT`, `RETRY_REQUIRED`, `PERMISSION_DENIED`, `UNKNOWN_FAILURE`).
  * `PersistenceResult`: Wrapper returning execution metadata, message, diagnostics, latency, and payloads.
  * `DatabaseTransport` & `PostgreSQLTransport`: Database driver abstraction isolating execution from concrete backends.
  * `WorkspaceRepository` / `WorkspaceRepositoryImpl`: Maps workspace models to durable databases.
  * `WorkspaceSessionRepository` / `WorkspaceSessionRepositoryImpl`: Handles session lifecycle durability.
  * `ProjectRepository` / `ProjectRepositoryImpl`: Persists project metadata.
  * `EngineeringProfileRepository` / `EngineeringProfileRepositoryImpl`: Durably maps engineering profiles, versions, and rollback histories.
  * `ConfigurationRepository` / `ConfigurationRepositoryImpl`: Persists configuration profile settings.
  * `PersistenceBootstrapper`: Coordinates database schema creation migrations on startup.
  * `WorkspacePersistenceService`: Coordinates durable workspace environments.
  * `WorkspacePersistenceValidator`: Checks configurations and metadata consistency.
  * `WorkspacePersistenceTelemetry`: Records transaction rollbacks and latencies.
  * `WorkspacePersistenceStatistics`: Compiles count stats from tables.
  * `WorkspacePersistenceReportGenerator`: Compiles statuses, health, statistics, and registry maps to docs.
  * `EngineeringTaskRepository` / `EngineeringTaskRepositoryImpl`: Maps engineering implementation tasks to persistent storage.
  * `PlanningRepository` / `PlanningRepositoryImpl`: Persists software engineering plans and dependencies.
  * `ApprovalRepository` / `ApprovalRepositoryImpl`: Handles active quality gating session durability.
  * `ReviewRepository` / `ReviewRepositoryImpl`: Persists gated run review sessions and transition histories.
  * `DocumentationMetadataRepository` / `DocumentationMetadataRepositoryImpl`: Persists document templates and artifact generation logs.
  * `TestSessionRepository` / `TestSessionRepositoryImpl`: Handles test execution session tracking.
  * `TestResultRepository` / `TestResultRepositoryImpl`: Handles detailed execution outcome status logs.
  * `EngineeringMemoryService` / `EngineeringMemoryServiceImpl`: Orchestrator coordinating all engineering memory database operations.
  * `EngineeringMemoryValidator`: Validates data structures for all engineering categories.
  * `EngineeringMemoryTelemetry`: Records latency and transaction details for engineering queries.
  * `EngineeringMemoryStatistics`: Aggregates active row metrics from engineering database tables.
  * `EngineeringMemoryHealthMonitor`: Verifies health and schema versions for engineering tables.
  * `EngineeringMemoryReportGenerator`: Compiles markdown diagnostic and statistics reports for engineering memory.
  * `WorkflowRepository` / `WorkflowRepositoryImpl`: Persists workflow node configurations, edge routes, triggers, actions, conditions, variables, and runtime execution policies.
  * `WorkflowExecutionRepository` / `WorkflowExecutionRepositoryImpl`: Persists execution session status, time duration metrics, success codes, and error summaries.
  * `WorkflowMonitoringRepository` / `WorkflowMonitoringRepositoryImpl`: Persists latency statistics, health score ratings, degradations alerts, and retry frequency logs.
  * `WorkflowOptimizationRepository` / `WorkflowOptimizationRepositoryImpl`: Persists optimization plans, recommended cache strategies, and complexity audit results.
  * `WorkflowVersionRepository` / `WorkflowVersionRepositoryImpl`: Persists parent-child lineages, semver tags, compatibility ratings, and rollback pathways.
  * `WorkflowTranslationRepository` / `WorkflowTranslationRepositoryImpl`: Persists compiler mappings, compilation warnings, node mappings, and IR version summaries.
  * `WorkflowIntegrationRepository` / `WorkflowIntegrationRepositoryImpl`: Persists server URLs, connection profile health indicators, and remote discovery capabilities.
  * `AutomationTelemetryRepository` / `AutomationTelemetryRepositoryImpl`: Persists average and p95 latencies and failure categories.
  * `AutomationStatisticsRepository` / `AutomationStatisticsRepositoryImpl`: Persists counts and failure ratios across all tables.
  * `AutomationPersistenceService` / `AutomationPersistenceServiceImpl`: Orchestrator coordinating all automation persistence database operations.
  * `AutomationPersistenceValidator`: Validates data structures for all automation categories.
  * `AutomationPersistenceTelemetry`: Records latency and transaction details for automation queries.
  * `AutomationPersistenceStatistics`: Aggregates active row metrics from automation database tables.
  * `AutomationPersistenceHealthMonitor`: Verifies health and schema versions for automation tables.
  * `AutomationPersistenceReportGenerator`: Compiles markdown diagnostic and statistics reports for automation persistence.
  * `AIProviderRepository` / `AIProviderRepositoryImpl`: Persists registered provider profiles (version, priority, status, costs, etc.).
  * `ProviderCapabilityRepository` / `ProviderCapabilityRepositoryImpl`: Persists provider capabilities maps.
  * `ProviderHealthRepository` / `ProviderHealthRepositoryImpl`: Persists provider availability indicators and health states.
  * `ProviderTelemetryRepository` / `ProviderTelemetryRepositoryImpl`: Persists request latency performance profiles.
  * `ProviderStatisticsRepository` / `ProviderStatisticsRepositoryImpl`: Persists query successes and failures totals.
  * `ProviderQuotaRepository` / `ProviderQuotaRepositoryImpl`: Persists budget quota limits and exhaustion thresholds.
  * `ProviderRoutingRepository` / `ProviderRoutingRepositoryImpl`: Persists selector model routing choices.
  * `ProviderSessionRepository` / `ProviderSessionRepositoryImpl`: Persists runtime session context configurations.
  * `ProviderCheckpointRepository` / `ProviderCheckpointRepositoryImpl`: Persists serializable execution checkpoints for failover switches.
  * `ProviderFailoverRepository` / `ProviderFailoverRepositoryImpl`: Persists failover event switches.
  * `AIUsageStatisticsRepository` / `AIUsageStatisticsRepositoryImpl`: Persists daily and monthly cumulative token trackers.
  * `AIMemoryRepository` / `AIMemoryRepositoryImpl`: Persists episodic facts and long term knowledge bases.
  * `AIMemoryPersistenceService` / `AIMemoryPersistenceServiceImpl`: Coordinating orchestrator for AI Memory Persistence.
  * `AIMemoryValidator`: Validates incoming data profiles for AI provider parameters.
  * `AIMemoryTelemetry`: Monitors validation and transaction queries latencies.
  * `AIMemoryStatistics`: Compiles telemetry and status metrics.
  * `AIMemoryHealthMonitor`: Evaluates current provider availability ratings.
  * `AIMemoryReportGenerator`: Produces operational audit logs.
* **Current Status**: Completed.

### 3.9 Runtime Intelligence Platform (Sprint 4 Milestone 6)
* **Purpose**: Self-monitoring and unified observability consumer for the Persistence Platform, recording repository latencies, execution throughputs, transaction depths, connection pool capacities, and migration history.
* **Core Interfaces & Classes**:
  * `RuntimeIntelligenceService` / `RuntimeIntelligenceServiceImpl`: Orchestrates the self-monitoring platform.
  * `RuntimeHealthMonitor`: Checks live database connections and availability percentages.
  * `RuntimeTelemetryCollector`: Gathers latencies, connection statuses, failures, and retries.
  * `RuntimeStatisticsEngine`: Tracks transaction counts, policies used, and cache hit/miss/read-through/write-through metrics.
  * `RuntimeDiagnosticsEngine`: Classifies runtime errors (`INFO`, `WARNING`, `ERROR`, `CRITICAL`) and maps them to remediation logs.
  * `RuntimeCapacityAnalyzer`: Evaluates connection pool starvation risks.
  * `RuntimeRecommendationEngine`: Automatically logs database tuning warnings based on observed metrics (Performance, Reliability, Capacity, Maintenance).
  * `RuntimeQueryProfiler`: Tracks queries executing slower than the 100ms threshold.
  * `RuntimeTransactionProfiler`: Profiles transaction durations and nesting levels (`tx_depth`).
  * `RuntimeRepositoryProfiler`: Profiles table access rates and averages repository latencies.
  * `RuntimeLifecycleMonitor`: Tracks boot durations, database migration history, and provider hot swaps.
  * `RuntimeCorrelationManager`: Injects a thread-local correlation context (`CorrelationID`, `WorkspaceID`, `ProjectID`, `Repository`, `Operation`) without modifying Repository APIs.
  * `RuntimeReportGenerator`: Compiles operational dashboards to Markdown status reports in `docs/persistence/`.
* **Current Status**: Completed.

### 3.10 PostgreSQL Production Live Validation (Sprint 4 Milestone 7)
* **Purpose**: Production live validation of all 30 repositories against the relational database engine, auditing connection lifecycles, connection pool recovery, schema migrations, policy behaviors, and runtime diagnostics.
* **Validation Artifacts**:
  * `POSTGRESQL_PRODUCTION_VALIDATION_REPORT.md`
  * `POSTGRESQL_RUNTIME_HEALTH.md`
  * `POSTGRESQL_PERFORMANCE_BASELINE.md`
  * `POSTGRESQL_DIAGNOSTICS.md`
  * `POSTGRESQL_CAPACITY_REPORT.md`
  * `POSTGRESQL_REPOSITORY_VALIDATION.md`
  * `POSTGRESQL_FAILURE_RECOVERY.md`
  * `POSTGRESQL_MIGRATION_VALIDATION.md`
* **Current Status**: Production Validated.

### 3.11 Redis Platform (Sprint 5 Milestones 1, 2, 3 & 4)
* **Purpose**: Implements high-performance runtime cache acceleration, session storage, and distributed coordination. Ephemeral states, dialog sessions, rate limits, lookup caches, lock leases, wait graphs, and reentrancy states are stored in Redis to accelerate read/write performance. Zero-downtime grace fallback is achieved via Simulated FakeRedisClient, local in-memory session dictionaries, and local fallback lock tables if Redis is offline.
* **Core Interfaces & Classes**:
  - `RedisRuntimeService` / `RedisRuntimeServiceImpl`: Coordinator orchestrating status, health, and reporting.
  - `RedisConnectionManager`: Directs connection pools and handles simulated fallback.
  - `RedisTransportImpl`: Low-level command routing recording latencies.
  - `RedisProviderImpl`: Ephemeral key-value operations wrapper.
  - `RedisCacheServiceImpl`: Main caching entrypoint with read-through, write-through, and cache-aside methods.
  - `CachePolicyManagerImpl`: Manages explicit cache policies and configurable TTL overrides.
  - `CacheInvalidationManagerImpl`: Coordinates manual, bulk, entity, workspace, project, provider, and pattern invalidations.
  - `CacheWarmupServiceImpl`: Prepopulates hot metadata at startup in a background thread.
  - `CacheRebuildServiceImpl`: Incrementally rebuilds cache once Redis connection is re-established.
  - `CacheStatisticsCollectorImpl` / `CacheHealthMonitorImpl` / `CacheDiagnosticsImpl` / `CacheRecommendationEngineImpl`: Caching statistics, diagnostics, health check, and recommendation engine.
  - `RedisSessionServiceImpl` / `SessionManagerImpl` / `SessionStoreImpl`: Main session engine directing sliding expiration, maximum lifetimes, heartbeats, and in-memory fallbacks.
  - `SessionRegistryImpl`: Centralized session ownership registry storing configs and policies.
  - `SessionRecoveryManagerImpl`: Rebuilds recoverable and persistent reference session data once connection returns.
  - `SessionStatisticsCollectorImpl` / `SessionHealthMonitorImpl` / `SessionDiagnosticsImpl` / `SessionRecommendationEngineImpl`: Telemetry monitoring, error capture, and optimization advice.
  - `RedisCoordinationServiceImpl` / `DistributedLockManagerImpl` / `LockLeaseManagerImpl` / `MutexManagerImpl`: Directs lock acquisition, renewals, releases, and reentrant/shared locks.
  - `LockRegistryImpl`: Centralized configuration registry for lock metadata.
  - `DeadlockDetectorImpl`: Cycle detector running DFS wait-graph cycles and recommendations.
  - `CoordinationStatisticsCollectorImpl` / `CoordinationHealthMonitorImpl` / `CoordinationDiagnosticsImpl` / `CoordinationRecommendationEngineImpl`: Tracks acquisition delays, wait latencies, diagnosed errors, and lock optimization advices.
* **Current Status**: Completed.

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
