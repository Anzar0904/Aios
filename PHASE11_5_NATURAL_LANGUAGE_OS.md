# Phase 11.5: Natural Language Operating System (NL OS)

This document provides a comprehensive overview of the design, architecture, and integration of the Natural Language Operating System (Phase 11.5) for AI OS.

## 1. Overview
The primary objective of the Natural Language Operating System (NL OS) is to enable users to interact with and control all subsystems of AI OS using plain English. Users are no longer required to remember syntax-heavy CLI commands. The system intelligently resolves intent, context, and entities to automatically execute the correct subsystem commands.

## 2. Core Architecture
The NL OS is structured into the following key layers:

```
                  +--------------------------------+
                  |      User English Input        |
                  +---------------+----------------+
                                  |
                                  v
                  +---------------+----------------+
                  |    Natural Language Router     |
                  +---------------+----------------+
                                  |
            +---------------------+---------------------+
            |                     |                     |
            v                     v                     v
+-----------+-----------+ +-------+-------+ +-----------+-----------+
|     Intent Engine     | | Context Engine| | Entity Extractor Engine|
+-----------+-----------+ +-------+-------+ +-----------+-----------+
            |                     |                     |
            +---------------------+---------------------+
                                  |
                                  v
                  +---------------+----------------+
                  |        Action Planner          |
                  +---------------+----------------+
                                  |
                                  v
                  +---------------+----------------+
                  |        Action Executor         |
                  +---------------+----------------+
                                  |
            +---------------------+---------------------+
            |                                           |
            v                                           v
+-----------+-----------+                   +-----------+-----------+
|    Knowledge Graph    |                   |    Learning Engine    |
+-----------------------+                   +-----------------------+
```

## 3. Subsystem Capabilities
The NL OS provides universal support across the following domains:
* **Project Intelligence**: Register, switch, query, and analyze projects.
* **Agency Intelligence**: Create leads, promote deals, draft proposals, and generate outreach plans.
* **Workflow Automation**: Deploy, activate, monitor, and troubleshoot n8n automation flows.
* **GitHub Integration**: List repositories, review open pull requests, check issues, and audit build states.
* **Research Hub**: Conduct literature searches, learn about topics, digest papers, and generate summaries.
* **Personal Intelligence**: Manage goals, tasks, calendars, streak tracking, and morning/weekly planners.
* **Documentation**: Generate and validate codebase documentation and architecture reviews.
* **System Control**: Query status, check uptime, run diagnostics, and manage sessions.

## 4. Subcommands
The CLI exposes these natural language control commands:
* `aios chat` - Enters the conversational natural language dashboard.
* `aios ask <question>` - Asks context-aware questions or routes actions in plain English.
* `aios intent <query>` - Inspects intent classification and confidence scores.
* `aios plan <query>` - Generates and views step-by-step action execution plans.
* `aios execute <query>` - Runs a step-by-step execution plan automatically.
* `aios context` - Displays or modifies the active context variables (e.g. current project, workflow, topic).
