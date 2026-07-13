# ruff: noqa: F403, F405, E501, N802, E402, N806, B007
import json
import logging
from typing import Any, Dict

from aios.services.persistence import *

logger = logging.getLogger(__name__)


def format_query(query: str, provider_name: str) -> str:
    """Helper to convert SQL query positional markers to Postgres formats dynamically."""
    if provider_name == "postgresql":
        import re
        # Convert INSERT OR REPLACE INTO table (cols) VALUES (vals) to ON CONFLICT (id) DO UPDATE SET
        match = re.match(r"INSERT\s+OR\s+REPLACE\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)", query, re.IGNORECASE)
        if match:
            table_name = match.group(1)
            cols_str = match.group(2)
            vals_str = match.group(3)
            cols = [c.strip() for c in cols_str.split(",")]
            update_clause = ", ".join([f"{col}=EXCLUDED.{col}" for col in cols if col != "id"])
            query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({vals_str}) ON CONFLICT (id) DO UPDATE SET {update_clause}"
        return query.replace("?", "%s")
    return query


def serialize_val(val: Any) -> str:
    if isinstance(val, PersistenceResult):
        return json.dumps(
            {
                "__type__": "PersistenceResult",
                "status": val.status.value,
                "message": val.message,
                "error_code": val.error_code,
                "diagnostics": val.diagnostics,
                "retryable": val.retryable,
                "provider": val.provider,
                "latency": val.latency,
                "operation_id": val.operation_id,
                "timestamp": val.timestamp,
                "repository": val.repository,
                "payload": val.payload,
            }
        )
    return json.dumps({"__type__": "raw", "value": val})


def deserialize_val(s: str) -> Any:
    d = json.loads(s)
    if isinstance(d, dict) and d.get("__type__") == "PersistenceResult":
        from aios.services.persistence import PersistenceStatus

        return PersistenceResult(
            status=PersistenceStatus(d["status"]),
            message=d["message"],
            error_code=d["error_code"],
            diagnostics=d["diagnostics"],
            retryable=d["retryable"],
            provider=d["provider"],
            latency=d["latency"],
            operation_id=d["operation_id"],
            timestamp=d["timestamp"],
            repository=d["repository"],
            payload=d["payload"],
        )
    elif isinstance(d, dict) and d.get("__type__") == "raw":
        return d["value"]
    return d


def build_qdrant_filter(filter_dict: Dict[str, Any]) -> Any:
    from qdrant_client.models import FieldCondition, Filter, MatchAny, MatchValue, Range

    if not filter_dict:
        return None

    must_conditions = []
    for key, val in filter_dict.items():
        if val is None:
            continue
        if key in ["created_at", "updated_at", "importance"]:
            if isinstance(val, dict):
                must_conditions.append(
                    FieldCondition(
                        key=key,
                        range=Range(
                            gt=val.get("gt"),
                            gte=val.get("gte"),
                            lt=val.get("lt"),
                            lte=val.get("lte"),
                        ),
                    )
                )
            else:
                must_conditions.append(
                    FieldCondition(
                        key=key,
                        range=Range(gte=float(val), lte=float(val))
                        if key in ["created_at", "updated_at"]
                        else Range(gte=int(val), lte=int(val)),
                    )
                )
        elif isinstance(val, list):
            must_conditions.append(FieldCondition(key=key, match=MatchAny(any=val)))
        else:
            must_conditions.append(FieldCondition(key=key, match=MatchValue(value=val)))

    if not must_conditions:
        return None
    return Filter(must=must_conditions)
