# Personal AI OS — Documentation Index

> **Sprint 7 Milestone 1 — Documentation Suite Foundation**
> *Version 2.0 · July 2026 · Unified Documentation Architecture*

This is the canonical documentation index for the Personal AI OS monorepo. Every document in the system is reachable from here. Start with the section most relevant to your task.

---

## 🗺️ Quick Navigation

| I want to… | Go to… |
|---|---|
| View auto-generated catalogs | [Generated Documentation →](#generated-documentation) |
| View detailed API reference | [API & Service Reference →](#api--service-reference) |
| View architecture diagrams | [Architecture Diagrams →](#architecture-diagrams) |
| Understand the system | [Architecture →](#architecture) |
| Learn individual services | [Services →](#services) |
| Build or extend a skill | [Skills →](#skills) |
| Understand the runtime/memory | [Runtime →](#runtime) |
| Set up the project | [Deployment →](#deployment) |
| Debug a problem | [Troubleshooting →](#troubleshooting) |
| Understand data storage | [Database →](#database) |
| Explore all persistence reports | [Persistence →](#persistence) |
| Check AI provider status | [Providers →](#providers) |
| Check infrastructure | [Infrastructure →](#infrastructure) |
| View n8n workflow docs | [n8n →](#n8n) |
| View source control reports | [Source Control →](#source-control) |
| See the roadmap | [Roadmaps →](#roadmaps) |
| Review design decisions | [ADRs →](#adrs) |
| Read engineering standards | [Guides →](#guides) |
| Check milestone history | [Milestones →](#milestones) |

---

## Generated Documentation

> Auto-generated catalogs of services, repositories, skills, providers, runtime components, database models, and dependency injection bindings.

📁 [`docs/generated/`](generated/README.md)

**⚠️ DO NOT EDIT MANUALLY** — these files are regenerated on every `python -m aios.docgen` invocation.

| Catalog | Description |
|---|---|
| [services.md](generated/services.md) | All 123 service interfaces and implementations |
| [repositories.md](generated/repositories.md) | All 104 repository implementations and entities |
| [skills.md](generated/skills.md) | All 10 registered skills with metadata |
| [providers.md](generated/providers.md) | All 7 AI providers with cost and capability matrices |
| [runtime.md](generated/runtime.md) | All 221 runtime components and utilities |
| [db_models.md](generated/db_models.md) | All 379 database models (enums and dataclasses) |
| [dependency_graph.md](generated/dependency_graph.md) | All 290 DI bindings with Mermaid visualization |

To regenerate: `python -m aios.docgen`

---

## API & Service Reference

> Detailed API documentation for all services with method signatures, parameters, return types, exceptions, and lifecycle methods.

📁 [`docs/reference/`](reference/README.md)

**⚠️ DO NOT EDIT MANUALLY** — these files are regenerated on every `python -m aios.docgen.refgen` invocation.

| Reference | Description |
|-----------|-------------|
| [services.md](reference/services.md) | Complete service API reference with method signatures and parameters |
| [interfaces.md](reference/interfaces.md) | Interface to implementation mappings |
| [lifecycle.md](reference/lifecycle.md) | Service lifecycle methods (initialization, runtime, cleanup) |
| [dependency_injection.md](reference/dependency_injection.md) | Constructor dependencies and DI bindings |
| [api_reference.md](reference/api_reference.md) | Comprehensive API reference (all services in one file) |

**Statistics**: 123 services · 496 public methods · 42 lifecycle methods · 5 services with DI dependencies

To regenerate: `python -m aios.docgen.refgen`

---

## Architecture Diagrams

> Mermaid diagrams visualizing system architecture, dependencies, lifecycle, and data flows.

📁 [`docs/diagrams/`](diagrams/README.md)

**⚠️ DO NOT EDIT MANUALLY** — these files are regenerated on every `python -m aios.docgen.diagram_main` invocation.

| Diagram | Description |
|---------|-------------|
| [architecture.md](diagrams/architecture.md) | Overall AI OS architecture with component relationships |
| [dependency_graph.md](diagrams/dependency_graph.md) | Service dependency graph showing inter-service relationships |
| [lifecycle.md](diagrams/lifecycle.md) | Runtime lifecycle phases (initialization, runtime, cleanup) |
| [runtime.md](diagrams/runtime.md) | Bootstrap sequence and system initialization flow |
| [persistence.md](diagrams/persistence.md) | Multi-layer persistence architecture (SQLite, PostgreSQL, Redis, Qdrant) |
| [semantic_memory.md](diagrams/semantic_memory.md) | Semantic memory pipeline with vector embeddings |
| [hybrid_retrieval.md](diagrams/hybrid_retrieval.md) | Hybrid keyword and semantic search retrieval |
| [omniroute.md](diagrams/omniroute.md) | OmniRoute model selection and routing architecture |
| [agents.md](diagrams/agents.md) | Agent interaction and coordination flow |

**Format**: Mermaid syntax (viewable in GitHub, VS Code, Mermaid Live Editor)

To regenerate: `python -m aios.docgen.diagram_main`

---

## Architecture

> Core system design, kernel specification, orchestration engines, and architectural evolution.

📁 [`docs/architecture/`](architecture/README.md)

| Document | Purpose |
|---|---|
| [KERNEL_SPECIFICATION.md](architecture/KERNEL_SPECIFICATION.md) | AI OS Kernel: runtime loop, event model, lifecycle contracts |
| [CORE_ARCHITECTURE.md](architecture/CORE_ARCHITECTURE.md) | Core package layers, module boundaries, service registry |
| [BRAIN.md](architecture/BRAIN.md) | Brain orchestrator: reasoning pipeline and context assembly |
| [INTELLIGENCE_ENGINE.md](architecture/INTELLIGENCE_ENGINE.md) | Model routing, provider selection, embeddings |
| [ACTION_ENGINE.md](architecture/ACTION_ENGINE.md) | Tool dispatch, skill execution, output formatting |
| [TASK_EXECUTOR.md](architecture/TASK_EXECUTOR.md) | Planning loop, approval gates, retries |
| [CONVERSATIONS.md](architecture/CONVERSATIONS.md) | Session management and turn structure |
| [ARCHITECTURE_GUIDELINES.md](architecture/ARCHITECTURE_GUIDELINES.md) | Boundary decoupling rules and DI policy |
| [SYSTEM_DESIGN.md](architecture/SYSTEM_DESIGN.md) | Component diagrams, sequence maps, event pipelines |
| [ARCHITECTURE_EVOLUTION_REPORT.md](architecture/ARCHITECTURE_EVOLUTION_REPORT.md) | Brain, Planner, Selector v2 scaling decisions |

---

## Services

> Individual service modules, APIs, and integration patterns.

📁 [`docs/services/`](services/README.md)

| Document | Purpose |
|---|---|
| [PROVIDERS.md](services/PROVIDERS.md) | AI provider registry: models, routing, failover, cost |
| [COMMANDS.md](services/COMMANDS.md) | CLI command registry: all slash commands |
| [SECURITY.md](services/SECURITY.md) | Security service: secrets, encryption, trust boundaries |
| [DEVELOPER_SERVICE.md](services/DEVELOPER_SERVICE.md) | Developer service: code generation, analysis, review |

---

## Skills

> Composable, prompt-driven capability modules.

📁 [`docs/skills/`](skills/README.md)

| Document | Purpose |
|---|---|
| [SKILLS_OVERVIEW.md](skills/SKILLS_OVERVIEW.md) | Complete skills registry and capability map |
| [GITHUB_SKILL.md](skills/GITHUB_SKILL.md) | GitHub skill: PR review, CI analysis, release notes |
| [GITHUB_SKILL_README.md](skills/GITHUB_SKILL_README.md) | GitHub skill implementation and prompt reference |

---

## Runtime

> Runtime intelligence: context assembly, retrieval pipelines, embedding engines, semantic search.

📁 [`docs/runtime/`](runtime/README.md)

| Document | Purpose |
|---|---|
| [RUNTIME_INTELLIGENCE_ARCHITECTURE.md](runtime/RUNTIME_INTELLIGENCE_ARCHITECTURE.md) | Qdrant-backed runtime intelligence design |
| [RUNTIME_INTELLIGENCE_DIAGNOSTICS.md](runtime/RUNTIME_INTELLIGENCE_DIAGNOSTICS.md) | Operational diagnostics for the runtime layer |

Full runtime report suite: [`docs/persistence/`](persistence/README.md)

---

## Infrastructure

> External service integrations: n8n workflow automation and source control operations.

📁 [`docs/infrastructure/`](infrastructure/README.md)

| Document | Purpose |
|---|---|
| [N8N_RUNTIME_STATUS.md](infrastructure/N8N_RUNTIME_STATUS.md) | n8n server status and connection health |
| [N8N_RUNTIME_INTEGRATION_REPORT.md](infrastructure/N8N_RUNTIME_INTEGRATION_REPORT.md) | Full n8n integration report |
| [SOURCE_CONTROL_STATUS.md](infrastructure/SOURCE_CONTROL_STATUS.md) | Git repository health and CI pipeline state |

Full n8n suite: [`docs/n8n/`](n8n/README.md) · Full source control suite: [`docs/source_control/`](source_control/README.md)

---

## Database

> All persistence layers: SQLite, PostgreSQL, Redis, and Qdrant.

📁 [`docs/database/`](database/README.md)

| Document | Purpose |
|---|---|
| [ARCHITECTURE_DISCOVERY.md](database/ARCHITECTURE_DISCOVERY.md) | Persistence architecture: schema, indexes, data flow |
| [REPOSITORY_REGISTRY.md](database/REPOSITORY_REGISTRY.md) | Registry of all repository implementations and SQL tables |
| [POSTGRESQL_PERFORMANCE_BASELINE.md](database/POSTGRESQL_PERFORMANCE_BASELINE.md) | PostgreSQL benchmarks: latency and throughput |
| [POSTGRESQL_PRODUCTION_VALIDATION_REPORT.md](database/POSTGRESQL_PRODUCTION_VALIDATION_REPORT.md) | Full production validation of 80+ repositories |
| [POSTGRESQL_CAPACITY_REPORT.md](database/POSTGRESQL_CAPACITY_REPORT.md) | Capacity planning: row counts, index sizes |

Full persistence report suite (162 files): [`docs/persistence/`](persistence/README.md)

---

## Roadmaps

> Product vision, requirements, technology choices, and release planning.

📁 [`docs/roadmaps/`](roadmaps/README.md)

| Document | Purpose |
|---|---|
| [PROJECT_VISION.md](roadmaps/PROJECT_VISION.md) | What the AI OS is, why it exists, guiding philosophy |
| [PRD.md](roadmaps/PRD.md) | Product Requirements: use cases, MVP scope |
| [DRD.md](roadmaps/DRD.md) | Design Requirements: schemas, contracts |
| [TECH_STACK.md](roadmaps/TECH_STACK.md) | Approved languages, packages, platform requirements |
| [ROADMAP.md](roadmaps/ROADMAP.md) | Sprint milestones and product maturity horizons |

---

## ADRs

> Architecture Decision Records — rationale behind every major technical choice.

📁 [`docs/adr/`](adr/README.md)

| Document | Purpose |
|---|---|
| [DECISION_LOG.md](adr/DECISION_LOG.md) | Chronological ADR log with context and rationale |
| [REPOSITORY_AUDIT.md](adr/REPOSITORY_AUDIT.md) | Code quality baseline for Sprint S0.x refactoring |

---

## Guides

> Engineering standards, coding conventions, and how-to references for contributors.

📁 [`docs/guides/`](guides/README.md)

| Document | Purpose |
|---|---|
| [CONTRIBUTING.md](guides/CONTRIBUTING.md) | Setup, branching, commit conventions |
| [ENGINEERING_CONSTITUTION.md](guides/ENGINEERING_CONSTITUTION.md) | Non-negotiable engineering principles |
| [ENGINEERING_GUIDELINES.md](guides/ENGINEERING_GUIDELINES.md) | Boring by default, optimize for deletion, SRP |
| [CODING_STANDARDS.md](guides/CODING_STANDARDS.md) | Style rules, 400-line file limit, complexity budgets |
| [TESTING_GUIDELINES.md](guides/TESTING_GUIDELINES.md) | Unit, integration, contract, and regression testing |
| [SECURITY_GUIDELINES.md](guides/SECURITY_GUIDELINES.md) | Secrets, encryption, risk gates |
| [DOCUMENTATION_GUIDELINES.md](guides/DOCUMENTATION_GUIDELINES.md) | Markdown formatting, docstrings, metadata blocks |
| [IMPLEMENTATION_GUIDELINES.md](guides/IMPLEMENTATION_GUIDELINES.md) | How to add skills, tools, and commands |
| [AI_MODEL_STRATEGY.md](guides/AI_MODEL_STRATEGY.md) | Model selection, offline runtimes, fallback chains |
| [ENGINEERING_BIBLE.md](guides/ENGINEERING_BIBLE.md) | CLI REPL mechanics, file execution map |

---

## Deployment

> Installation, configuration, environment setup, and service dependencies.

📁 [`docs/deployment/`](deployment/README.md)

| Document | Purpose |
|---|---|
| [OPERATIONS_MANUAL.md](deployment/OPERATIONS_MANUAL.md) | Installation, configuration, backups, diagnostics, recovery |

---

## Troubleshooting

> Diagnostic guides and failure recovery playbooks.

📁 [`docs/troubleshooting/`](troubleshooting/README.md)

| Document | Purpose |
|---|---|
| [WORKSPACE_DIAGNOSTICS.md](troubleshooting/WORKSPACE_DIAGNOSTICS.md) | Workspace layer: save/load/session failures |
| [POSTGRESQL_DIAGNOSTICS.md](troubleshooting/POSTGRESQL_DIAGNOSTICS.md) | PostgreSQL: connectivity, schema validation |
| [POSTGRESQL_FAILURE_RECOVERY.md](troubleshooting/POSTGRESQL_FAILURE_RECOVERY.md) | PostgreSQL recovery playbook |
| [REDIS_DIAGNOSTICS.md](troubleshooting/REDIS_DIAGNOSTICS.md) | Redis: connectivity, eviction, TTL bugs |
| [REDIS_FAILURE_RECOVERY.md](troubleshooting/REDIS_FAILURE_RECOVERY.md) | Redis recovery playbook |

---

## Persistence

> Full persistence platform documentation: PostgreSQL, Redis, Qdrant, and Workspace — architecture, diagnostics, health, statistics, validation, and integration reports.

📁 [`docs/persistence/`](persistence/README.md)

| Category | Key Documents |
|---|---|
| Architecture & Discovery | [ARCHITECTURE_DISCOVERY.md](persistence/ARCHITECTURE_DISCOVERY.md) · [REPOSITORY_REGISTRY.md](persistence/REPOSITORY_REGISTRY.md) |
| PostgreSQL | [POSTGRESQL_PRODUCTION_VALIDATION_REPORT.md](persistence/POSTGRESQL_PRODUCTION_VALIDATION_REPORT.md) · [POSTGRESQL_PERFORMANCE_BASELINE.md](persistence/POSTGRESQL_PERFORMANCE_BASELINE.md) |
| Redis | [REDIS_PLATFORM_ARCHITECTURE.md](persistence/REDIS_PLATFORM_ARCHITECTURE.md) · [REDIS_PLATFORM_DISCOVERY.md](persistence/REDIS_PLATFORM_DISCOVERY.md) |
| Qdrant | [QDRANT_PLATFORM_ARCHITECTURE.md](persistence/QDRANT_PLATFORM_ARCHITECTURE.md) · [QDRANT_PLATFORM_DISCOVERY.md](persistence/QDRANT_PLATFORM_DISCOVERY.md) |
| Runtime Intelligence | [RUNTIME_INTELLIGENCE_ARCHITECTURE.md](persistence/RUNTIME_INTELLIGENCE_ARCHITECTURE.md) · [RUNTIME_INTELLIGENCE_DISCOVERY.md](persistence/RUNTIME_INTELLIGENCE_DISCOVERY.md) |
| Workspace | [WORKSPACE_DIAGNOSTICS.md](persistence/WORKSPACE_DIAGNOSTICS.md) · [WORKSPACE_SERVICE_INTEGRATION.md](persistence/WORKSPACE_SERVICE_INTEGRATION.md) |

> 162 documents total — see [`persistence/README.md`](persistence/README.md) for the complete index.

---

## Providers

> AI provider health, routing decisions, cost analysis, and performance benchmarks.

📁 [`docs/providers/`](providers/README.md)

| Document | Purpose |
|---|---|
| [PROVIDERS_STATUS.md](providers/PROVIDERS_STATUS.md) | Current status of all registered AI providers |
| [PROVIDERS_HEALTH.md](providers/PROVIDERS_HEALTH.md) | Aggregate provider health check results |
| [ROUTING_REPORT.md](providers/ROUTING_REPORT.md) | OmniRoute model selection and routing decisions |
| [COST_REPORT.md](providers/COST_REPORT.md) | Provider cost analysis and budget tracking |
| [PERFORMANCE_REPORT.md](providers/PERFORMANCE_REPORT.md) | Provider latency and throughput benchmarks |

---

## n8n

> n8n workflow automation: server status, health, diagnostics, and execution reports.

📁 [`docs/n8n/`](n8n/README.md)

| Document | Purpose |
|---|---|
| [N8N_RUNTIME_STATUS.md](n8n/N8N_RUNTIME_STATUS.md) | n8n server runtime status |
| [N8N_HEALTH.md](n8n/N8N_HEALTH.md) | n8n service health check |
| [N8N_DIAGNOSTICS.md](n8n/N8N_DIAGNOSTICS.md) | n8n diagnostic reports |
| [N8N_EXECUTION_REPORT.md](n8n/N8N_EXECUTION_REPORT.md) | Workflow execution results |
| [N8N_SERVER_INFO.md](n8n/N8N_SERVER_INFO.md) | n8n server configuration |

---

## Source Control

> Git repository health, branch management, pull requests, releases, and CI workflow reports.

📁 [`docs/source_control/`](source_control/README.md)

| Document | Purpose |
|---|---|
| [SOURCE_CONTROL_STATUS.md](source_control/SOURCE_CONTROL_STATUS.md) | Git repository health and CI pipeline state |
| [REPOSITORY_REPORT.md](source_control/REPOSITORY_REPORT.md) | Repository structure and metadata |
| [BRANCH_REPORT.md](source_control/BRANCH_REPORT.md) | Branch status and management |
| [PULL_REQUEST_REPORT.md](source_control/PULL_REQUEST_REPORT.md) | Pull request activity |
| [RELEASE_REPORT.md](source_control/RELEASE_REPORT.md) | Release history and tagging |
| [WORKFLOW_REPORT.md](source_control/WORKFLOW_REPORT.md) | GitHub Actions workflow results |
| [DIAGNOSTICS.md](source_control/DIAGNOSTICS.md) | Source control diagnostics |

---

## Milestones

> Sprint milestone completion reports.

📁 [`docs/milestones/`](milestones/README.md)

| Sprint | Reports |
|---|---|
| S0 — Architecture | Persistence, Approval Engine, Automation Intelligence, Source Control |
| S6 — Qdrant/Vector | Documentation Intelligence |
| S7 — Documentation | M1: Documentation Foundation *(this milestone)* |
| n8n Integration | Production validation and runtime integration |

---

## Legacy Indexes

The following indexes are preserved for backward compatibility:

| Document | Notes |
|---|---|
| [INDEX.md](INDEX.md) | Original documentation homepage (pre-S7.M1) |
| [AI_CONTEXT.md](AI_CONTEXT.md) | AI-optimized entrypoint (token-efficient; AI agents start here) |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Live project dashboard: priorities, risks, technical debt |
| [VERSION.md](VERSION.md) | Version registry: project, architecture, documentation, API |
| [CHANGELOG.md](CHANGELOG.md) | Chronological release and change log |

---

*Documentation Architecture: Sprint 7 Milestone 1 · Personal AI OS · July 2026*
