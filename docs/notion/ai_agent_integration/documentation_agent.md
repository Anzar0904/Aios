# Notion Intelligence — Documentation Agent Integration
**Sprint 9 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the Documentation Agent's workspace triggers, API schema update methods, and documentation sync templates.
* **Scope**: Governs Python document parsers, release log compilers, and markdown page generators.
* **Audience**: Technical Writers, Integration Developers, and AI coding agents.
* **Related Documents**:
  * [notion/data_model/block_model.md](file:///Users/anzarakhtar/aios/docs/notion/data_model/block_model.md) - Block parser conversions.
  * [notion/ai_agent_integration/agent_integration.md](file:///Users/anzarakhtar/aios/docs/notion/ai_agent_integration/agent_integration.md) - Context routing rules.

---

## 1. Documentation Agent Execution Scope

The **Documentation Agent** keeps the project's external wiki in sync with the codebase. When the agent detects local code changes or new releases, it updates the corresponding pages on Notion.

```
 [Local Git Commit / Release] ===> Spawns Documentation Agent
                                          |
                                [Parse Code Modules] ===> Extract API signatures & docstrings
                                          |
                                 [Fetch Wiki Page] ===> Pull current page from Notion
                                          |
                               [Compile Release Diffs]
                                          |
                              [Update Notion Page AST] ===> Patch modified blocks
```

---

## 2. API Wiki Template Specification

When pushing API reference changes to Notion, the Documentation Agent structures the technical documentation using a standardized format:

```markdown
# [Module Name] API Reference
**Version**: [Version Number] · **Last Verified**: [Commit Hash]

---

> [!NOTE]
> This page is maintained automatically by the Documentation Agent.
> Manual edits to block tables will be overwritten during the next release cycle.

## 1. Interface Class: [ClassName]
[Describe the class responsibility...]

| Method Signature | Input Parameters | Output Type | Description |
|------------------|------------------|-------------|-------------|
| `def method_a()` | `param: type` | `return_type`| [Details...] |

## 2. Module Dependencies
[Diagram or list showing imports boundaries...]
```

---

## 3. Inline Block Patching Sequence

To avoid overwriting custom comments or notes added to Notion wiki pages by human users, the Documentation Agent uses **Targeted Block Patching**:
1. Retrieve the block AST children list for the wiki page.
2. Locate the specific code block or table block tagged with the metadata indicator `[DOC_AGENT_SECTION]`.
3. Generate the updated API text table block payload.
4. Issue a `PATCH` request to update only that block ID, leaving surrounding heading and discussion blocks untouched.
   ```python
   # Patch only the target API table block to avoid overwriting surrounding context
   notion_client.patch_block(
       block_id=target_block_id,
       payload={
           "type": "table",
           "table": updated_table_data
       }
   )
   ```
