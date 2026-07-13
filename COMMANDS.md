# Personal AI OS Command Reference

This document is automatically generated from the Command Registry.

## Developer Commands

### `analyze dependencies`
- **Description**: Analyzes package and build configurations to detect dependency bloat and risks.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `analyze dependencies`

### `analyze repository`
- **Description**: Performs a detailed workspace analysis, detecting languages, frameworks, and architecture.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `analyze repository`

### `analyze todos`
- **Description**: Scans the workspace to aggregate, prioritize, and assess unresolved TODO/FIXME items.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `analyze todos`

### `detect code smells`
- **Description**: Scans the repository to identify code smells, long methods, or architectural anti-patterns.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `detect code smells`

### `detect dead code`
- **Description**: Scans files and imports to detect dead or obsolete code paths.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `detect dead code`

### `detect duplicate code`
- **Description**: Finds redundant or duplicated blocks of code across workspace files.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `detect duplicate code`

### `explain file`
- **Description**: Explains the purpose, key classes, and structure of a specific file.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `explain file core/src/aios/kernel.py`

### `explain stack trace`
- **Description**: Explains a system stack trace, pointing to exceptions and lines of failure.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `explain stack trace <error trace>`

### `generate commit message`
- **Description**: Generates a standard git commit message for the active changes.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: git
- **Example**: `generate commit message`

### `generate release notes`
- **Description**: Drafts release notes from recent git activities and commit summaries.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: git
- **Example**: `generate release notes`

### `investigate bug`
- **Description**: Investigates a bug report or error scenario, pinpointing potential origins.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `investigate bug <description>`

### `review architecture`
- **Description**: Reviews architectural patterns, separations of concerns, coupling, and SOLID compliance.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `review architecture`

### `review git changes`
- **Description**: Reviews active uncommitted git changes and provides insights.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: git
- **Example**: `review git changes`

### `review repository`
- **Description**: Performs a comprehensive code quality and structure review of the repository.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `review repository`

### `review security`
- **Description**: Performs a security audit of the workspace identifying potential vulnerabilities.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `review security`

### `review tests`
- **Description**: Reviews test infrastructure, unit test coverage, gaps, and quality.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `review tests`

### `suggest refactoring`
- **Description**: Suggests structural refactoring blueprints to improve code design.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `suggest refactoring`

### `summarize architecture`
- **Description**: Generates a high-level summary of the system architecture.
- **Category**: Developer
- **Required Agent**: developer_agent
- **Required Tools**: filesystem
- **Example**: `summarize architecture`

## Automation Commands

### `approve`
- **Description**: Approves the currently active action execution plan.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `approve`

### `execute`
- **Description**: Executes the approved steps in the active action execution plan.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `execute`

### `execution history`
- **Description**: Lists all persisted action execution plans.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `execution history`

### `plan`
- **Description**: Generates an execution plan for a multi-step action objective.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `plan write file test.txt content Hello`

### `reject`
- **Description**: Rejects and clears the currently active action execution plan.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `reject`

### `rollback`
- **Description**: Rolls back/reverts executed changes of a plan by ID.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `rollback <plan_id>`

### `run task`
- **Description**: Executes a multi-step engineering objective by planning and orchestrating commands.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `run task Review my repository and generate release notes`

### `task history`
- **Description**: Lists all persisted task executions.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `task history`

### `task resume`
- **Description**: Resumes the execution of a pending or failed task by ID.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `task resume <task_id>`

### `task status`
- **Description**: Displays the status of the last executed task.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `task status`

### `workflow clone`
- **Description**: Command to perform workflow clone action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow clone arguments`

### `workflow create`
- **Description**: Command to perform workflow create action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow create arguments`

### `workflow delete`
- **Description**: Command to perform workflow delete action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow delete arguments`

### `workflow edit`
- **Description**: Command to perform workflow edit action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow edit arguments`

### `workflow execute`
- **Description**: Command to perform workflow execute action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow execute arguments`

### `workflow explain`
- **Description**: Command to perform workflow explain action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow explain arguments`

### `workflow export`
- **Description**: Command to perform workflow export action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow export arguments`

### `workflow health`
- **Description**: Command to perform workflow health action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow health arguments`

### `workflow import`
- **Description**: Command to perform workflow import action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow import arguments`

### `workflow list`
- **Description**: Command to perform workflow list action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow list arguments`

