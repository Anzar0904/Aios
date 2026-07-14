# Agent Memory Guide

The **Agent Memory** system allows agents to persist details about their operations, achievements, failures, and lessons learned. This gives agents historical context and helps them avoid repeating mistakes.

## Core Features
1. **Execution Logging**: Records metadata for every executed task (success status, output data, runtime stamps).
2. **Lessons Learned**: Extracts feedback (e.g. why a test suite crashed, what database schemas worked best) and logs them into a searchable ledger.
3. **Persistence**: State is written to `.agent/agent_memory.json` in the workspace root.
4. **Agent Profile Association**: Links memory IDs directly to the agent's profile descriptors for quick lookup.

## Memory Ledger Schema

Memory logs are stored in `.agent/agent_memory.json` as a list of dictionary records:

```json
[
  {
    "task_id": "task_crm_soft_1784051048",
    "title": "Develop CRM Codebase",
    "description": "Develop backend controllers, frontend UI mockups, and database migrations.",
    "success": true,
    "results": "[Software Engineer Agent] Accomplished task 'Develop CRM Codebase' successfully.",
    "assigned_agent": "agent_software",
    "timestamp": 1784051048.225,
    "lesson_learned": "Successfully completed 'Develop CRM Codebase'. Derived result: [Software Engineer Agent] Accomplished task..."
  }
]
```

## Python API Usage

To fetch the memory logs of a specific agent:

```python
from aios.registry import ServiceRegistry
from aios.services.agent_platform import AutonomousAgentPlatform

platform = ServiceRegistry._global_registry.get(AutonomousAgentPlatform)
memories = platform.get_agent_memory("agent_software")

for entry in memories:
    print(f"Task: {entry['title']} | Success: {entry['success']}")
    print(f"Lesson Learned: {entry['lesson_learned']}\n")
```

## CLI Usage

To inspect the memory ledger of an agent from the terminal:

```bash
aios agent memory <agent_id>
```
For example:
```bash
aios agent memory agent_software
```
This prints a clean table displaying tasks, status, and the lessons learned.
