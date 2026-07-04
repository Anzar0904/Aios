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