### `workflow logs`
- **Description**: Command to perform workflow logs action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow logs arguments`

### `workflow monitor`
- **Description**: Command to perform workflow monitor action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow monitor arguments`

### `workflow optimize`
- **Description**: Command to perform workflow optimize action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow optimize arguments`

### `workflow search`
- **Description**: Command to perform workflow search action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow search arguments`

### `workflow stop`
- **Description**: Command to perform workflow stop action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow stop arguments`

### `workflow validate`
- **Description**: Command to perform workflow validate action on workflows.
- **Category**: Automation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workflow validate arguments`

## System Commands

### `system status`
- **Description**: Displays current kernel state and OS uptime.
- **Category**: System
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `system status`

## Memory Commands

### `remember`
- **Description**: Adds a fact or note to persistent workspace memory.
- **Category**: Memory
- **Required Agent**: mock_agent
- **Required Tools**: None
- **Example**: `remember this project is built in python`

## Conversation Commands

### `current conversation`
- **Description**: Displays active conversation metadata.
- **Category**: Conversation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `current conversation`

### `delete conversation`
- **Description**: Deletes a conversation.
- **Category**: Conversation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `delete conversation`

### `list conversations`
- **Description**: Lists all persisted conversations.
- **Category**: Conversation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `list conversations`

### `new conversation`
- **Description**: Creates and switches to a new conversation.
- **Category**: Conversation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `new conversation`

### `rename conversation`
- **Description**: Renames the active conversation.
- **Category**: Conversation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `rename conversation`

### `resume`
- **Description**: Resumes a specific conversation.
- **Category**: Conversation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `resume <id>`

### `resume conversation`
- **Description**: Resumes a specific conversation.
- **Category**: Conversation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `resume conversation <id>`

### `show history`
- **Description**: Shows the history and summary of the active conversation.
- **Category**: Conversation
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `show history`

## CLI Commands

### `approval approve`
- **Description**: Approve a request by request ID.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `approval approve [request_id]`

### `approval cancel`
- **Description**: Cancel a request by request ID.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `approval cancel [request_id]`

### `approval history`
- **Description**: Display the governance execution audit log history.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `approval history`

### `approval pending`
- **Description**: List pending governance decisions in the queue.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `approval pending`

### `approval policies`
- **Description**: Display configured scope policies mapping.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `approval policies`

### `approval preview`
- **Description**: Generate/display execution preview details for a request.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `approval preview [request_id]`

### `approval queue`
- **Description**: List all requests in the governance approval queue.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `approval queue`

### `approval reject`
- **Description**: Reject a request by request ID.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `approval reject [request_id]`

### `approval status`
- **Description**: Display current status of a request by request ID.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `approval status [request_id]`

### `brain`
- **Description**: Runs a multi-skill query or objective through the Brain orchestrator.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `brain clone repository Anzar0904/aios and get status`

### `brain explain`
- **Description**: Explains how the Brain would route and plan a given query.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `brain explain clone repository Anzar0904/aios`

### `brain status`
- **Description**: Displays the status and history of the Brain orchestrator.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `brain status`

### `brain trace`
- **Description**: Traces execution details of the last or specified workflow.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `brain trace wf_abcd`

### `business analytics`
- **Description**: Display active client counts, success rates and revenue.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `business analytics`

### `business clients`
- **Description**: List and filter registered agency clients database.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `business clients`

### `business leads`
- **Description**: List and review sales lead pipeline and scores.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `business leads`

### `business organizations`
- **Description**: List or manage multiple business agency profiles and teams.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `business organizations`

### `business projects`
- **Description**: View active portfolio projects linked to clients.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `business projects`

### `business proposals`
- **Description**: Display agency proposals and timeline estimates.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `business proposals`

### `business summary`
- **Description**: Compile business operations status and write reports.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `business summary`

### `business tasks`
- **Description**: List agency project tasks and milestones.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `business tasks`

### `business timeline`
- **Description**: Generate aggregated client timeline history.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `business timeline [client_id]`

### `business workflows`
- **Description**: Inspect client workflow ownership and n8n stats.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `business workflows`

### `career analyze`
- **Description**: Command to perform career analyze action on Career details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `career analyze arguments`

### `career applications`
- **Description**: Command to perform career applications action on Career details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `career applications arguments`

### `career cover-letter`
- **Description**: Command to perform career cover-letter action on Career details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `career cover-letter arguments`

