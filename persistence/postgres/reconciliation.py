from __future__ import annotations

from typing import Any

from persistence.reconciliation import ReconciliationCaseVersion


class PostgresReconciliationCaseRepository:
    """Append-only reconciliation case history；latest/unresolved 皆為 derived query。"""
    def __init__(self, connection: Any) -> None: self._connection = connection
    def append(self, version: ReconciliationCaseVersion) -> None:
        with self._connection.cursor() as c:
            c.execute("INSERT INTO trading.reconciliation_case_history (case_id, version, recorded_at, state, actor_ref, evidence, case_json) VALUES (%s,%s,%s,%s,%s,%s,%s)", (version.case_id, version.version, version.recorded_at, version.reconciliation_case.state.value, version.actor_ref, list(version.evidence), version.model_dump_json()))
    def latest(self, case_id: str):
        with self._connection.cursor() as c:
            c.execute("SELECT case_json FROM trading.reconciliation_case_history WHERE case_id=%s ORDER BY version DESC LIMIT 1", (case_id,)); row=c.fetchone()
        if row is None: return None
        return ReconciliationCaseVersion.model_validate_json(row[0]) if isinstance(row[0], str) else ReconciliationCaseVersion.model_validate(row[0])
    def unresolved(self):
        with self._connection.cursor() as c:
            c.execute("SELECT DISTINCT ON (case_id) case_json FROM trading.reconciliation_case_history ORDER BY case_id, version DESC"); rows=c.fetchall()
        items = (
            ReconciliationCaseVersion.model_validate_json(row[0])
            if isinstance(row[0], str)
            else ReconciliationCaseVersion.model_validate(row[0])
            for row in rows
        )
        return tuple(item for item in items if item.reconciliation_case.state.value != "RESOLVED")
