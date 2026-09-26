from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, field_validator

from persistence.contracts import normalize_aware_utc, normalize_stable_id


class AuthorizationEnvironment(str, Enum):
    """Authorization authority 所屬環境；測試證據不得假裝 production authority。"""

    TEST = "TEST"
    PRODUCTION = "PRODUCTION"


class AuthorizationDecision(str, Enum):
    """Protected action 的 explicit authorization decision。"""

    APPROVED = "APPROVED"
    DENIED = "DENIED"


class ProtectedActionAuthorizationError(RuntimeError):
    """Protected action 缺少可信、exact-world 授權時 default deny。"""


class AuthorizationIntegrityConflictError(ProtectedActionAuthorizationError):
    """同一 authorization identity 與不同 protected world 綁定時明確拒絕。"""


class ProtectedActionAuthorization(BaseModel):
    """Core 可消費並可 durable-attribution 的授權 evidence。

    本 model 不是 IAM、broker invocation authority 或 business/currentness gate；
    它僅證明某一 decision 精確綁定某 action/resource/world/command。
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    authorization_id: str
    principal_id: str
    policy_id: str
    policy_version: str
    action: str
    resource: str
    protected_world_fingerprint: str
    command_id: str
    correlation_id: str
    decision: AuthorizationDecision
    provenance: str
    authorized_at: datetime
    environment: AuthorizationEnvironment

    @field_validator(
        "authorization_id", "principal_id", "policy_id", "policy_version",
        "action", "resource", "protected_world_fingerprint", "command_id",
        "correlation_id", "provenance", mode="before",
    )
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("action", mode="after")
    @classmethod
    def _action(cls, value: str) -> str:
        return value.upper()

    @field_validator("authorized_at")
    @classmethod
    def _authorized_at(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)


@runtime_checkable
class ProtectedActionAuthorizationProvider(Protocol):
    """External N/L authority verification port；core 不實作 authentication/IAM。"""

    @property
    def environment(self) -> AuthorizationEnvironment: ...

    def verify(self, authorization_id: str) -> ProtectedActionAuthorization | None: ...


def require_protected_action_authorization(
    *,
    provider: ProtectedActionAuthorizationProvider | None,
    authorization_id: str,
    environment: AuthorizationEnvironment,
    action: str,
    resource: str,
    protected_world_fingerprint: str,
    command_id: str,
    correlation_id: str,
) -> ProtectedActionAuthorization:
    """在 protected boundary 驗證 trusted authority 與 exact world；缺任一項即 fail closed。"""

    expected = {
        "authorization_id": normalize_stable_id(authorization_id),
        "action": normalize_stable_id(action).upper(),
        "resource": normalize_stable_id(resource),
        "protected_world_fingerprint": normalize_stable_id(protected_world_fingerprint),
        "command_id": normalize_stable_id(command_id),
        "correlation_id": normalize_stable_id(correlation_id),
    }
    if provider is None:
        raise ProtectedActionAuthorizationError("authorization authority is unavailable")
    if provider.environment is not environment:
        raise ProtectedActionAuthorizationError("authorization authority environment is not trusted")
    evidence = provider.verify(expected["authorization_id"])
    if evidence is None:
        raise ProtectedActionAuthorizationError("authorization evidence is unavailable")
    if evidence.environment is not environment:
        raise ProtectedActionAuthorizationError("authorization evidence environment mismatch")
    if evidence.decision is not AuthorizationDecision.APPROVED:
        raise ProtectedActionAuthorizationError("protected action authorization was denied")
    for name, value in expected.items():
        if getattr(evidence, name) != value:
            raise AuthorizationIntegrityConflictError(
                f"authorization evidence does not match protected {name}"
            )
    return evidence
