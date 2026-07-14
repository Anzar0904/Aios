# Agent Registry Guide

The **Agent Registry** is the central component responsible for cataloging, initializing, and tracking all agents in the AI OS ecosystem.

## Core Features
1. **Cataloging & Metadata**: Stores Agent ID, Name, Role, Capabilities, Status (`idle`, `busy`, `offline`), Assigned Tasks, Performance Metrics, and Memory references.
2. **Persistence**: Saves state information to `.agent/agents.json` inside the workspace root.
3. **Knowledge Graph Sync**: Automatically registers the agent's definition and capabilities to the SQLite Graph database.

## Registry Storage Schema

The registry state is stored in `.agent/agents.json` as a dictionary of `AgentDescriptor` records:

```json
{
  "softwareengineer": {
    "agent_id": "agent_software",
    "name": "SoftwareEngineer",
    "role": "Software Engineer",
    "capabilities": [
      "coding",
      "architecture",
      "refactoring",
      "feature_development",
      "repository_updates"
    ],
    "status": "idle",
    "assigned_tasks": [],
    "performance_metrics": {
      "success_rate": 1.0,
      "tasks_completed": 0,
      "failures": 0
    },
    "memory_references": []
  }
}
```

## The 7 Core Specialized Agents

1. **Software Engineer Agent** (`agent_software`): Coding, Architecture, Refactoring, Feature Dev, Repo Updates.
2. **Test Engineer Agent** (`agent_test`): Testing, Validation, Regression, CI Verification, Bug Reproduction.
3. **Documentation Engineer Agent** (`agent_doc`): README, Architecture, API, Guides, KB Updates.
4. **Research Engineer Agent** (`agent_research`): Paper analysis, Repo analysis, Synthesis, Tech recommendations.
5. **Agency Engineer Agent** (`agent_agency`): CRM operations, Leads management, Proposals, Client tracking.
6. **Automation Engineer Agent** (`agent_automation`): Workflow generation, deployment, monitoring, repair, optimization.
7. **Integration Engineer Agent** (`agent_integration`): GitHub, Notion, n8n, Supabase, Calendar, Email, External Services.

## Python API Usage

To register a custom agent programmatically in python:

```python
from aios.registry import ServiceRegistry
from aios.services.agent_platform import AutonomousAgentPlatform
from aios.services.agent import Agent

class CustomAgent(Agent):
    @property
    def name(self): return "MyCustomAgent"
    # ... implement execute()

platform = ServiceRegistry._global_registry.get(AutonomousAgentPlatform)
platform.register_agent(
    agent=CustomAgent(),
    role="Specialized Helper",
    capabilities=["optimization", "formatting"]
)
```

## CLI Usage

To view all registered agents and their current capabilities:

```bash
aios agent list
```
