# Research Workflows Spec
**Sprint 11 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define standard execution workflows, process states, and verification steps for common research tasks.
* **Scope**: Governs automated API scans, compiler diagnostics research, and package checks.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [research/orchestration/research_planning.md](file:///Users/anzarakhtar/aios/docs/research/orchestration/research_planning.md) - Research planning.
  * [research/orchestration/automation_pipeline.md](file:///Users/anzarakhtar/aios/docs/research/orchestration/automation_pipeline.md) - Automation workflows.

---

## 1. Core Research Workflows

The **Research Orchestration** module defines three standard workflows for common engineering research tasks:

### 1.1 API Specification Scan
1. **Target Identification**: Read target API endpoint details.
2. **Search Specifications**: Query search providers to locate official API documentation or Swagger files.
3. **Parse Parameters**: Convert raw docs to markdown, extracting endpoint paths, request parameters, and response schemas.
4. **Cache & Index**: Save the extracted schemas to the database, mapping them to the local concept catalog.

### 1.2 Compiler Diagnostics Research
1. **Analyze Error**: Extract error codes, messages, and line numbers from compiler diagnostics.
2. **Search Issues**: Query search providers (targeting GitHub Issues, StackOverflow, and forums) for the error message.
3. **Extract Solutions**: Identify discussion threads containing solutions, extracting code snippets and verification comments.
4. **Compile Fixes**: Suggest resolution paths to the developer agent to fix the error.

### 1.3 Package Dependency Checks
1. **Read Lockfiles**: Identify active library versions from workspace configuration files.
2. **Check Vulnerabilities**: Query vulnerability databases to check for security advisories.
3. **Analyze Version Drift**: Search release logs to identify version changes, and check for deprecation warnings.
