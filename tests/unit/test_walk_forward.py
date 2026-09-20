from datetime import datetime, timedelta

import pytest

from backtest.walk_forward import (
    WalkForwardConfig,
    WalkForwardWindowGenerator,
    generate_walk_forward_windows,
)


def make_timestamps(count: int) -> list[datetime]:
    start = datetime(2026, 1, 1)
    return [start + timedelta(minutes=index) for index in range(count)]


def test_rolling_windows_generate_expected_boundaries() -> None:
    timestamps = make_timestamps(10)

    windows = generate_walk_forward_windows(
        timestamps,
        train_size=4,
        test_size=2,
    )

    assert len(windows) == 3

    assert windows[0].train_start_index == 0
    assert windows[0].train_end_index == 4
    assert windows[0].test_start_index == 4
    assert windows[0].test_end_index == 6

    assert windows[1].train_start_index == 2
    assert windows[1].train_end_index == 6
    assert windows[1].test_start_index == 6
    assert windows[1].test_end_index == 8

    assert windows[2].train_start_index == 4
    assert windows[2].train_end_index == 8
    assert windows[2].test_start_index == 8
    assert windows[2].test_end_index == 10


def test_rolling_windows_have_no_train_test_overlap() -> None:
    timestamps = make_timestamps(20)

    windows = generate_walk_forward_windows(
        timestamps,
        train_size=6,
        test_size=3,
    )

    for window in windows:
        assert window.train_end_index == window.test_start_index
        assert window.train_end < window.test_start


def test_expanding_windows_keep_train_start_at_zero() -> None:
    timestamps = make_timestamps(12)

    windows = generate_walk_forward_windows(
        timestamps,
        train_size=4,
        test_size=2,
        expanding=True,
    )

    assert len(windows) == 4

    assert all(window.train_start_index == 0 for window in windows)

    assert [window.train_size for window in windows] == [4, 6, 8, 10]

    assert [window.test_size for window in windows] == [2, 2, 2, 2]


def test_custom_step_size() -> None:
    timestamps = make_timestamps(15)

    windows = generate_walk_forward_windows(
        timestamps,
        train_size=5,
        test_size=2,
        step_size=1,
    )

    assert len(windows) == 9

    assert windows[0].train_start_index == 0
    assert windows[1].train_start_index == 1
    assert windows[2].train_start_index == 2


def test_insufficient_data_returns_no_windows() -> None:
    timestamps = make_timestamps(5)

    windows = generate_walk_forward_windows(
        timestamps,
        train_size=4,
        test_size=2,
    )

    assert windows == []


def test_empty_timestamps_are_rejected() -> None:
    generator = WalkForwardWindowGenerator(
        WalkForwardConfig(train_size=4, test_size=2)
    )

    with pytest.raises(ValueError, match="must not be empty"):
        generator.generate([])


def test_unsorted_timestamps_are_rejected() -> None:
    timestamps = make_timestamps(5)
    timestamps[3], timestamps[4] = timestamps[4], timestamps[3]

    with pytest.raises(ValueError, match="strictly increasing"):
        generate_walk_forward_windows(
            timestamps,
            train_size=2,
            test_size=1,
        )


def test_invalid_configuration_is_rejected() -> None:
    with pytest.raises(ValueError, match="train_size"):
        WalkForwardConfig(train_size=0, test_size=2)

    with pytest.raises(ValueError, match="test_size"):
        WalkForwardConfig(train_size=2, test_size=0)

    with pytest.raises(ValueError, match="step_size"):
        WalkForwardConfig(
            train_size=2,
            test_size=1,
            step_size=0,
        )
