"""
persistence_impl_modules/migrations.py

Manages SQL database schema migrations.
"""

from __future__ import annotations

import logging
import time
from typing import List

from aios.services.persistence import PersistenceProvider

logger = logging.getLogger(__name__)


class Migration:
    """Migration definition model."""

    def __init__(self, version: int, name: str, up_sql: str) -> None:
        self.version = version
        self.name = name
        self.up_sql = up_sql


class MigrationManager:
    """Discovers, validates, and executes migrations."""

    def __init__(self, provider: PersistenceProvider) -> None:
        self.provider = provider
        self.registered_migrations: List[Migration] = []

    def register_migration(self, version: int, name: str, up_sql: str) -> None:
        self.registered_migrations.append(Migration(version, name, up_sql))
        self.registered_migrations.sort(key=lambda m: m.version)

    def initialize_history_table(self) -> None:
        self.provider.execute(
            "CREATE TABLE IF NOT EXISTS _migrations "
            "(version INTEGER PRIMARY KEY, name TEXT, applied_at REAL)"
        )

    def get_applied_versions(self) -> List[int]:
        self.initialize_history_table()
        rows = self.provider.execute("SELECT version FROM _migrations ORDER BY version")
        return [row["version"] for row in rows]

    def get_pending_migrations(self) -> List[Migration]:
        applied = self.get_applied_versions()
        return [m for m in self.registered_migrations if m.version not in applied]

    def validate_migrations(self) -> List[str]:
        errors = []
        versions = [m.version for m in self.registered_migrations]
        if len(versions) != len(set(versions)):
            errors.append("Duplicate migration versions detected.")
        if versions != sorted(versions):
            errors.append("Migrations are not registered in ascending sequential order.")
        return errors

    def execute_migrations(self) -> int:
        errors = self.validate_migrations()
        if errors:
            raise RuntimeError(f"Migration validation failed: {errors}")

        self.initialize_history_table()
        pending = self.get_pending_migrations()
        executed_count = 0
        for m in pending:
            self.provider.begin_transaction()
            try:
                for query in m.up_sql.split(";"):
                    q = query.strip()
                    if q:
                        self.provider.execute(q)
                self.provider.execute(
                    "INSERT INTO _migrations (version, name, applied_at) VALUES (?, ?, ?)",
                    (m.version, m.name, time.time()),
                )
                self.provider.commit_transaction()
                executed_count += 1
            except Exception as e:
                self.provider.rollback_transaction()
                logger.error(f"Migration version {m.version} ({m.name}) failed: {e}")
                raise RuntimeError(f"Migration failed: {e}") from e
        return executed_count
