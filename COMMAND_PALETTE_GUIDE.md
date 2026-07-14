# Command Palette Guide

The **Command Palette** is a searchable command bar that allows users to quickly find and execute registered shell commands, workspace navigation paths, agent runs, and projects switches.

## Triggering the Command Palette

### 1. Interactive Command Center
Press `k` in the Command Center main menu.

### 2. General OS Chat Mode
Press `Ctrl+K`. This automatically clears the prompt line and overlays the Command Palette search prompt:

```
Search commands, projects, agents, workflows: status
```

## Search & Selection Logic

1. **Incremental Filter**: The palette filters registered commands, projects, agents, and workflows as the user type.
2. **Tab Selection**: Shows matched commands (e.g. `aios status`, `aios agent execute`).
3. **Execution**: Prompts the user to select one of the matches to execute in-process.

## Example Interactions

* **Inspect Health Status**:
  1. Trigger palette (`Ctrl+K`).
  2. Type `status`.
  3. Select `aios status` and press enter to render system health.

* **List Repositories**:
  1. Trigger palette (`Ctrl+K`).
  2. Type `repos`.
  3. Select `aios github repos` and press enter.
