from __future__ import annotations

from typing import Any


class PostgresDriverUnavailableError(RuntimeError):
    """Optional Psycopg 3 driver 未安裝時的明確 boundary failure。"""


def connect_postgres(dsn: str) -> Any:
    """以 lazy Psycopg import 建立 explicit transaction connection；不記錄 DSN。"""

    normalized = dsn.strip()
    if not normalized:
        raise ValueError("PostgreSQL DSN must not be blank")
    try:
        import psycopg
    except ImportError as exc:
        raise PostgresDriverUnavailableError("Psycopg 3 driver is unavailable") from exc
    return psycopg.connect(normalized, autocommit=False)
