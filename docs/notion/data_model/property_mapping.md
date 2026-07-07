# Notion Intelligence — Property Mapping Specification
**Sprint 9 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define serialization and deserialization helpers for individual cell properties inside database rows and page configurations.
* **Scope**: Dictates the converter classes and property encoder/decoder logics.
* **Audience**: Backend Engineers, Integration Developers, and AI coding agents.
* **Related Documents**:
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - Database properties mapping catalog.
  * [notion/data_model/database_model.md](file:///Users/anzarakhtar/aios/docs/notion/data_model/database_model.md) - Database and row models.

---

## 1. Property Mapping Service

Because Notion's API properties contain nested structures, the Personal AI OS uses a dedicated utility class, `NotionPropertyMapper`, to translate property values between Python types and Notion JSON payloads.

```
       [Python Raw Values]
         /      |      \
        v       v       v
      (str)  (datetime) (bool)
        \       |       /
         v      v      v
      [NotionPropertyMapper]
         /      |      \
        v       v       v
   [RichText] [Date] [Checkbox]
```

---

## 2. Python Class Implementations

The mapping logic is encapsulated under `aios.providers.notion.mapper`:

```python
from typing import Dict, Any, List, Optional
from datetime import datetime

class NotionPropertyMapper:
    @staticmethod
    def deserialize_property(prop_data: Dict[str, Any]) -> Any:
        """Translate a Notion property JSON block into a clean Python type."""
        prop_type = prop_data.get("type")
        
        if prop_type == "title":
            title_list = prop_data.get("title", [])
            return "".join([t.get("plain_text", "") for t in title_list])
            
        elif prop_type == "rich_text":
            text_list = prop_data.get("rich_text", [])
            return "".join([t.get("plain_text", "") for t in text_list])
            
        elif prop_type == "select":
            select_obj = prop_data.get("select")
            return select_obj.get("name") if select_obj else None
            
        elif prop_type == "multi_select":
            items = prop_data.get("multi_select", [])
            return [item.get("name") for item in items]
            
        elif prop_type == "date":
            date_obj = prop_data.get("date")
            if not date_obj:
                return None
            start_str = date_obj.get("start")
            end_str = date_obj.get("end")
            start = datetime.fromisoformat(start_str.replace("Z", "+00:00")) if start_str else None
            end = datetime.fromisoformat(end_str.replace("Z", "+00:00")) if end_str else None
            return (start, end) if end else start
            
        elif prop_type == "checkbox":
            return prop_data.get("checkbox", False)
            
        elif prop_type == "number":
            return prop_data.get("number")
            
        elif prop_type == "relation":
            relations = prop_data.get("relation", [])
            return [rel.get("id") for rel in relations]
            
        elif prop_type == "people":
            people = prop_data.get("people", [])
            return [person.get("id") for person in people]
            
        return prop_data  # Fallback for unhandled types (e.g. formula, rollup)

    @staticmethod
    def serialize_property(prop_type: str, value: Any) -> Dict[str, Any]:
        """Convert a standard Python value into a Notion-compliant property payload."""
        if prop_type == "title":
            return {"title": [{"text": {"content": str(value)}}]}
            
        elif prop_type == "rich_text":
            return {"rich_text": [{"text": {"content": str(value)}}]}
            
        elif prop_type == "select":
            return {"select": {"name": str(value)}} if value else {"select": None}
            
        elif prop_type == "multi_select":
            return {"multi_select": [{"name": str(v)} for v in value]}
            
        elif prop_type == "date":
            if not value:
                return {"date": None}
            if isinstance(value, tuple) and len(value) == 2:
                # Range tuple
                start, end = value
                return {
                    "date": {
                        "start": start.isoformat(),
                        "end": end.isoformat()
                    }
                }
            return {"date": {"start": value.isoformat()}}
            
        elif prop_type == "checkbox":
            return {"checkbox": bool(value)}
            
        elif prop_type == "number":
            return {"number": value} if value is not None else {"number": None}
            
        raise ValueError(f"Serialization for property type '{prop_type}' is not supported.")
```