### `career interview`
- **Description**: Command to perform career interview action on Career details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `career interview arguments`

### `career jobs`
- **Description**: Command to perform career jobs action on Career details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `career jobs arguments`

### `career optimize`
- **Description**: Command to perform career optimize action on Career details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `career optimize arguments`

### `career report`
- **Description**: Command to perform career report action on Career details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `career report arguments`

### `career resume`
- **Description**: Command to perform career resume action on Career details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `career resume arguments`

### `career roadmap`
- **Description**: Command to perform career roadmap action on Career details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `career roadmap arguments`

### `career score`
- **Description**: Command to perform career score action on Career details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `career score arguments`

### `career workflow`
- **Description**: Command to perform career workflow action on Career details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `career workflow arguments`

### `commands`
- **Description**: Lists all commands, optionally filtered by category.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `commands developer`

### `dashboard`
- **Description**: Display the systems status dashboard panel.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `dashboard`

### `diagnostics`
- **Description**: Display telemetry performance and resource metrics.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `diagnostics`

### `generate research report`
- **Description**: Generates a technical research report based on gathered source snippets.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `generate research report sandboxing in macOS`

### `goal add`
- **Description**: Command to perform goal add action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `goal add arguments`

### `goal list`
- **Description**: Command to perform goal list action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `goal list arguments`

### `goal update`
- **Description**: Command to perform goal update action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `goal update arguments`

### `help`
- **Description**: Displays general help or detailed documentation for a specific command.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `help analyze repository`

### `knowledge add`
- **Description**: Command to perform knowledge add action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `knowledge add arguments`

### `knowledge search`
- **Description**: Command to perform knowledge search action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `knowledge search arguments`

### `learning add`
- **Description**: Command to perform learning add action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `learning add arguments`

### `learning progress`
- **Description**: Command to perform learning progress action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `learning progress arguments`

### `portfolio add`
- **Description**: Command to perform portfolio add action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `portfolio add arguments`

### `portfolio list`
- **Description**: Command to perform portfolio list action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `portfolio list arguments`

### `preferences show`
- **Description**: Command to perform preferences show action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `preferences show arguments`

### `preferences update`
- **Description**: Command to perform preferences update action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `preferences update arguments`

### `profile create`
- **Description**: Command to perform profile create action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `profile create arguments`

### `profile delete`
- **Description**: Command to perform profile delete action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `profile delete arguments`

### `profile list`
- **Description**: Command to perform profile list action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `profile list arguments`

### `profile show`
- **Description**: Command to perform profile show action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `profile show arguments`

### `profile switch`
- **Description**: Command to perform profile switch action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `profile switch arguments`

### `profile update`
- **Description**: Command to perform profile update action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `profile update arguments`

### `project add`
- **Description**: Command to perform project add action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `project add arguments`

### `project analyze`
- **Description**: Auto-discover framework, package manager and config at path.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `project analyze [path]`

### `project architecture`
- **Description**: Retrieve project component service mappings and module maps.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `project architecture [project_id]`

### `project graph`
- **Description**: Query and display project knowledge graph node connections.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `project graph [project_id]`

### `project health`
- **Description**: Display health scorecard including coverage and technical debt.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `project health [project_id]`

### `project list`
- **Description**: List all registered projects under Project Intelligence.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `project list`

### `project memory`
- **Description**: Perform semantic lookup over design decisions and resolutions.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `project memory [project_id] [query]`

### `project risks`
- **Description**: Inspect coverage gaps, environment drift, and security risks.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `project risks [project_id]`

### `project status`
- **Description**: Display the active project ID and overall registry statistics.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `project status`

### `project summary`
- **Description**: Compile project profile summary and generate reports.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `project summary [project_id]`

### `project timeline`
- **Description**: Generate aggregated historical timeline events.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `project timeline [project_id]`

### `research topic`
- **Description**: Performs technical research on a topic and returns a cited markdown report.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `research topic LocalEventBus versus NATS`

### `resume compare`
- **Description**: Command to perform resume compare action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `resume compare arguments`

### `resume create`
- **Description**: Command to perform resume create action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `resume create arguments`

### `resume optimize`
- **Description**: Command to perform resume optimize action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `resume optimize arguments`

### `resume versions`
- **Description**: Command to perform resume versions action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `resume versions arguments`

### `runtime events`
- **Description**: Command to perform runtime events action on system runtime.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `runtime events arguments`

