# Task Delegation Engine Guide

The **Task Delegation Engine** controls how tasks are routed, divided, reassigned, and tracked throughout their lifecycle. It coordinates agent status transitions and links assignments directly to the Universal Knowledge Graph.

## Core Operations

### 1. Assign Task
Assigns a specific task to an agent, transitioning the agent's status to `busy` and linking the relationship in the Knowledge Graph with the `ASSIGNED_TO` type.

```python
platform.assign_task(task_id="task_123", agent_id="agent_software")
```

### 2. Reassign Task
Reassigns a task from an active agent to another agent, resetting the original agent's status to `idle` (if no other tasks are assigned to them) and setting the new agent's status to `busy`.

```python
platform.reassign_task(task_id="task_123", new_agent_id="agent_test")
```

### 3. Split Task
Decomposes a complex task into multiple subtasks, each with its own title, description, and dependencies, establishing a nested parent-child relationship in the Task Tree.

```python
subtasks = platform.split_task(
    task_id="task_main",
    subtasks_list=[
        {"title": "Research CRM schema", "description": "Formulate database definitions"},
        {"title": "Implement CRM schema", "description": "Write sqlite migrations", "dependencies": ["task_main_sub_1"]}
    ]
)
```

### 4. Merge Tasks
Combines multiple related tasks into a single target task, appending descriptions and results to reduce overall management overhead.

```python
platform.merge_tasks(task_ids=["task_sub_1", "task_sub_2"], target_task_id="task_main")
```

## Lifecycle States of a Task

```
  [ Pending ] 
       │      (assign_task)
       ▼
  [ Running ] ───────► (reassign_task) ──► [ Running (New Agent) ]
       │
       ├─────────────────────────┐
       ▼ (success)               ▼ (error / crash)
 [ Completed ]               [ Failed ]
```

- **Pending**: Task generated and added to the queue, but no active execution has started.
- **Running**: Assigned to an agent and currently being processed by the Execution Engine.
- **Completed**: Agent finished the task successfully. Results are persisted and linked.
- **Failed**: Task failed or timed out. An error message is logged and stored.

## CLI Usage

To manually assign a task to an agent:
```bash
aios agent assign <task_id> <agent_id>
```
For example:
```bash
aios agent assign task_crm_res_1784051048 agent_research
```
