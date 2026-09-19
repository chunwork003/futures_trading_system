from datetime import datetime, timedelta

from backtest.metrics import MetricsCalculator
from backtest.models import (
    Direction,
    ExitReason,
    Trade,
)


def make_trade(
    trade_id: str,
    net_pnl: float,
    r_multiple: float | None,
    minutes_after_start: int,
    mae: float | None = None,
    mfe: float | None = None,
) -> Trade:

    start = datetime(2026, 1, 1, 9, 0)

    return Trade(
        trade_id=trade_id,
        signal_id=f"SIG-{trade_id}",
        trade_date=start.date(),
        symbol="TX",
        contract="TXF202601",
        timeframe="1m",
        strategy_id="TEST",
        strategy_version="v1",
        direction=Direction.LONG,
        entry_time=start,
        exit_time=start + timedelta(
            minutes=minutes_after_start
        ),
        entry_price=25000,
        exit_price=25000,
        quantity=1,
        gross_pnl=net_pnl,
        commission=0,
        slippage_cost=0,
        net_pnl=net_pnl,
        risk_points=10,
        pnl_points=net_pnl / 200,
        r_multiple=r_multiple,
        mae_points=mae,
        mfe_points=mfe,
        holding_minutes=1,
        exit_reason=ExitReason.TP,
        result=(
            "WIN"
            if net_pnl > 0
            else "LOSS"
            if net_pnl < 0
            else "BREAKEVEN"
        ),
    )


def test_metrics_calculator():

    trades = [
        make_trade("T1", 100, 1.0, 1, -5, 10),
        make_trade("T2", 200, 2.0, 2, -5, 10),
        make_trade("T3", -50, -0.5, 3, -5, 10),
        make_trade("T4", -100, -1.0, 4, -5, 10),
        make_trade("T5", 150, 1.5, 5, -5, 10),
        make_trade("T6", -200, -2.0, 6, -5, 10),
    ]

    calculator = MetricsCalculator()

    metrics = calculator.calculate(
        trades=trades,
        initial_capital=1_000_000,
    )

    assert metrics.trade_count == 6
    assert metrics.win_count == 3
    assert metrics.loss_count == 3
    assert metrics.breakeven_count == 0

    assert metrics.win_rate == 0.5

    assert metrics.gross_profit == 450
    assert metrics.gross_loss == 350
    assert metrics.net_pnl == 100

    assert metrics.average_win == 150
    assert metrics.average_loss == 350 / 3

    assert metrics.profit_factor == 450 / 350
    assert metrics.expectancy == 100 / 6

    assert metrics.max_consecutive_losses == 2

    assert metrics.average_r == (
        1 + 2 - 0.5 - 1 + 1.5 - 2
    ) / 6

    assert metrics.average_mae == -5
    assert metrics.average_mfe == 10
    assert metrics.average_holding_minutes == 1


def test_equity_curve_is_time_sorted():

    # 故意打亂輸入順序。
    trades = [
        make_trade("T3", -50, -0.5, 3),
        make_trade("T1", 100, 1.0, 1),
        make_trade("T4", -100, -1.0, 4),
        make_trade("T2", 200, 2.0, 2),
    ]

    calculator = MetricsCalculator()

    curve = calculator.build_equity_curve(
        trades=trades,
        initial_capital=1_000_000,
    )

    assert [point.trade_id for point in curve] == [
        "T1",
        "T2",
        "T3",
        "T4",
    ]

    assert [point.equity for point in curve] == [
        1_000_100,
        1_000_300,
        1_000_250,
        1_000_150,
    ]

    assert [point.peak_equity for point in curve] == [
        1_000_100,
        1_000_300,
        1_000_300,
        1_000_300,
    ]

    assert [point.drawdown for point in curve] == [
        0,
        0,
        50,
        150,
    ]


