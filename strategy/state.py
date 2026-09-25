from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class StatefulStrategy(Protocol):
    """明確 versioned strategy state codec；禁止 generic __dict__ reflection。"""

    state_schema_version: int
    def export_state(self) -> dict[str, object]: ...
    def restore_state(self, state: dict[str, object]) -> None: ...
