# Project Intelligence Guide

Project Intelligence is the master orchestration and aggregation layer in AI OS. It gathers insights from workspace analysis, git repositories, database environments, deployments, and n8n workflows, presenting them in a single, unified project model.

---

## Capabilities

1. **Central Registry:** Keeps track of all projects managed by AI OS.
2. **Project Profile:** Merges codebase details, schema definitions, deployment status, and issues.
3. **Architecture Mapping:** Constructs dependency maps, service connections, and module diagrams.
4. **Health Scorecard:** Calculates documentation quality, test coverage, and technical debt hours.
5. **Timeline History:** Merges commits, database migrations, and deployments into a historical timeline.
6. **Risk Engine:** Evaluates environmental configuration drift, test gaps, and database vulnerabilities.
7. **Reports:** Generates 7 comprehensive markdown reports under `docs/project/`.

---

## Quick Start

1. Auto-discover your workspace:
   ```bash
   aios project analyze .
   ```
2. Verify status and registered projects:
   ```bash
   aios project list
   aios project status
   ```
3. Compile all 7 architecture, health, risk, and timeline reports:
   ```bash
   aios project summary
   ```
   Reports will be output under `docs/project/`.