def test_r_distribution():

    trades = [
        make_trade("T1", 100, 1.0, 1),
        make_trade("T2", 200, 2.0, 2),
        make_trade("T3", -50, -0.5, 3),
        make_trade("T4", -100, -1.0, 4),
        make_trade("T5", 150, 1.5, 5),
        make_trade("T6", -200, -2.0, 6),
    ]

    calculator = MetricsCalculator()

    metrics = calculator.calculate(
        trades=trades,
        initial_capital=1_000_000,
    )

    r = metrics.r_distribution

    assert r.count == 6
    assert r.average_r == (
        1 + 2 - 0.5 - 1 + 1.5 - 2
    ) / 6

    assert r.median_r == 0.25

    assert r.min_r == -2
    assert r.max_r == 2

    assert r.positive_r_count == 3
    assert r.negative_r_count == 3
    assert r.zero_r_count == 0

    assert r.r_1_or_more_count == 3
    assert r.r_2_or_more_count == 1
    assert r.r_3_or_more_count == 0

    assert r.minus_1_or_less_count == 2


def test_mae_mfe_distribution():

    trades = [
        make_trade("T1", 100, 1.0, 1, -5, 10),
        make_trade("T2", 200, 2.0, 2, -10, 20),
        make_trade("T3", -50, -0.5, 3, -15, 5),
        make_trade("T4", -100, -1.0, 4, -20, 0),
    ]

    calculator = MetricsCalculator()

    metrics = calculator.calculate(
        trades=trades,
        initial_capital=1_000_000,
    )

    mae = metrics.mae_distribution
    mfe = metrics.mfe_distribution

    assert mae.count == 4
    assert mae.average == -12.5
    assert mae.median == -12.5
    assert mae.minimum == -20
    assert mae.maximum == -5

    assert mfe.count == 4
    assert mfe.average == 8.75
    assert mfe.median == 7.5
    assert mfe.minimum == 0
    assert mfe.maximum == 20


def test_mae_mfe_distribution_ignores_none():

    trades = [
        make_trade("T1", 100, 1.0, 1, -5, 10),
        make_trade("T2", 200, 2.0, 2, None, 20),
        make_trade("T3", -50, -0.5, 3, -15, None),
    ]

    calculator = MetricsCalculator()

    metrics = calculator.calculate(
        trades=trades,
        initial_capital=1_000_000,
    )

    mae = metrics.mae_distribution
    mfe = metrics.mfe_distribution

    assert mae.count == 2
    assert mae.average == -10
    assert mae.median == -10
    assert mae.minimum == -15
    assert mae.maximum == -5

    assert mfe.count == 2
    assert mfe.average == 15
    assert mfe.median == 15
    assert mfe.minimum == 10
    assert mfe.maximum == 20


def test_grouped_metrics_by_market_state():

    trades = [
        make_trade("T1", 100, 1.0, 1),
        make_trade("T2", 200, 2.0, 2),
        make_trade("T3", -50, -0.5, 3),
        make_trade("T4", -100, -1.0, 4),
    ]

    trades[0] = trades[0].model_copy(
        update={"market_state": "UPTREND"}
    )

    trades[1] = trades[1].model_copy(
        update={"market_state": "UPTREND"}
    )

    trades[2] = trades[2].model_copy(
        update={"market_state": "RANGE"}
    )

    trades[3] = trades[3].model_copy(
        update={"market_state": "RANGE"}
    )

    calculator = MetricsCalculator()

    groups = calculator.calculate_grouped(
        trades=trades,
        initial_capital=1_000_000,
        dimension="market_state",
    )

    assert len(groups) == 2

    assert [group.value for group in groups] == [
        "RANGE",
        "UPTREND",
    ]

    range_group = groups[0]
    uptrend_group = groups[1]

    assert range_group.dimension == "market_state"
    assert range_group.metrics.trade_count == 2
    assert range_group.metrics.win_count == 0
    assert range_group.metrics.loss_count == 2
    assert range_group.metrics.net_pnl == -150

    assert uptrend_group.metrics.trade_count == 2
    assert uptrend_group.metrics.win_count == 2
    assert uptrend_group.metrics.loss_count == 0
    assert uptrend_group.metrics.net_pnl == 300


def test_grouped_metrics_handles_none_as_unknown():

    trades = [
        make_trade("T1", 100, 1.0, 1),
        make_trade("T2", -50, -0.5, 2),
    ]

    trades[0] = trades[0].model_copy(
        update={"setup": None}
    )

    trades[1] = trades[1].model_copy(
        update={"setup": "ORB"}
    )

    calculator = MetricsCalculator()

    groups = calculator.calculate_grouped(
        trades=trades,
        initial_capital=1_000_000,
        dimension="setup",
    )

    assert [group.value for group in groups] == [
        "ORB",
        "UNKNOWN",
    ]

    assert groups[0].metrics.net_pnl == -50
    assert groups[1].metrics.net_pnl == 100


