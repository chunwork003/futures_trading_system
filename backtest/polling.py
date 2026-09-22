from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PollingConfig:
    interval_seconds: float = 30.0

    def __post_init__(self) -> None:
        if self.interval_seconds <= 0:
            raise ValueError("interval_seconds must be greater than 0")
