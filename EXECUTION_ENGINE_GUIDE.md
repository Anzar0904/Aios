# Execution Engine Guide

The **Execution Engine** is responsible for carrying out planned tasks in the correct order, resolving dependencies, invoking specialized agents, logging results, updating metrics, and updating the Knowledge Graph.

## Execution Models

1. **Single-Agent Execution**: Directly runs an isolated task utilizing the assigned agent.
2. **Multi-Agent Execution**: Performs topological sorting on a list of tasks, routing run blocks dynamically based on prerequisite task completions.
3. **Sequential Execution**: Sequentially runs tasks where each stage depends on the output of the prior stage (e.g. Research -> Code -> Test -> Doc).
4. **Parallel Execution** (Planned): Executes independent sibling tasks concurrently to speed up deployment.

## Execution Sequence & Topological Sort

The engine executes tasks in dependency order. If Task B depends on Task A, the engine blocks Task B until Task A succeeds:

```
[Start] ──► [Filter Runnable Tasks (Prerequisites Met)] 
                 │
                 ▼
          [Execute Task (Agent Context -> LLM/Fallback)]
                 │
                 ▼
          [Store Result & Record Memory]
                 │
                 ▼
          [Update Agent Performance Metrics]
                 │
                 ▼
   ┌──────[More Tasks left?]
   │             │ Yes
   │             ▼
   │      [Next Iteration]
   │
   └─────► No ──► [Finished]
```

## Python API Usage

To trigger the execution of a planned list of tasks:

```python
from aios.registry import ServiceRegistry
from aios.services.agent_platform import AutonomousAgentPlatform

platform = ServiceRegistry._global_registry.get(AutonomousAgentPlatform)
tasks = platform.generate_plan("Research and build a local database cache")

# This automatically executes tasks according to their dependency topology
success = platform.execute_plan(tasks)
if success:
    print("All tasks completed successfully!")
```

## Dashboard Overview

To see active execution tasks, queue pipelines, and progress, open the dashboard via CLI:

```bash
aios agents
```
This shows running, completed, and pending tasks in real-time.
