# Merge Conflict & Collision Resolution Spec
**Sprint 10 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define collision markers parsing, AST-level conflict mapping, and three-way merging strategies.
* **Scope**: Governs Git merge states, conflict markers, and code resolution models.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [workspace/codebase/ast_analysis.md](file:///Users/anzarakhtar/aios/docs/workspace/codebase/ast_analysis.md) - AST scopes.
  * [workspace/source_control/git_intelligence.md](file:///Users/anzarakhtar/aios/docs/workspace/source_control/git_intelligence.md) - Git execution.

---

## 1. Conflict Marker Parsing

During a merge or rebase operation, Git inserts standard conflict markers when automatic edits collide:
* **Conflict Blocks**:
  * `<<<<<<< HEAD` (Current changes block start)
  * `=======` (Divider between current and incoming modifications)
  * `>>>>>>> branch_name` (Incoming changes block end)

The **Merge Conflict Parser** reads conflicted files line-by-line, grouping these markers into structured conflict objects containing target line numbers, current texts, and incoming modifications.

---

## 2. AST-Level Symbol Mapping

Unlike simple text diff tools, the AI OS maps conflict blocks directly to code structures:
1. **Identify Conflict Offsets**: Extract line ranges for conflicted blocks (e.g. Lines 120–135).
2. **Resolve Symbol Scopes**: Cross-reference the lines with the `codebase_symbols` SQL table.
3. **Determine Collision Targets**: Map conflicts to specific methods or classes:
   ```
   [Conflict Mapped Scope]
   File: core/src/aios/services/knowledge_hub_impl.py
   Target: class LocalKnowledgeHub -> def sync_document
   Collision: Current block modified return types; Incoming block changed parameter definitions.
   ```
   This gives the AI reasoning engine precise semantic context for resolving the conflict.

---

## 3. Automated Resolution Strategies

To resolve conflicts safely:
1. **Semantic Three-Way Merge**: If changes occur in disjoint methods or functions in the same file, the engine automatically merges them.
2. **User Prompts**: If changes collide inside the same AST block:
   * Prompt the user via the REPL showing side-by-side symbol-level diffs.
   * Provide options: `Keep Current (HEAD)`, `Accept Incoming`, or `Interactive Merge`.
3. **Rollback Safety**: If resolving conflicts breaks local tests or compilation, the engine issues a rollback (`git merge --abort` or `git rebase --abort`) to prevent workspace corruption.
