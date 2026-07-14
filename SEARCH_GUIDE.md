# Universal Search Guide

The **Universal Search** engine provides search capability across all projects, tasks, workflows, documents, clients, meetings, and agents.

## Search Targets

Universal Search queries scan the following entities:

1. **Projects**: Active workspace context names and properties.
2. **Tasks**: Backlog and active multi-agent pipeline tasks.
3. **Workflows**: n8n automation deployments and templates.
4. **Research**: Ingested papers, knowledge graph nodes, and learning trends.
5. **GitHub**: Pull requests, issues, commits, and releases.
6. **Clients & Meetings**: CRM records, customer retainers, and calendars.
7. **Documents & Notes**: Architectural diagrams, release notes, and markdown guides.
8. **Agents**: Registered core and custom agents and capabilities.

## Execution Options

### 1. Interactive Command Center Mode
Press `s` in the Command Center main menu. You will be prompted to enter a search term:

```
Universal Search Query: Wayne
```

This immediately displays matching records in a structured table.

### 2. Direct CLI Command Mode
Run the `search` subcommand directly from your terminal:

```bash
aios search <query>
```
For example:
```bash
aios search Wayne
```

This outputs a summary table listing entity types, matched names, and descriptions.
