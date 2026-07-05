# Context Service Semantic Integration

## Overview
The Context Service acts as the central query coordinator, retrieving semantic memories from all subsystems to construct rich prompts for the model routing and execution pipelines.

## Integration Architecture
When an enriched context query is processed, the Context Service queries Qdrant collections in parallel to gather relevant workspace, conversation, research, engineering, and documentation memories.

### Processing Pipeline
- **Method**: `LocalContextService.build_enriched_context()` in [context_impl.py](file:///Users/anzarakhtar/aios/core/src/aios/services/context_impl.py#L84)
- **Search Scope**: Queries `workspace_memory`, `conversation_memory`, `engineering_memory`, `research_memory`, and `documentation_memory`.
- **Deduplication & Budgeting**: Ranks and assembles candidates up to the token budget.
