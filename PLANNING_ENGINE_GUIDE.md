# Planning Engine Guide

The **Planning Engine** converts abstract natural language goals into structured, execution-ready **Task Trees** containing specialized agent assignments, prerequisites, and detailed task descriptions.

## Decomposing Goals into Task Trees

When given a goal (e.g. "Build a CRM system"), the Planning Engine performs the following steps:

1. **Context Loading**: Fetches the active workspace, project specifications, and database structures.
2. **Capability Check**: Matches the requirements of the objective against the capability sets of registered agents.
3. **Dependency Mapping**: Identifies which tasks must finish before others can begin (e.g., code cannot be tested until it is written).
4. **Structured JSON Output**: Generates a set of tasks formatted as `MultiAgentTask` objects, linking dependencies to establish execution order.

## Planning Flow Chart

```
             ┌─────────────────────────┐
             │   User Goal / Request   │
             └────────────┬────────────┘
                          │
                          ▼
             ┌─────────────────────────┐
             │  LLM / Template Planner │
             └────────────┬────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
 ┌─────────────────────┐     ┌─────────────────────┐
 │ Task 1: Research    │     │ Task 2: Software    │
 │ Agent: Research     │     │ Agent: Software     │
 │ Deps: []            │     │ Deps: [Task 1]      │
 └──────────┬──────────┘     └──────────┬──────────┘
            │                           │
            └─────────────┬─────────────┘
                          ▼
             ┌─────────────────────────┐
             │ Task 3: Test            │
             │ Agent: Test             │
             │ Deps: [Task 2]          │
             └─────────────────────────┘
```

## Template Fallbacks

If the Model Service is unavailable, the Planning Engine uses built-in heuristic templates to formulate structural tasks:

- **CRM Objective Fallback**:
  1. **Research CRM Architectures**: Analyzes specifications and databases (`agent_research`).
  2. **Develop CRM Codebase**: Writes code and migrations (`agent_software`), depends on task 1.
  3. **Verify CRM with Tests**: Runs pytest validation suites (`agent_test`), depends on task 2.
  4. **Generate CRM Documentation**: Writes READMEs and API documentation (`agent_doc`), depends on task 3.

## Python API Usage

To generate a plan programmatically:

```python
from aios.registry import ServiceRegistry
from aios.services.agent_platform import AutonomousAgentPlatform

platform = ServiceRegistry._global_registry.get(AutonomousAgentPlatform)
tasks = platform.generate_plan("Build a customer relationship tracker")

for task in tasks:
    print(f"ID: {task.task_id} | Title: {task.title} | Agent: {task.assigned_agent}")
```
