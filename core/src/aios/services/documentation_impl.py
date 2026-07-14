"""Phase 8: Documentation Intelligence — Engine and Registry Service Implementations.

Provides database implementations for Document Registry, Tech Decision log registry,
keyword search indexes, and auto-generation engines.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from threading import Lock
from typing import Generator, List, Optional

from aios.services.documentation import (
    DecisionRecord,
    DocStatus,
    DocType,
    DocumentationService,
    DocumentRecord,
    new_id,
)

logger = logging.getLogger(__name__)

_DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".aios_documentation.db")


class DocumentationServiceImpl(DocumentationService):
    """SQLite-backed Documentation Engine managing document generation and search indexing."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self._db_path = db_path or os.getenv("AIOS_DOCUMENTATION_DB", _DEFAULT_DB)
        self._lock = Lock()
        self._conn: Optional[sqlite3.Connection] = None

    def initialize(self) -> None:
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._bootstrap_schema()
        logger.info("Documentation Service initialized at: %s", self._db_path)

    def start(self) -> None:
        pass

    def shutdown(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def _bootstrap_schema(self) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id      TEXT PRIMARY KEY,
                    title            TEXT NOT NULL,
                    doc_type         TEXT NOT NULL,
                    content          TEXT NOT NULL DEFAULT '',
                    project_id       TEXT NOT NULL DEFAULT '',
                    owner            TEXT NOT NULL DEFAULT '',
                    status           TEXT NOT NULL DEFAULT 'draft',
                    version          INTEGER NOT NULL DEFAULT 1,
                    created_at       REAL NOT NULL,
                    updated_at       REAL NOT NULL,
                    related_entities TEXT NOT NULL DEFAULT '[]'
                );

                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id      TEXT PRIMARY KEY,
                    title            TEXT NOT NULL,
                    category         TEXT NOT NULL,
                    status           TEXT NOT NULL DEFAULT 'proposed',
                    context          TEXT NOT NULL DEFAULT '',
                    consequences     TEXT NOT NULL DEFAULT '',
                    owner            TEXT NOT NULL DEFAULT '',
                    timestamp        REAL NOT NULL
                );
                """
            )

    @contextmanager
    def _tx(self) -> Generator[sqlite3.Connection, None, None]:
        assert self._conn is not None
        with self._lock:
            with self._conn:
                yield self._conn

    # ── Document CRUD Registry ───────────────────────────────────────────────

    def register_document(self, doc: DocumentRecord) -> DocumentRecord:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO documents (
                    document_id, title, doc_type, content, project_id, owner, status,
                    version, created_at, updated_at, related_entities
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    title=excluded.title, doc_type=excluded.doc_type, content=excluded.content,
                    project_id=excluded.project_id, owner=excluded.owner, status=excluded.status,
                    version=excluded.version + 1, updated_at=excluded.updated_at,
                    related_entities=excluded.related_entities
                """,
                (
                    doc.document_id,
                    doc.title,
                    doc.doc_type.value,
                    doc.content,
                    doc.project_id,
                    doc.owner,
                    doc.status.value,
                    doc.version,
                    doc.created_at,
                    doc.updated_at,
                    json.dumps(doc.related_entities),
                ),
            )
        # Fetch updated version
        fetched = self.get_document(doc.document_id)
        return fetched if fetched else doc

    def get_document(self, document_id: str) -> Optional[DocumentRecord]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM documents WHERE document_id = ?", (document_id,)
            ).fetchone()
        return DocumentRecord.from_dict(dict(row)) if row else None

    def list_documents(self) -> List[DocumentRecord]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute("SELECT * FROM documents ORDER BY updated_at DESC").fetchall()
        return [DocumentRecord.from_dict(dict(r)) for r in rows]

    def delete_document(self, document_id: str) -> bool:
        with self._tx() as conn:
            cur = conn.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
            return cur.rowcount > 0

    # ── Decision Logs ────────────────────────────────────────────────────────

    def record_decision(self, decision: DecisionRecord) -> DecisionRecord:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO decisions (
                    decision_id, title, category, status, context, consequences, owner, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(decision_id) DO UPDATE SET
                    title=excluded.title, category=excluded.category, status=excluded.status,
                    context=excluded.context, consequences=excluded.consequences, owner=excluded.owner,
                    timestamp=excluded.timestamp
                """,
                (
                    decision.decision_id,
                    decision.title,
                    decision.category,
                    decision.status,
                    decision.context,
                    decision.consequences,
                    decision.owner,
                    decision.timestamp,
                ),
            )
        return decision

    def list_decisions(self) -> List[DecisionRecord]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute("SELECT * FROM decisions ORDER BY timestamp DESC").fetchall()
        return [DecisionRecord.from_dict(dict(r)) for r in rows]

    # ── Search Engine ────────────────────────────────────────────────────────

    def search_documents(self, query: str) -> List[DocumentRecord]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT * FROM documents
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY updated_at DESC
                """,
                (f"%{query}%", f"%{query}%"),
            ).fetchall()
        return [DocumentRecord.from_dict(dict(r)) for r in rows]

    # ── Documentation Engine Builders ────────────────────────────────────────

    def generate_readme(self, project_id: str) -> DocumentRecord:
        """Create structured README.md details."""
        did = new_id()
        content = f"""# Project README: {project_id.capitalize()}

## Project Overview
This project contains the workspace directory files for the target '{project_id}' module.

## Features
- Dynamic workspace context management
- Local model routing configs
- Task status progress tracking

## Installation
```bash
aios workspace switch {project_id}
aios work
```

## Usage Commands
- `aios status`
- `aios today`
- `aios tasks`
"""
        doc = DocumentRecord(
            document_id=did,
            title=f"{project_id.capitalize()} README",
            doc_type=DocType.README,
            content=content,
            project_id=project_id,
            status=DocStatus.PUBLISHED,
        )
        return self.register_document(doc)

    def generate_architecture_doc(self, project_id: str) -> DocumentRecord:
        """Create component diagram detailing service flows."""
        did = new_id()
        content = f"""# System Architecture: {project_id.capitalize()}

## Component Diagram
```mermaid
graph TD
    UI[Unified CLI] --> Kernel[Kernel Engine]
    Kernel --> DB[SQLite Registry]
    Kernel --> KG[Knowledge Graph]
```

## Data Flow
Data flows from CLI command modules into the SQL tables, which subsequently emit updates to sync nodes in the graph.
"""
        doc = DocumentRecord(
            document_id=did,
            title=f"{project_id.capitalize()} Architecture Guide",
            doc_type=DocType.ARCHITECTURE,
            content=content,
            project_id=project_id,
            status=DocStatus.PUBLISHED,
        )
        return self.register_document(doc)

    def generate_api_doc(self, module_name: str) -> DocumentRecord:
        """Create api interface signatures catalog."""
        did = new_id()
        content = f"""# API Documentation: {module_name}

## Service Interfaces
- `initialize()`: Sets up resource handlers.
- `start()`: Boots loops processes.
- `shutdown()`: Closes connection handles.

## Commands
- `aios {module_name} list`
- `aios {module_name} status`
"""
        doc = DocumentRecord(
            document_id=did,
            title=f"{module_name.capitalize()} API Reference",
            doc_type=DocType.API_DOCS,
            content=content,
            project_id=module_name,
            status=DocStatus.PUBLISHED,
        )
        return self.register_document(doc)
