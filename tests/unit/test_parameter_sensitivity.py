from __future__ import annotations

import pytest

from backtest.parameter_sensitivity import (
    LocalSensitivityGrid,
    generate_local_parameter_grid,
)


def test_default_local_grid_contains_15_parameters() -> None:
    parameters = generate_local_parameter_grid()

    assert len(parameters) == 15


def test_local_grid_contains_expected_boundaries() -> None:
    parameters = generate_local_parameter_grid()

    assert (10, 40) in parameters
    assert (10, 60) in parameters
    assert (15, 50) in parameters
    assert (20, 40) in parameters
    assert (20, 60) in parameters


def test_invalid_fast_slow_pair_is_removed() -> None:
    grid = LocalSensitivityGrid(
        fast_windows=(20, 50),
        slow_windows=(10, 30),
    )

    assert generate_local_parameter_grid(grid) == [(20, 30)]


def test_empty_grid_returns_empty_list() -> None:
    grid = LocalSensitivityGrid(
        fast_windows=(),
        slow_windows=(),
    )

    assert generate_local_parameter_grid(grid) == []


def test_grid_values_are_deterministic() -> None:
    first = generate_local_parameter_grid()
    second = generate_local_parameter_grid()

    assert first == second
