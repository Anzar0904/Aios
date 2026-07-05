# Documentation Engine Semantic Integration

## Overview
The Documentation Engine indexes architecture documents, PRDs, engineering guidelines, and specifications to ensure they can be semantically retrieved by agents and query services.

## Integration Architecture
Registering new artifacts in the Documentation Service automatically schedules them for vector indexing in Qdrant.

### Trigger Hooks
- **Location**: `DocumentationService.register_artifact` in [documentation_intelligence_impl.py](file:///Users/anzarakhtar/aios/core/src/aios/services/documentation_intelligence_impl.py#L312)
- **Target Collection**: `documentation_memory`

## Data Schema & Payload
```json
{
  "text": "Documentation Artifact: [spec] Title: Semantic Memory Spec...",
  "importance": 9.0,
  "tags": ["documentation", "spec", "architecture"],
  "timestamp": 1700000000.0,
  "status": "active"
}
```
