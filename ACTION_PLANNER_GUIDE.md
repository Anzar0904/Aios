# Action Planner Guide

This document describes how natural language requests are decomposed into structured action execution plans.

## 1. Overview
The Action Planner converts complex natural language goals into a sequence of executable steps. For example, if a user requests "Create a project and connect GitHub", the planner decomposes the request into distinct commands, establishing correct dependencies so that they run in the appropriate sequence.

## 2. Plan Structure
An action plan contains:
* **Plan ID**: A unique identifier for the execution instance.
* **Objective**: The user's original plain English query.
* **Steps**: A list of execution steps, each containing:
  * `step_id`: Unique identifier (e.g. `step_1`).
  * `action_type`: 'cli_command' or similar.
  * `target`: The exact CLI command argument list to run (e.g. `project create my_proj`).
  * `description`: Explanatory label.
  * `status`: 'pending', 'running', 'completed', or 'failed'.
  * `dependencies`: List of preceding step IDs.

## 3. Plan Generation
Plan generation uses a hybrid planner:
1. **Rule-Based Splitter**: Breaks queries containing clauses (split by "and", "then", etc.) and routes each clause independently.
2. **LLM Planner**: Generates structured step lists when the semantic intent involves complex dependency coordination.

## 4. Usage
To generate and view a plan without executing it, run:
```bash
aios plan "Create project AI_Tutor and deploy workflow lead_gen"
```

Output:
```
==================================================
Plan plan_1720980000: Create project AI_Tutor and deploy workflow lead_gen
==================================================
Step ID  Description                               Target Command                     Status      Dependencies
step_1   Run command: aios project create AI_Tutor aios project create AI_Tutor        pending
step_2   Run command: aios workflow deploy lead_gen aios workflow deploy lead_gen      pending     step_1
==================================================
```
