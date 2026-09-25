from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from persistence.contracts import PersistenceConflictError


class MigrationConflictError(PersistenceConflictError):
    """Migration version 重複，或已套用 version/name 與檔案不一致。"""


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    sql: str


_MIGRATION_NAME = re.compile(r"^(?P<version>\d{4})_(?P<name>[a-z0-9_]+)\.sql$")


def discover_migrations(directory: Path) -> tuple[Migration, ...]:
    """決定性讀取 NNNN_name.sql；拒絕 duplicate version。"""

    migrations: list[Migration] = []
    for path in directory.iterdir():
        match = _MIGRATION_NAME.fullmatch(path.name)
        if match and path.is_file():
            migrations.append(
                Migration(
                    version=int(match.group("version")),
                    name=match.group("name"),
                    sql=path.read_text(encoding="utf-8"),
                )
            )
    migrations.sort(key=lambda item: item.version)
    versions = [item.version for item in migrations]
    if len(set(versions)) != len(versions):
        raise MigrationConflictError("duplicate migration version")
    return tuple(migrations)


def pending_migrations(
    migrations: tuple[Migration, ...],
    applied: Iterable[tuple[int, str]],
) -> tuple[Migration, ...]:
    applied_by_version = dict(applied)
    for migration in migrations:
        applied_name = applied_by_version.get(migration.version)
        if applied_name is not None and applied_name != migration.name:
            raise MigrationConflictError(
                f"migration {migration.version} name conflicts with applied metadata"
            )
    return tuple(item for item in migrations if item.version not in applied_by_version)


def run_migrations(connection: Any, migrations: tuple[Migration, ...]) -> None:
    """在 caller-owned transaction 執行 SQL 並寫 metadata；本函式絕不 commit。"""

    with connection.cursor() as cursor:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS trading")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trading.schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute("SELECT version, name FROM trading.schema_migrations")
        applied = tuple(cursor.fetchall())
        for migration in pending_migrations(migrations, applied):
            cursor.execute(migration.sql)
            cursor.execute(
                "INSERT INTO trading.schema_migrations (version, name) VALUES (%s, %s)",
                (migration.version, migration.name),
            )
