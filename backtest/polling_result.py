from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PollingResult:
    iterations: int
    results: list[Any]
