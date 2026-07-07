# Notion Intelligence — Block Model Specification
**Sprint 9 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the Block representations, AST structure definitions, text parsing, and markdown translation systems.
* **Scope**: Governs Python block models, AST parsing engines, and markdown builders.
* **Audience**: Backend Developers, Integration Engineers, and AI coding agents.
* **Related Documents**:
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - Block AST and markdown translation overview.
  * [notion/integration_strategy.md](file:///Users/anzarakhtar/aios/docs/notion/integration_strategy.md) - Semantic vector indexing strategies.

---

## 1. Block AST Hierarchy

Notion pages represent content using blocks. The Personal AI OS parses block children recursively and compiles them into a tree hierarchy:

```
               [NotionPage]
                    |
                    v
             [BlockTreeRoot]
              /      |      \
             v       v       v
         [Heading1] [Paragraph] [ListBlock]
                                  /     \
                                 v       v
                            [ListItem] [ListItem]
```

---

## 2. Python Class Interfaces

The block definitions live under `aios.providers.notion.models.block`:

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class NotionBlock:
    block_id: str
    type: str  # e.g., 'paragraph', 'heading_1', 'code', 'to_do', 'bulleted_list_item'
    created_at: datetime
    updated_at: datetime
    has_children: bool
    content_payload: Dict[str, Any] = field(default_factory=dict)
    children: List["NotionBlock"] = field(default_factory=list)

    @classmethod
    def from_notion_json(cls, data: Dict[str, Any]) -> "NotionBlock":
        """Parse raw Notion block JSON into a typed block instance."""
        block_type = data["type"]
        return cls(
            block_id=data["id"],
            type=block_type,
            created_at=datetime.fromisoformat(data["created_time"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["last_edited_time"].replace("Z", "+00:00")),
            has_children=data.get("has_children", False),
            content_payload=data.get(block_type, {})
        )
```

---

## 3. Markdown Translation & AST Compiler

The `NotionBlockCompiler` compiles block trees into formatted Markdown text, and parses Markdown files back into block mutation requests.

```python
class NotionBlockCompiler:
    @staticmethod
    def block_to_markdown(block: NotionBlock, indent_level: int = 0) -> str:
        """Translate a single block node and its nested children to Markdown."""
        indent = "  " * indent_level
        type_handlers = {
            "paragraph": lambda b: NotionBlockCompiler._compile_paragraph(b),
            "heading_1": lambda b: f"\n# {NotionBlockCompiler._get_rich_text(b)}\n",
            "heading_2": lambda b: f"\n## {NotionBlockCompiler._get_rich_text(b)}\n",
            "heading_3": lambda b: f"\n### {NotionBlockCompiler._get_rich_text(b)}\n",
            "bulleted_list_item": lambda b: f"* {NotionBlockCompiler._get_rich_text(b)}",
            "numbered_list_item": lambda b: f"1. {NotionBlockCompiler._get_rich_text(b)}",
            "to_do": lambda b: f"- [{'x' if b.content_payload.get('checked') else ' '}] {NotionBlockCompiler._get_rich_text(b)}",
            "code": lambda b: f"\n```{b.content_payload.get('language', 'text')}\n{NotionBlockCompiler._get_code_text(b)}\n```\n",
            "quote": lambda b: f"\n> {NotionBlockCompiler._get_rich_text(b)}\n",
            "callout": lambda b: f"\n> [!NOTE]\n> {NotionBlockCompiler._get_rich_text(b)}\n"
        }

        handler = type_handlers.get(block.type)
        if not handler:
            return ""  # Ignore unsupported block types (e.g. breadcrumb, dividers)

        base_text = f"{indent}{handler(block)}\n"
        
        # Recursively compile children
        children_text = ""
        for child in block.children:
            children_text += NotionBlockCompiler.block_to_markdown(child, indent_level + 1)
            
        return base_text + children_text

    @staticmethod
    def _get_rich_text(block: NotionBlock) -> str:
        """Extract plain text from standard Notion rich_text structures."""
        rich_text_list = block.content_payload.get("rich_text", [])
        return "".join([t.get("plain_text", "") for t in rich_text_list])

    @staticmethod
    def _get_code_text(block: NotionBlock) -> str:
        """Extract plain text from code block rich_text arrays."""
        rich_text_list = block.content_payload.get("rich_text", [])
        return "".join([t.get("plain_text", "") for t in rich_text_list])
```

---

## 4. Compilation Limits
To avoid timeouts, the parser handles recursion up to **10 levels deep**. Pages exceeding this recursion limit are truncated, and a warning is logged in the system debugger.