### `runtime health`
- **Description**: Command to perform runtime health action on system runtime.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `runtime health arguments`

### `runtime restart`
- **Description**: Command to perform runtime restart action on system runtime.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `runtime restart arguments`

### `runtime start`
- **Description**: Command to perform runtime start action on system runtime.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `runtime start arguments`

### `runtime status`
- **Description**: Command to perform runtime status action on system runtime.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `runtime status arguments`

### `runtime stop`
- **Description**: Command to perform runtime stop action on system runtime.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `runtime stop arguments`

### `runtime tasks`
- **Description**: Command to perform runtime tasks action on system runtime.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `runtime tasks arguments`

### `runtime watchers`
- **Description**: Command to perform runtime watchers action on system runtime.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `runtime watchers arguments`

### `search command`
- **Description**: Searches for commands matching a keyword.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `search command review`

### `search web`
- **Description**: Searches the web/local repositories for snippets related to the query.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `search web python git libraries`

### `session`
- **Description**: Display the CLI Session state details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `session`

### `setup`
- **Description**: Run interactive onboarding guide configurations.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `setup`

### `skills`
- **Description**: Lists all loaded skills.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `skills`

### `skills disable`
- **Description**: Disables an enabled skill and unregisters its commands.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `skills disable developer`

### `skills enable`
- **Description**: Enables a disabled skill and registers its commands.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `skills enable developer`

### `skills inspect`
- **Description**: Inspects metadata details of a specific skill.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `skills inspect developer`

### `skills list`
- **Description**: Lists all loaded skills.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `skills list`

### `skills reload`
- **Description**: Reloads skills and updates their metadata/commands.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `skills reload`

### `supabase auth`
- **Description**: Analyze authentication providers, OAuth configuration, and MFA settings.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `supabase auth`

### `supabase functions`
- **Description**: List edge functions, their status, and deploy readiness.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `supabase functions`

### `supabase login`
- **Description**: Log in to Supabase using personal access token or project URL + service role key.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `supabase login --token sb_pat_xxx`

### `supabase migrations`
- **Description**: View migration logs, drift detection status, and pending migrations.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `supabase migrations`

### `supabase projects`
- **Description**: List all discovered or configured Supabase projects.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `supabase projects`

### `supabase schema`
- **Description**: Explore the database schema of the active Supabase project.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `supabase schema`

### `supabase security`
- **Description**: Analyze security policies, public tables, and RLS state of the project.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `supabase security`

### `supabase status`
- **Description**: Show the current connection status to Supabase.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `supabase status`

### `supabase storage`
- **Description**: List storage buckets and check policies for public/private access.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `supabase storage`

### `supabase summary`
- **Description**: Generate a high-level summary of the connected project and write markdown reports.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `supabase summary`

### `template create`
- **Description**: Command to perform template create action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `template create arguments`

### `template list`
- **Description**: Command to perform template list action on personal details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `template list arguments`

### `vercel deployments`
- **Description**: Display recent deployments and rollback candidates.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `vercel deployments`

### `vercel domains`
- **Description**: List custom domains, verification state and SSL status.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `vercel domains`

### `vercel env`
- **Description**: List environment variables metadata (without exposing secrets).
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `vercel env`

### `vercel login`
- **Description**: Log in to Vercel using personal access token.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `vercel login --token vc_xxx`

### `vercel logs`
- **Description**: Retrieve build logs and AI failure diagnosis for a deployment.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `vercel logs <deployment_id>`

### `vercel projects`
- **Description**: List discovered Vercel projects.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `vercel projects`

### `vercel status`
- **Description**: Display connection state, active project, and scoped team.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `vercel status`

### `vercel summary`
- **Description**: Compile project health metrics and generate markdown reports.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `vercel summary`

### `workspace graph`
- **Description**: Generates and displays module/dependency graph representation using Mermaid notation.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workspace graph`

### `workspace refresh`
- **Description**: Forces invalidation of incremental caches and runs a complete clean workspace rescan.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workspace refresh`

### `workspace scan`
- **Description**: Scans the repository structures, dependencies, health metrics, and generates markdown documentation reports.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workspace scan`

### `workspace status`
- **Description**: Displays current branch status, uncommitted files, tracked test counts, and linters configuration.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workspace status`

### `workspace summary`
- **Description**: Displays the high-level architecture overview, components, tech stack, and health details.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `workspace summary`
