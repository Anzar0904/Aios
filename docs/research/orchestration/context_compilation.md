# Context Compilation & OmniRoute Spec
**Sprint 11 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define context compilation algorithms, token optimization rules, and OmniRoute parameters for research.
* **Scope**: Governs prompt loaders, text compressors, and vector relevance filters.
* **Audience**: AI Prompt Engineers, Integration Engineers, and System Architects.
* **Related Documents**:
  * [workspace/orchestration/context_management.md](file:///Users/anzarakhtar/aios/docs/workspace/orchestration/context_management.md) - Workspace context.
  * [research/memory/retrieval_optimization.md](file:///Users/anzarakhtar/aios/docs/research/memory/retrieval_optimization.md) - Retrieval options.

---

## 1. OmniRoute Context Routing

Research documents (such as academic publications or IETF specs) can be extremely long, easily exceeding LLM token limits when analyzing complex topics. The **Context Compilation** module integrates with **OmniRoute** to optimize prompt context windows:

```
[Agent Query]
      |
      v
[Relevance Scopes] ===> Retrieve top 10 concept vectors from Qdrant
      |
      v
[Token Estimator] ===> Count raw tokens in target context
      |
      +---> Tokens < Limit: Inject raw markdown document.
      +---> Tokens > Limit: Apply Compression Pipeline.
      |
      v
[LLM Prompt Context]
```

---

## 2. Document Compression Pipeline

If the combined research context exceeds target token limits:
1. **Fact Summarization**: Replaces full document text with the structured summary generated during parsing.
2. **Citations Stripping**: Removes verbose references and trims long list items.
3. **Relevance Filtering**: Uses Qdrant similarity scores to keep only the top 3 relevant sections, keeping surrounding sections as single-line summaries.
4. **Pruning**: Excludes unverified or low-confidence facts from the context window.
