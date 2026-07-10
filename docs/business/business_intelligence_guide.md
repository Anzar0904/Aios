# Business Intelligence Guide

Business Intelligence is the operational command center of AI OS, enabling it to manage an AI Automation Agency. It unifies clients, project portfolios, workflows, proposals, and agency analytics.

---

## Capabilities

1. **Organization Profiles:** Manage multiple agency companies, team roles, and permissions.
2. **Client Registry:** Maintain client contact database, tags, and communication history.
3. **Lead Pipeline:** Score and track sales opportunities from discovery to conversion.
4. **Project Portfolio:** Connect client accounts automatically to technical Project Intelligence models.
5. **Proposal Engine:** Draft, version, and manage project scopes, deliverables, timelines, and budgets.
6. **Workflow Ownership:** Map active n8n workflows and runtime success rates to their respective client accounts.
7. **Task Backlog:** Organizes milestones, priorities, dependencies, and deadlines.
8. **Operational Reports:** Compiles 6 operational reports under `docs/business/`.

---

## Quick Start

1. Display your client registry and lead pipeline:
   ```bash
   aios business clients
   aios business leads
   ```
2. Verify active project portfolios and workflow allocations:
   ```bash
   aios business projects
   aios business workflows
   ```
3. Compile all operational reports:
   ```bash
   aios business summary
   ```
   Reports will be output under `docs/business/`.
