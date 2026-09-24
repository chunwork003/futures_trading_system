from decimal import Decimal

import pytest

from backtest.engine import BacktestEngine
from backtest.models import BacktestConfig
from backtest.specification_resolution import (
    ResolvedParameterSource,
    SpecificationResolutionError,
)
from domain.instruments import InstrumentSpec


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


def _mark_to_market(engine: BacktestEngine) -> float:
    engine.portfolio.open_position(
        direction="LONG",
        entry_price=100.0,
        quantity=1,
    )
    return engine.portfolio.mark_to_market(101.0)


def test_legacy_engine_preserves_default_multiplier_and_calculation() -> None:
    config = BacktestConfig(symbol="TX")
    engine = BacktestEngine(config)

    assert engine.config is config
    assert engine.config.multiplier == 200
    assert engine.resolved_multiplier.source is (
        ResolvedParameterSource.LEGACY_CONFIG
    )
    assert _mark_to_market(engine) == 200.0


def test_canonical_multiplier_is_used_by_existing_portfolio_calculation() -> None:
    config = BacktestConfig(symbol="MTX")
    spec = _instrument()
    before = spec.model_dump()

    engine = BacktestEngine.from_instrument_spec(config, spec)

    assert engine.config.multiplier == 50.0
    assert engine.portfolio.multiplier == 50.0
    assert engine.resolved_multiplier.source is (
        ResolvedParameterSource.CANONICAL_SPEC
    )
    assert _mark_to_market(engine) == 50.0
    assert spec.model_dump() == before
    assert config.multiplier == 200


def test_explicit_override_wins_in_canonical_entry_point() -> None:
    engine = BacktestEngine.from_instrument_spec(
        BacktestConfig(symbol="MTX"),
        _instrument(),
        multiplier_override=100,
    )

    assert engine.config.multiplier == 100.0
    assert engine.resolved_multiplier.source is (
        ResolvedParameterSource.EXPLICIT_OVERRIDE
    )
    assert _mark_to_market(engine) == 100.0


def test_missing_canonical_multiplier_fails_before_engine_initialization() -> None:
    with pytest.raises(SpecificationResolutionError, match="multiplier requires"):
        BacktestEngine.from_instrument_spec(
            BacktestConfig(symbol="MTX"),
            _instrument(multiplier=None),
        )
