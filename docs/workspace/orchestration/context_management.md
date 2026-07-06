# Context Window Management Spec
**Sprint 10 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define context selection algorithms, token optimization rules, and OmniRoute parameters.
* **Scope**: Governs prompt loaders, code compressors, and vector relevance filters.
* **Audience**: AI Prompt Engineers, Integration Engineers, and System Architects.
* **Related Documents**:
  * [docs/04_AI_MODEL_STRATEGY.md](file:///Users/anzarakhtar/aios/docs/04_AI_MODEL_STRATEGY.md) - Model selection and context bounds.
  * [workspace/integration_strategy.md](file:///Users/anzarakhtar/aios/docs/workspace/integration_strategy.md) - Semantic vector strategies.

---

## 1. OmniRoute Context Routing

Workspace files contain significant boilerplate code (imports, exports, variable setup), which can easily exceed LLM token limits when analyzing large projects. The **Context Management** module integrates with **OmniRoute** to dynamically optimize context windows:

```
[Agent Query]
      |
      v
[Relevance Scopes] ===> Retrieve top 10 symbol vectors from Qdrant
      |
      v
[Token Estimator] ===> Count raw tokens in target context
      |
      +---> Tokens < Limit: Inject raw code files.
      +---> Tokens > Limit: Apply Compression Pipeline.
      |
      v
[LLM Prompt Context]
```

---

## 2. Code Compression Pipeline

If the combined file context exceeds target token limits:
1. **Signature Extraction**: Strips method bodies, returning only class layouts, parameter signatures, and docstring headers.
2. **Comment Stripping**: Removes local comments and trims long docstrings.
3. **AST Pruning**: Filters out unused variables, private helpers, and import blocks.
4. **Relevance Filtering**: Uses Qdrant similarity scores to keep only the top 3 relevant method definitions in full, keeping surrounding methods as single-line signature definitions.

---

## 3. Dynamic Diff Injections

For tasks modifying active code, the context manager injects:
* **Active Git Diffs**: Staged and unstaged diff hunks are formatted as markdown code blocks.
* **Error Diagnostics**: Build and test diagnostics are injected as high-priority alert nodes at the top of the prompt, ensuring the model focuses on fixing active failures.
