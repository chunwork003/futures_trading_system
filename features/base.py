from __future__ import annotations

from abc import ABC, abstractmethod

import polars as pl


class Feature(ABC):
    """Base interface for all feature calculators."""

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def calculate(self, bars: pl.DataFrame) -> pl.DataFrame:
        raise NotImplementedError
