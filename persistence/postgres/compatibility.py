from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PostgresIntegrationStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class PostgresCompatibilityEvidence(BaseModel):
    """實際 integration verification 證據；版本支援聲明不會自動升級狀態。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    major: int = Field(gt=0)
    status: PostgresIntegrationStatus
    server_version_num: int | None = None
    driver_version: str | None = None
    verified_on: date | None = None
    evidence: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _validate_status_metadata(self) -> PostgresCompatibilityEvidence:
        if self.status is PostgresIntegrationStatus.PENDING:
            if any((self.server_version_num, self.driver_version, self.verified_on, self.evidence)):
                raise ValueError("PENDING evidence cannot claim verification metadata")
        elif not all((self.server_version_num, self.driver_version, self.verified_on, self.evidence)):
            raise ValueError("VERIFIED or FAILED evidence requires explicit metadata")
        if any(not item.strip() for item in self.evidence):
            raise ValueError("evidence items must be non-blank")
        return self


POSTGRES_COMPATIBILITY_TARGETS = (
    PostgresCompatibilityEvidence(major=17, status=PostgresIntegrationStatus.PENDING),
    PostgresCompatibilityEvidence(major=18, status=PostgresIntegrationStatus.PENDING),
)


def detect_postgres_major(server_version_num: int) -> int:
    """由 PostgreSQL server_version_num 擷取 major；不產生 VERIFIED 證據。"""

    if server_version_num <= 0:
        raise ValueError("server_version_num must be positive")
    return server_version_num // 10000
