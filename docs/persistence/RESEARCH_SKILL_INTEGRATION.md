# Research Skill Semantic Integration

## Overview
The Research Skill automatically catalogs technical search reports, source URLs, and citations in Qdrant to build a reusable reference repository for the system.

## Integration Architecture
At the end of a research session, the resulting detailed technical report is parsed and stored in the `research_memory` vector index.

### Trigger Hooks
- **Location**: `LocalResearchService.research` in [research_impl.py](file:///Users/anzarakhtar/aios/core/src/aios/services/research_impl.py#L305)
- **Target Collection**: `research_memory`

## Data Schema & Payload
```json
{
  "text": "Research Query: Explain EventBus\nReport: ...\nCitations: ...",
  "importance": 7.0,
  "tags": ["research", "report", "citations"],
  "timestamp": 1700000000.0,
  "status": "active"
}
```
