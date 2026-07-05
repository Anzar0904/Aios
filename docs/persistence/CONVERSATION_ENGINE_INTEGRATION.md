# Conversation Engine Semantic Integration

## Overview
The Conversation Engine automatically indexes message exchanges, summary dialogues, decisions, and action items in Qdrant to ensure that the context of previous user queries is preserved across sessions.

## Integration Architecture
Message additions and routine summarizations in the Conversation Engine trigger Qdrant indexing hooks.

### Trigger Hooks
- **Location**: `ConversationManager.add_message` in [manager.py](file:///Users/anzarakhtar/aios/core/src/aios/services/conversation/manager.py#L90)
- **Location**: `ConversationManager.summarize_if_needed` in [manager.py](file:///Users/anzarakhtar/aios/core/src/aios/services/conversation/manager.py#L225)
- **Target Collection**: `conversation_memory`

## Data Schema & Payload
```json
{
  "text": "Conversation [Test Title] Msg: USER: How do I query the database?",
  "importance": 6.0,
  "tags": ["conversation", "user", "dialogue"],
  "timestamp": 1700000000.0,
  "status": "active"
}
```
