from __future__ import annotations

import pytest
from pydantic import ValidationError

from strategy.instance import (
    CanonicalInstrumentBindingProvenance,
    StrategyInstance,
    config_fingerprint,
)
from strategy.registry import StrategyRegistry


class DummyStrategy:
    def __init__(self, symbol: str = "TX", timeframe: str = "1m") -> None:
        self.symbol = symbol
        self.timeframe = timeframe


def binding(
    *,
    instrument_id: int = 101,
    reference_id: str = "BIND-101",
) -> CanonicalInstrumentBindingProvenance:
    return CanonicalInstrumentBindingProvenance(
        instrument_id=instrument_id,
        authority_id="CANONICAL-INSTRUMENT-PROVISIONING",
        authority_version="V1",
        reference_id=reference_id,
    )


def instance(
    *,
    strategy_instance_id: str = "SI-1",
    strategy_version: str = "1.0.0",
    config_version: str = "CFG-1",
    symbol: str = "TX",
    instrument_id: int = 101,
    provenance: CanonicalInstrumentBindingProvenance | None = None,
) -> StrategyInstance:
    config = {"symbol": symbol, "timeframe": "1m"}
    return StrategyInstance(
        strategy_instance_id=strategy_instance_id,
        strategy_id="DUMMY",
        strategy_version=strategy_version,
        config_version=config_version,
        config_fingerprint=config_fingerprint(config),
        instrument_id=instrument_id,
        timeframe="1m",
        config_json=config,
        instrument_binding_provenance=(
            binding(instrument_id=instrument_id)
            if provenance is None
            else provenance
        ),
    )


def registry(version: str = "1.0.0") -> StrategyRegistry:
    value = StrategyRegistry()
    value.register("DUMMY", version, DummyStrategy)
    return value


def test_same_config_fingerprint_does_not_merge_strategy_instance_identity() -> None:
    first = instance(strategy_instance_id="SI-A")
    second = instance(strategy_instance_id="SI-B")

    assert first.config_fingerprint == second.config_fingerprint
    assert first.strategy_instance_id != second.strategy_instance_id
    assert first != second


def test_missing_durable_binding_provenance_is_not_governing_authority() -> None:
    legacy = instance().model_copy(update={"instrument_binding_provenance": None})

    with pytest.raises(
        ValueError,
        match="durable canonical instrument binding provenance",
    ):
        registry().validate_governing_instance(legacy)


def test_binding_provenance_conflict_fails_closed() -> None:
    with pytest.raises(
        ValidationError,
        match="binding provenance conflicts",
    ):
        instance(
            instrument_id=101,
            provenance=binding(instrument_id=202),
        )


def test_config_fingerprint_corruption_fails_closed() -> None:
    item = instance()
    with pytest.raises(ValidationError, match="config_fingerprint"):
        StrategyInstance(
            **{
                **item.model_dump(),
                "config_fingerprint": "corrupt",
            }
        )


def test_governing_implementation_revision_mismatch_fails_closed() -> None:
    item = instance(strategy_version="1.0.0")

    with pytest.raises(
        ValueError,
        match="implementation revision mismatch",
    ):
        registry("2.0.0").validate_governing_instance(item)


def test_alias_drift_does_not_rewrite_historical_canonical_binding() -> None:
    original = instance(
        config_version="CFG-1",
        symbol="TX",
        provenance=binding(reference_id="BIND-HISTORICAL"),
    )
    display_changed = instance(
        config_version="CFG-2",
        symbol="TXF-DISPLAY",
        provenance=binding(reference_id="BIND-HISTORICAL"),
    )

    assert original.instrument_id == 101
    assert display_changed.instrument_id == 101
    assert (
        original.instrument_binding_provenance
        == display_changed.instrument_binding_provenance
    )
    assert original.config_fingerprint != display_changed.config_fingerprint


def test_symbol_is_not_canonical_binding_or_contract_authority() -> None:
    item = instance(symbol="LEGACY-ALIAS")
    definition = registry().validate_governing_instance(item)

    assert definition.strategy_id == item.strategy_id
    assert item.instrument_binding_provenance.instrument_id == item.instrument_id
    assert "contract" not in {
        name.lower()
        for name in type(item.instrument_binding_provenance).model_fields
    }


def test_binding_provenance_is_immutable_auditable_material() -> None:
    item = instance()
    provenance = item.instrument_binding_provenance

    assert provenance is not None
    assert provenance.authority_id == "CANONICAL-INSTRUMENT-PROVISIONING"
    assert provenance.authority_version == "V1"
    assert provenance.reference_id == "BIND-101"

    with pytest.raises(ValidationError):
        provenance.instrument_id = 999
