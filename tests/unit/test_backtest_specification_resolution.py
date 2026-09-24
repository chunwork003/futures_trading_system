from datetime import date
from decimal import Decimal

import pytest

from backtest.models import BacktestConfig
from backtest.risk import RiskConfig
from backtest.specification_resolution import (
    BacktestSpecificationResolver,
    MarginResolutionError,
    ResolvedParameterSource,
    SpecificationResolutionError,
)
from domain.instruments import InstrumentSpec
from domain.margins import MarginScheduleEntry, MarginScheduleResolver


def _instrument(*, multiplier: Decimal | None = Decimal("50")) -> InstrumentSpec:
    return InstrumentSpec(
        instrument_id=2,
        canonical_symbol="MTX",
        name="Mini-TAIEX Futures",
        asset_type="FUTURES",
        exchange="TAIFEX",
        currency="TWD",
        multiplier=multiplier,
        tick_size=Decimal("1"),
    )


def _margin(
    *,
    margin_id: int,
    effective_date: date,
    contract_id: int | None = None,
    initial: str = "100000",
    maintenance: str = "80000",
) -> MarginScheduleEntry:
    return MarginScheduleEntry(
        margin_id=margin_id,
        instrument_id=2,
        contract_id=contract_id,
        effective_date=effective_date,
        currency="TWD",
        clearing_margin=Decimal("70000"),
        maintenance_margin=Decimal(maintenance),
        initial_margin=Decimal(initial),
        source="TAIFEX",
    )


def test_explicit_multiplier_override_wins() -> None:
    result = BacktestSpecificationResolver.resolve_multiplier(
        explicit_override=200,
        instrument_spec=_instrument(),
    )

    assert result.value == 200.0
    assert result.source is ResolvedParameterSource.EXPLICIT_OVERRIDE


def test_canonical_decimal_multiplier_converts_at_backtest_boundary() -> None:
    spec = _instrument(multiplier=Decimal("200"))
    before = spec.model_dump()

    result = BacktestSpecificationResolver.resolve_multiplier(
        explicit_override=None,
        instrument_spec=spec,
    )

    assert result.value == 200.0
    assert isinstance(result.value, float)
    assert result.source is ResolvedParameterSource.CANONICAL_SPEC
    assert spec.model_dump() == before


@pytest.mark.parametrize(
    ("instrument_spec", "explicit_override"),
    [(None, None), (_instrument(multiplier=None), None)],
)
def test_missing_multiplier_fails_explicitly(
    instrument_spec: InstrumentSpec | None,
    explicit_override: float | None,
) -> None:
    with pytest.raises(SpecificationResolutionError, match="multiplier requires"):
        BacktestSpecificationResolver.resolve_multiplier(
            explicit_override=explicit_override,
            instrument_spec=instrument_spec,
        )


def test_existing_backtest_multiplier_default_is_preserved() -> None:
    assert BacktestConfig(symbol="TX").multiplier == 200


def test_explicit_risk_override_wins_without_mixing_canonical_values() -> None:
    override = RiskConfig(
        initial_margin_per_contract=120000,
        maintenance_margin_per_contract=0,
    )
    resolver = MarginScheduleResolver(
        [_margin(margin_id=1, effective_date=date(2026, 1, 1))]
    )

    result = BacktestSpecificationResolver.resolve_margins(
        explicit_override=override,
        margin_resolver=resolver,
        instrument_id=2,
        as_of_date=date(2026, 2, 1),
    )

    assert result.initial_margin_per_contract == 120000.0
    assert result.maintenance_margin_per_contract == 0.0
    assert result.source is ResolvedParameterSource.EXPLICIT_OVERRIDE
    assert result.margin_id is None


def test_canonical_contract_margin_precedes_instrument_margin() -> None:
    entries = [
        _margin(margin_id=1, effective_date=date(2026, 1, 1)),
        _margin(
            margin_id=2,
            contract_id=21,
            effective_date=date(2026, 1, 1),
            initial="110000",
            maintenance="90000",
        ),
    ]

    result = BacktestSpecificationResolver.resolve_margins(
        explicit_override=None,
        margin_resolver=MarginScheduleResolver(entries),
        instrument_id=2,
        contract_id=21,
        as_of_date=date(2026, 1, 2),
    )

    assert result.initial_margin_per_contract == 110000.0
    assert result.maintenance_margin_per_contract == 90000.0
    assert result.margin_id == 2
    assert result.source is ResolvedParameterSource.CANONICAL_MARGIN_SCHEDULE


def test_canonical_margin_falls_back_to_latest_instrument_entry() -> None:
    entries = [
        _margin(margin_id=1, effective_date=date(2026, 1, 1)),
        _margin(
            margin_id=2,
            effective_date=date(2026, 2, 1),
            initial="105000",
            maintenance="85000",
        ),
        _margin(
            margin_id=3,
            effective_date=date(2026, 3, 1),
            initial="115000",
            maintenance="95000",
        ),
    ]

    result = BacktestSpecificationResolver.resolve_margins(
        explicit_override=None,
        margin_resolver=MarginScheduleResolver(entries),
        instrument_id=2,
        contract_id=999,
        as_of_date=date(2026, 2, 15),
    )

    assert result.initial_margin_per_contract == 105000.0
    assert result.maintenance_margin_per_contract == 85000.0
    assert result.margin_id == 2


def test_explicit_no_margin_mode_preserves_zero_margin_behavior() -> None:
    result = BacktestSpecificationResolver.resolve_margins(
        explicit_override=None,
        margin_resolver=None,
        instrument_id=2,
        as_of_date=date(2026, 1, 1),
        no_margin_mode=True,
    )

    assert result.initial_margin_per_contract == 0.0
    assert result.maintenance_margin_per_contract == 0.0
    assert result.source is ResolvedParameterSource.NO_MARGIN_MODE


def test_missing_margin_does_not_silently_enable_zero_margin_mode() -> None:
    resolver = MarginScheduleResolver(
        [_margin(margin_id=1, effective_date=date(2026, 2, 1))]
    )

    with pytest.raises(MarginResolutionError, match="margin requires"):
        BacktestSpecificationResolver.resolve_margins(
            explicit_override=None,
            margin_resolver=resolver,
            instrument_id=2,
            as_of_date=date(2026, 1, 1),
        )


def test_margin_resolution_does_not_mutate_domain_entry() -> None:
    entry = _margin(margin_id=1, effective_date=date(2026, 1, 1))
    before = entry.model_dump()

    BacktestSpecificationResolver.resolve_margins(
        explicit_override=None,
        margin_resolver=MarginScheduleResolver([entry]),
        instrument_id=2,
        as_of_date=date(2026, 1, 1),
    )

    assert entry.model_dump() == before
