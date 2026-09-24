from datetime import date
from decimal import Decimal

import pytest

from backtest.engine import BacktestEngine
from backtest.models import BacktestConfig
from backtest.risk import RiskConfig
from backtest.specification_resolution import (
    MarginResolutionError,
    ResolvedParameterSource,
)
from domain.instruments import InstrumentSpec
from domain.margins import MarginScheduleEntry, MarginScheduleResolver


def _instrument() -> InstrumentSpec:
    return InstrumentSpec(
        instrument_id=2,
        canonical_symbol="MTX",
        name="Mini-TAIEX Futures",
        asset_type="FUTURES",
        exchange="TAIFEX",
        currency="TWD",
        multiplier=Decimal("50"),
        tick_size=Decimal("1"),
    )


def _margin(
    *,
    margin_id: int,
    effective_date: date,
    initial: str,
    maintenance: str,
    contract_id: int | None = None,
) -> MarginScheduleEntry:
    return MarginScheduleEntry(
        margin_id=margin_id,
        instrument_id=2,
        contract_id=contract_id,
        effective_date=effective_date,
        currency="TWD",
        clearing_margin=Decimal("0"),
        maintenance_margin=Decimal(maintenance),
        initial_margin=Decimal(initial),
        source="TAIFEX",
    )


def test_legacy_explicit_margin_behavior_is_unchanged() -> None:
    risk_config = RiskConfig(
        initial_margin_per_contract=70_000,
        maintenance_margin_per_contract=60_000,
        max_contracts=2,
        max_margin_utilization=0.8,
    )
    config = BacktestConfig(symbol="MTX", risk_config=risk_config)
    engine = BacktestEngine(config)

    assert engine.config is config
    assert engine.risk_manager.config is risk_config
    assert engine.risk_manager.initial_margin_required(2) == 140_000
    assert engine.resolved_margins.source is ResolvedParameterSource.LEGACY_CONFIG


def test_explicit_margin_override_wins_in_specification_path() -> None:
    override = RiskConfig(
        initial_margin_per_contract=70_000,
        maintenance_margin_per_contract=60_000,
        max_contracts=3,
        max_margin_utilization=0.75,
    )
    canonical = _margin(
        margin_id=1,
        effective_date=date(2026, 1, 1),
        initial="90000",
        maintenance="80000",
    )

    engine = BacktestEngine.from_specifications(
        BacktestConfig(symbol="MTX", risk_config=override),
        _instrument(),
        as_of_date=date(2026, 1, 2),
        margin_resolver=MarginScheduleResolver([canonical]),
    )

    assert engine.risk_manager.initial_margin_required(1) == 70_000
    assert engine.risk_manager.config.max_contracts == 3
    assert engine.risk_manager.config.max_margin_utilization == 0.75
    assert engine.resolved_margins.source is (
        ResolvedParameterSource.EXPLICIT_OVERRIDE
    )


def test_contract_margin_changes_actual_risk_capacity() -> None:
    instrument_margin = _margin(
        margin_id=1,
        effective_date=date(2026, 1, 1),
        initial="50000",
        maintenance="40000",
    )
    contract_margin = _margin(
        margin_id=2,
        contract_id=21,
        effective_date=date(2026, 1, 1),
        initial="90000",
        maintenance="80000",
    )

    engine = BacktestEngine.from_specifications(
        BacktestConfig(symbol="MTX"),
        _instrument(),
        as_of_date=date(2026, 1, 2),
        contract_id=21,
        margin_resolver=MarginScheduleResolver(
            [instrument_margin, contract_margin]
        ),
    )

    assert engine.risk_manager.initial_margin_required(1) == 90_000
    assert not engine.risk_manager.can_open(equity=80_000, quantity=1)
    assert engine.resolved_margins.margin_id == 2
    assert engine.resolved_margins.source is (
        ResolvedParameterSource.CANONICAL_MARGIN_SCHEDULE
    )


def test_instrument_margin_fallback_is_used_by_risk_consumer() -> None:
    instrument_margin = _margin(
        margin_id=1,
        effective_date=date(2026, 1, 1),
        initial="50000",
        maintenance="40000",
    )

    engine = BacktestEngine.from_specifications(
        BacktestConfig(symbol="MTX"),
        _instrument(),
        as_of_date=date(2026, 1, 2),
        contract_id=999,
        margin_resolver=MarginScheduleResolver([instrument_margin]),
    )

    assert engine.risk_manager.initial_margin_required(1) == 50_000
    assert engine.risk_manager.can_open(equity=80_000, quantity=1)
    assert engine.resolved_margins.margin_id == 1


def test_explicit_as_of_date_deterministically_selects_schedule() -> None:
    entries = [
        _margin(
            margin_id=1,
            effective_date=date(2026, 1, 1),
            initial="50000",
            maintenance="40000",
        ),
        _margin(
            margin_id=2,
            effective_date=date(2026, 2, 1),
            initial="60000",
            maintenance="50000",
        ),
    ]

    engine = BacktestEngine.from_specifications(
        BacktestConfig(symbol="MTX"),
        _instrument(),
        as_of_date=date(2026, 1, 31),
        margin_resolver=MarginScheduleResolver(entries),
    )

    assert engine.risk_manager.initial_margin_required(1) == 50_000
    assert engine.resolved_margins.margin_id == 1


def test_missing_margin_does_not_become_zero_margin() -> None:
    with pytest.raises(MarginResolutionError, match="margin requires"):
        BacktestEngine.from_specifications(
            BacktestConfig(symbol="MTX"),
            _instrument(),
            as_of_date=date(2026, 1, 1),
        )


def test_explicit_no_margin_mode_reaches_risk_consumer() -> None:
    engine = BacktestEngine.from_specifications(
        BacktestConfig(symbol="MTX"),
        _instrument(),
        as_of_date=date(2026, 1, 1),
        no_margin_mode=True,
    )

    assert engine.risk_manager.initial_margin_required(10) == 0.0
    assert engine.risk_manager.can_open(equity=1.0, quantity=1)
    assert engine.resolved_margins.source is (
        ResolvedParameterSource.NO_MARGIN_MODE
    )


def test_canonical_margin_domain_models_are_not_mutated() -> None:
    instrument = _instrument()
    margin = _margin(
        margin_id=1,
        effective_date=date(2026, 1, 1),
        initial="50000",
        maintenance="40000",
    )
    instrument_before = instrument.model_dump()
    margin_before = margin.model_dump()

    BacktestEngine.from_specifications(
        BacktestConfig(symbol="MTX"),
        instrument,
        as_of_date=date(2026, 1, 1),
        margin_resolver=MarginScheduleResolver([margin]),
    )

    assert instrument.model_dump() == instrument_before
    assert margin.model_dump() == margin_before
