# Automation Engine Semantic Integration

## Overview
The Automation Engine indexes automated job descriptions, execution session workflows, and execution summaries to build an operations knowledge-base.

## Integration Architecture
Completing automation runs or registering new workflow structures triggers Qdrant indexing.

### Trigger Hooks
- **Location**: `LocalAutomationService.run_session` in [automation_impl.py](file:///Users/anzarakhtar/aios/core/src/aios/services/automation_impl.py#L420)
- **Target Collection**: `automation_memory`

## Data Schema & Payload
```json
{
  "text": "Automation Session Run [id_123] status: success\nSteps: ...",
  "importance": 6.0,
  "tags": ["automation", "session", "run_report"],
  "timestamp": 1700000000.0,
  "status": "active"
}
```
