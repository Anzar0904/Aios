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

## Career Commands

### `analyze job`
- **Description**: Performs detailed job description analysis.
- **Category**: Career
- **Required Agent**: career_agent
- **Required Tools**: filesystem
- **Example**: `analyze job job.pdf`

### `ats score`
- **Description**: Evaluates ATS compliance and matches scoring requirements.
- **Category**: Career
- **Required Agent**: career_agent
- **Required Tools**: filesystem
- **Example**: `ats score resume.pdf job.pdf`

### `cover letter`
- **Description**: Drafts a cover letter matching resume to job description.
- **Category**: Career
- **Required Agent**: career_agent
- **Required Tools**: filesystem
- **Example**: `cover letter resume.pdf job.pdf`

### `tailor resume`
- **Description**: Tailors a resume matching Qualifications against job descriptions.
- **Category**: Career
- **Required Agent**: career_agent
- **Required Tools**: filesystem
- **Example**: `tailor resume resume.pdf job.pdf`

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

### `commands`
- **Description**: Lists all commands, optionally filtered by category.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `commands developer`

### `help`
- **Description**: Displays general help or detailed documentation for a specific command.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `help analyze repository`

### `search command`
- **Description**: Searches for commands matching a keyword.
- **Category**: CLI
- **Required Agent**: None
- **Required Tools**: None
- **Example**: `search command review`

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