def test_grouped_metrics_rejects_invalid_dimension():

    trades = [
        make_trade("T1", 100, 1.0, 1),
    ]

    calculator = MetricsCalculator()

    try:
        calculator.calculate_grouped(
            trades=trades,
            initial_capital=1_000_000,
            dimension="invalid_field",
        )
    except ValueError as exc:
        assert "Unsupported grouping dimension" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_multi_grouped_metrics():

    trades = [
        make_trade("T1", 100, 1.0, 1),
        make_trade("T2", 200, 2.0, 2),
        make_trade("T3", -50, -0.5, 3),
        make_trade("T4", -100, -1.0, 4),
    ]

    trades[0] = trades[0].model_copy(
        update={
            "market_state": "UPTREND",
            "setup": "ORB",
            "entry_type": "MARKET",
            "direction": Direction.LONG,
        }
    )

    trades[1] = trades[1].model_copy(
        update={
            "market_state": "UPTREND",
            "setup": "ORB",
            "entry_type": "MARKET",
            "direction": Direction.LONG,
        }
    )

    trades[2] = trades[2].model_copy(
        update={
            "market_state": "RANGE",
            "setup": "FALSE_BREAK",
            "entry_type": "LIMIT",
            "direction": Direction.SHORT,
        }
    )

    trades[3] = trades[3].model_copy(
        update={
            "market_state": "RANGE",
            "setup": "FALSE_BREAK",
            "entry_type": "LIMIT",
            "direction": Direction.SHORT,
        }
    )

    calculator = MetricsCalculator()

    groups = calculator.calculate_multi_grouped(
        trades=trades,
        initial_capital=1_000_000,
        dimensions=[
            "market_state",
            "setup",
            "entry_type",
            "direction",
        ],
        minimum_samples=2,
    )

    assert len(groups) == 2

    assert groups[0].dimensions == {
        "market_state": "RANGE",
        "setup": "FALSE_BREAK",
        "entry_type": "LIMIT",
        "direction": "Direction.SHORT",
    }

    assert groups[1].dimensions == {
        "market_state": "UPTREND",
        "setup": "ORB",
        "entry_type": "MARKET",
        "direction": "Direction.LONG",
    }

    assert groups[0].sample_count == 2
    assert groups[0].sample_status == "SUFFICIENT"
    assert groups[0].metrics.net_pnl == -150

    assert groups[1].sample_count == 2
    assert groups[1].sample_status == "SUFFICIENT"
    assert groups[1].metrics.net_pnl == 300


def test_multi_grouped_metrics_low_sample():

    trades = [
        make_trade("T1", 100, 1.0, 1),
        make_trade("T2", 200, 2.0, 2),
        make_trade("T3", -50, -0.5, 3),
    ]

    for trade_index in range(len(trades)):
        trades[trade_index] = trades[trade_index].model_copy(
            update={
                "market_state": "UPTREND",
                "setup": "ORB",
            }
        )

    calculator = MetricsCalculator()

    groups = calculator.calculate_multi_grouped(
        trades=trades,
        initial_capital=1_000_000,
        dimensions=[
            "market_state",
            "setup",
        ],
        minimum_samples=5,
    )

    assert len(groups) == 1
    assert groups[0].sample_count == 3
    assert groups[0].sample_status == "LOW_SAMPLE"


def test_multi_grouped_metrics_rejects_invalid_configuration():

    trades = [
        make_trade("T1", 100, 1.0, 1),
    ]

    calculator = MetricsCalculator()

    try:
        calculator.calculate_multi_grouped(
            trades=trades,
            initial_capital=1_000_000,
            dimensions=[],
        )
    except ValueError as exc:
        assert "dimensions must not be empty" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )

    try:
        calculator.calculate_multi_grouped(
            trades=trades,
            initial_capital=1_000_000,
            dimensions=[
                "market_state",
                "invalid_field",
            ],
        )
    except ValueError as exc:
        assert "Unsupported grouping dimensions" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )

    try:
        calculator.calculate_multi_grouped(
            trades=trades,
            initial_capital=1_000_000,
            dimensions=[
                "market_state",
                "market_state",
            ],
        )
    except ValueError as exc:
        assert "duplicates" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )
