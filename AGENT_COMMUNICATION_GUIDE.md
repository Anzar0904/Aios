# Agent Communication Bus Guide

The **Agent Communication Bus** is the messaging backbone of AI OS. It allows specialized agents to pass structured messages, coordinate pipelines, request work, share outputs, escalate problems, and log collaborations.

## Core Features
1. **Message Routing**: Supports point-to-point requests, replies, and notifications between agents.
2. **Metadata Logs**: Records message payloads, types, related task IDs, and timestamps.
3. **Persistence**: Saves communication logs to `.agent/agent_communications.json`.
4. **Knowledge Graph Linking**: Inserts `COLLABORATES_WITH` relationships in the SQLite graph to index agent networks.

## Message Types
- `request`: An agent requests another agent to run a subtask (e.g. Software Engineer requests Test Engineer to run tests).
- `result`: An agent returns the successful results or artifacts of a request.
- `escalation`: An agent reports an error, block, or permission issue that needs parent agent or user attention.
- `info`: General telemetry or state sharing messages.

## Communication Schema

Communication logs are stored in `.agent/agent_communications.json`:

```json
[
  {
    "message_id": "b4a241ea-bf40-4550-9fb4-c0e267dc88bf",
    "sender_id": "agent_software",
    "recipient_id": "agent_test",
    "content": "Please review this implementation.",
    "message_type": "request",
    "task_id": null,
    "timestamp": 1784051043.976
  }
]
```

## Python API Usage

To send a message from one agent to another programmatically:

```python
from aios.registry import ServiceRegistry
from aios.services.agent_platform import AutonomousAgentPlatform

platform = ServiceRegistry._global_registry.get(AutonomousAgentPlatform)

# Send message
msg = platform.send_message(
    sender_id="agent_software",
    recipient_id="agent_test",
    content="The codebase is ready for integration tests.",
    message_type="request"
)

# Fetch all logs
messages = platform.get_messages()
print(f"Total communications logged: {len(messages)}")
```
