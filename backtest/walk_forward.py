from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence


@dataclass(frozen=True)
class WalkForwardConfig:
    train_size: int
    test_size: int
    step_size: int | None = None
    expanding: bool = False

    def __post_init__(self) -> None:
        if self.train_size <= 0:
            raise ValueError("train_size must be greater than 0")

        if self.test_size <= 0:
            raise ValueError("test_size must be greater than 0")

        if self.step_size is not None and self.step_size <= 0:
            raise ValueError("step_size must be greater than 0")

    @property
    def effective_step_size(self) -> int:
        return self.step_size or self.test_size


@dataclass(frozen=True)
class WalkForwardWindow:
    window_id: int
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime
    train_start_index: int
    train_end_index: int
    test_start_index: int
    test_end_index: int

    @property
    def train_size(self) -> int:
        return self.train_end_index - self.train_start_index

    @property
    def test_size(self) -> int:
        return self.test_end_index - self.test_start_index


class WalkForwardWindowGenerator:
    def __init__(self, config: WalkForwardConfig) -> None:
        self.config = config

    def generate(
        self,
        timestamps: Sequence[datetime],
    ) -> list[WalkForwardWindow]:
        self._validate_timestamps(timestamps)

        windows: list[WalkForwardWindow] = []
        total = len(timestamps)

        train_start_index = 0
        window_id = 1

        while True:
            train_end_index = train_start_index + self.config.train_size
            test_start_index = train_end_index
            test_end_index = test_start_index + self.config.test_size

            if test_end_index > total:
                break

            if self.config.expanding:
                actual_train_start_index = 0
            else:
                actual_train_start_index = train_start_index

            windows.append(
                WalkForwardWindow(
                    window_id=window_id,
                    train_start=timestamps[actual_train_start_index],
                    train_end=timestamps[train_end_index - 1],
                    test_start=timestamps[test_start_index],
                    test_end=timestamps[test_end_index - 1],
                    train_start_index=actual_train_start_index,
                    train_end_index=train_end_index,
                    test_start_index=test_start_index,
                    test_end_index=test_end_index,
                )
            )

            train_start_index += self.config.effective_step_size
            window_id += 1

        return windows

    @staticmethod
    def _validate_timestamps(
        timestamps: Sequence[datetime],
    ) -> None:
        if not timestamps:
            raise ValueError("timestamps must not be empty")

        for previous, current in zip(timestamps, timestamps[1:]):
            if current <= previous:
                raise ValueError(
                    "timestamps must be strictly increasing"
                )


def generate_walk_forward_windows(
    timestamps: Sequence[datetime],
    *,
    train_size: int,
    test_size: int,
    step_size: int | None = None,
    expanding: bool = False,
) -> list[WalkForwardWindow]:
    config = WalkForwardConfig(
        train_size=train_size,
        test_size=test_size,
        step_size=step_size,
        expanding=expanding,
    )

    return WalkForwardWindowGenerator(config).generate(timestamps)
