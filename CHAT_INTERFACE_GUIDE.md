# Chat Interface Guide

This document describes how to use the interactive Natural Language Chat Interface in AI OS.

## 1. Commands
The CLI supports two entrypoints for natural language operations:
1. `aios chat` - Enters the interactive conversational dashboard shell.
2. `aios ask <query>` - Executes a single natural language query or asks a context-aware question directly.

## 2. Interactive Chat Shell (`aios chat`)
Running `aios chat` launches the interactive command center.
Inside the shell, you can type:
* **Plain English Commands**: E.g. "show open github prs", "create a project named AI_Coach", "deploy workflow marketing".
* **Subsystem Queries**: E.g. "what projects do I have?", "list my goals".
* **Explanation Queries**:
  * "what are you doing?"
  * "why did you choose this?"
  * "explain the plan."
* **General Chat**: General questions (e.g. "how do I configure redis?") stream replies directly from the LLM model service.
* **Control Commands**:
  * `/exit` or `/quit` - Quit the session.
  * `/clear` - Clear the terminal.
  * `/status` - Audit system component health.
  * `/history` - View conversation sessions log.

## 3. Context & Execution Control
You can manage the active context variables during your chat session:
* E.g. type `"context set project CompilerOS"` to focus your active context on a specific project.
* Type `"execute deploy it"` to resolve the target workflow and execute the deploy steps.
