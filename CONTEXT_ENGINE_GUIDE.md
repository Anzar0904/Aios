# Context Engine Guide

This document describes how the Context Engine tracks, updates, and persists user context within the AI OS Natural Language Operating System.

## 1. Overview
The Context Engine is responsible for identifying the background variables and objects that the user is currently working on or discussing. This enables "pronoun resolution" and allows the user to invoke commands like "Deploy it" or "Show details" without repeating name qualifiers.

## 2. Tracked Variables
The Context Engine maintains persistent keys in `.agent/context.json` for:
* **Current Project**: The active workspace project.
* **Current Workflow**: The active n8n automation flow under discussion.
* **Current Goal**: The personal or sprint goal currently targeted.
* **Current Research Topic**: The current academic or technical topic.
* **Current Agency Client**: The active CRM lead or corporate client.
* **Current Conversation**: The active interactive discussion session.

## 3. Pronoun Resolution Flow
When a user runs a query containing a pronoun (e.g. "it", "them", "that", "this"), the Context Engine resolves the reference using the active context:
1. **Analyze query**: Identify the domain of the action (e.g. "deploy" maps to workflows).
2. **Lookup context**: Fetch the corresponding tracked variable (e.g. `workflow = "lead_generation"`).
3. **Substitute reference**: Convert "deploy it" into "deploy lead_generation" before routing.

## 4. Usage
To view the current active context control panel, run:
```bash
aios context
```

To set a context value manually:
```bash
aios context set project AI_Tutor
```

To clear all context values:
```bash
aios context clear
```
