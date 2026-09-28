from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from trading.account import BrokerAccount


class RecoveryReadinessFenceToken(BaseModel):
    """交易內 currentness witness；綁定 recovery world，但不代表經濟或 READY 權威。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    account: BrokerAccount
    recovery_generation: int = Field(ge=1)
    recovery_cut_revision: int = Field(ge=0)
    captured_readiness_revision: int = Field(ge=0)


class RecoveryReadinessFenceConflictError(RuntimeError):
    """鎖定後 recovery world 或 readiness revision 改變時 fail closed。"""


@runtime_checkable
class RecoveryReadinessFenceRepository(Protocol):
    """Caller-owned transaction 的 neutral fence port；不得自行 commit 或授予 READY。"""

    def lock_active(self, account: BrokerAccount) -> RecoveryReadinessFenceToken | None: ...
    def advance_locked(self, token: RecoveryReadinessFenceToken) -> RecoveryReadinessFenceToken: ...
