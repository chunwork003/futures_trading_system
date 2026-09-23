from datetime import datetime

import pytest

from backtest.portfolio import Portfolio


def test_initial_portfolio_is_flat():
    portfolio = Portfolio(
        initial_capital=1_000_000,
        multiplier=200,
    )

    assert portfolio.initial_capital == 1_000_000
    assert portfolio.realized_pnl == 0
    assert portfolio.unrealized_pnl == 0
    assert portfolio.equity == 1_000_000
    assert portfolio.commission_paid == 0
    assert portfolio.position is None


def test_long_mark_to_market():
    portfolio = Portfolio(
        initial_capital=1_000_000,
        multiplier=200,
    )

    portfolio.open_position(
        direction="LONG",
        entry_price=25_000,
        quantity=1,
    )

    portfolio.mark_to_market(25_010)

    assert portfolio.unrealized_pnl == 2_000
    assert portfolio.realized_pnl == 0
    assert portfolio.equity == 1_002_000


def test_short_mark_to_market():
    portfolio = Portfolio(
        initial_capital=1_000_000,
        multiplier=200,
    )

    portfolio.open_position(
        direction="SHORT",
        entry_price=25_000,
        quantity=1,
    )

    portfolio.mark_to_market(24_990)

    assert portfolio.unrealized_pnl == 2_000
    assert portfolio.realized_pnl == 0
    assert portfolio.equity == 1_002_000


def test_long_close_creates_realized_pnl():
    portfolio = Portfolio(
        initial_capital=1_000_000,
        multiplier=200,
    )

    portfolio.open_position(
        direction="LONG",
        entry_price=25_000,
        quantity=1,
    )

    portfolio.mark_to_market(25_010)

    realized = portfolio.close_position(
        exit_price=25_010,
    )

    assert realized == 2_000
    assert portfolio.realized_pnl == 2_000
    assert portfolio.unrealized_pnl == 0
    assert portfolio.equity == 1_002_000
    assert portfolio.position is None


def test_short_close_creates_realized_pnl():
    portfolio = Portfolio(
        initial_capital=1_000_000,
        multiplier=200,
    )

    portfolio.open_position(
        direction="SHORT",
        entry_price=25_000,
        quantity=1,
    )

    portfolio.mark_to_market(24_990)

    realized = portfolio.close_position(
        exit_price=24_990,
    )

    assert realized == 2_000
    assert portfolio.realized_pnl == 2_000
    assert portfolio.unrealized_pnl == 0
    assert portfolio.equity == 1_002_000
    assert portfolio.position is None


def test_losing_long_position():
    portfolio = Portfolio(
        initial_capital=1_000_000,
        multiplier=200,
    )

    portfolio.open_position(
        direction="LONG",
        entry_price=25_000,
        quantity=1,
    )

    portfolio.mark_to_market(24_990)

    assert portfolio.unrealized_pnl == -2_000
    assert portfolio.equity == 998_000


def test_losing_short_position():
    portfolio = Portfolio(
        initial_capital=1_000_000,
        multiplier=200,
    )

    portfolio.open_position(
        direction="SHORT",
        entry_price=25_000,
        quantity=1,
    )

    portfolio.mark_to_market(25_010)

    assert portfolio.unrealized_pnl == -2_000
    assert portfolio.equity == 998_000


def test_commission_reduces_realized_pnl():
    portfolio = Portfolio(
        initial_capital=1_000_000,
        multiplier=200,
    )

    portfolio.open_position(
        direction="LONG",
        entry_price=25_000,
        quantity=1,
        commission=50,
    )

    portfolio.close_position(
        exit_price=25_010,
        commission=50,
    )

    assert portfolio.realized_pnl == 1_900
    assert portfolio.commission_paid == 100
    assert portfolio.equity == 1_001_900


def test_multiple_contracts():
    portfolio = Portfolio(
        initial_capital=1_000_000,
        multiplier=200,
    )

    portfolio.open_position(
        direction="LONG",
        entry_price=25_000,
        quantity=2,
    )

    portfolio.mark_to_market(25_010)

    assert portfolio.unrealized_pnl == 4_000
    assert portfolio.equity == 1_004_000


def test_reset_returns_portfolio_to_initial_state():
    portfolio = Portfolio(
        initial_capital=1_000_000,
        multiplier=200,
    )

    portfolio.open_position(
        direction="LONG",
        entry_price=25_000,
        quantity=1,
        commission=50,
    )

    portfolio.mark_to_market(25_010)

    portfolio.reset()

    assert portfolio.realized_pnl == 0
    assert portfolio.unrealized_pnl == 0
    assert portfolio.equity == 1_000_000
    assert portfolio.commission_paid == 0
    assert portfolio.position is None


def test_partial_close_reduces_position_quantity() -> None:
    portfolio = Portfolio(
        initial_capital=1_000_000,
        multiplier=200,
    )

    portfolio.open_position(
        direction="LONG",
        entry_price=25_000,
        quantity=2,
    )

    realized = portfolio.close_position(
        exit_price=25_010,
        quantity=1,
    )

    assert realized == 2_000
    assert portfolio.realized_pnl == 2_000
    assert portfolio.position is not None
    assert portfolio.position.direction == "LONG"
    assert portfolio.position.entry_price == 25_000
    assert portfolio.position.quantity == 1
    assert portfolio.unrealized_pnl == 0
