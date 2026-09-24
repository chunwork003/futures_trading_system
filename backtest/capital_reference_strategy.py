from __future__ import annotations

from abc import ABC, abstractmethod


class CapitalReferenceStrategy(ABC):
    @abstractmethod
    def update(self, equity: float) -> float:
        raise NotImplementedError
