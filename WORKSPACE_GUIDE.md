# Workspace Navigation Guide

AI OS coordinates multiple workspaces into one interface, allowing users to inspect projects, sales pipelines, academic research, source code repositories, automation workflows, and autonomous agent tasks.

## Pinned Workspaces

Navigate between workspaces by pressing their respective hotkeys in the Command Center menu:

### 1. Project Workspace (`p`)
* **Current Project**: Active workspace context folder name.
* **Goals**: High-level objectives and progress bars.
* **Tasks**: Outstanding backlog items.
* **Roadmap**: Sprint releases timeline.
* **Documentation**: Clickable list of markdown guides.

### 2. Agency Workspace (`a`)
* **Leads**: Qualified contacts and current pipeline stage.
* **Clients**: Active accounts and retainer metrics.
* **Meetings**: Calendar sync and agendas.
* **Proposals**: Generated proposals and review statuses.
* **Pipeline**: Expected revenue value.
* **Follow-Ups**: Pending follow-up alerts.

### 3. Research Workspace (`r`)
* **Active Research**: Active research queries and topics.
* **Findings**: Knowledge synthesized from sources.
* **Papers**: Ingested academic papers catalog.
* **Insights**: Extracted graph nodes and relationships.
* **Learning Trends**: Current learning progress and topic logs.

### 4. GitHub Workspace (`g`)
* **Repositories**: Tracked codebase repositories.
* **PRs**: Open pull requests and checks statuses.
* **Issues**: Open backlog issues.
* **Actions**: Telemetry on recent GitHub Action runs.
* **Releases**: Tagged releases version details.
* **Health**: Repository health percentage.

### 5. Workflow Workspace (`w`)
* **Active Workflows**: Deployments on the n8n runtime engine.
* **Deployments**: Version hashes and run statuses.
* **Executions**: Total run counts and histories.
* **Failures**: Failure logs and node-level crash details.
* **Templates**: Built-in automation templates.

### 6. Agent Workspace (`t`)
* **Agents**: Seeding statuses and metrics of the 7 core agents.
* **Current Tasks**: Active tasks assigned to agents.
* **Execution Queue**: Pending task priority queues.
* **Performance**: Task completion rate calculations.
* **Communication**: Collaboration logs.

---

## Workspace Subcommands CLI

You can boot directly into a specific workspace using the CLI command:
```bash
aios workspace <project|agency|research|github|workflow|agent>
```
For example:
```bash
aios workspace agency
```
This bypasses the main dashboard and launches the specified workspace view immediately.
