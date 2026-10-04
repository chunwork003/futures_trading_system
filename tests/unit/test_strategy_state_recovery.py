
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from persistence.strategy_state import (
    StrategyStateSnapshot,
)
from strategy.instance import (
    StrategyInstance,
    config_fingerprint,
)
from strategy.registry import (
    StrategyRegistry,
)
from strategy.state import StatefulStrategy
from strategies.ema_cross import (
    EMACrossStrategy,
)
from strategies.trend_state import (
    TrendStateStrategy,
)
from strategies.trend_state_exit import (
    TrendStateExitStrategy,
)


NOW = datetime(
    2026,
    9,
    25,
    1,
    tzinfo=timezone.utc,
)

MOR1_A = "mor1_" + ("a" * 64)
MOR1_B = "mor1_" + ("b" * 64)


def instance(
    strategy_id="EMA_CROSS",
    version="1.0.0",
    config=None,
):
    config = (
        config
        or {
            "symbol": "TX",
            "timeframe": "1m",
        }
    )

    return StrategyInstance(
        strategy_instance_id="SI-1",
        strategy_id=strategy_id,
        strategy_version=version,
        config_version="C1",
        config_fingerprint=(
            config_fingerprint(
                config
            )
        ),
        instrument_id=1,
        timeframe="1m",
        config_json=config,
    )


def make_snapshot(
    item,
    revision_id=MOR1_A,
):
    return StrategyStateSnapshot(
        snapshot_id="SS",
        strategy_instance_id=(
            item.strategy_instance_id
        ),
        strategy_id=item.strategy_id,
        strategy_version=(
            item.strategy_version
        ),
        config_version=(
            item.config_version
        ),
        config_fingerprint=(
            item.config_fingerprint
        ),
        instrument_id=1,
        timeframe="1m",
        state_schema_version=1,
        last_market_observation_revision_id=(
            revision_id
        ),
        captured_at=NOW,
        state_json={
            "schema_version": 1,
            "previous_ema20": 1.0,
            "previous_ema60": 2.0,
        },
    )


def test_strategy_instance_fingerprint_and_registry_version_scope_validation():
    item = instance()

    assert (
        item.config_fingerprint
        == config_fingerprint(
            item.config_json
        )
    )

    with pytest.raises(
        ValidationError,
        match="fingerprint",
    ):
        StrategyInstance(
            **{
                **item.model_dump(),
                "config_fingerprint": "bad",
            }
        )

    registry = StrategyRegistry()

    registry.register(
        "EMA_CROSS",
        "1.0.0",
        EMACrossStrategy,
    )

    assert isinstance(
        registry.create_instance(
            item
        ),
        EMACrossStrategy,
    )

    with pytest.raises(
        ValueError,
        match="version",
    ):
        registry.create_instance(
            instance(
                version="2"
            )
        )

    with pytest.raises(
        ValueError,
        match="scope",
    ):
        registry.create_instance(
            instance(
                config={
                    "symbol": "TX",
                    "timeframe": "5m",
                }
            )
        )


@pytest.mark.parametrize(
    "factory,row1,row2",
    [
        (
            lambda: EMACrossStrategy("TX"),
            {
                "ema_20": 1,
                "ema_60": 2,
            },
            {
                "ema_20": 3,
                "ema_60": 2,
                "timestamp": NOW,
                "close": 1,
            },
        ),
        (
            lambda: TrendStateStrategy("TX"),
            {
                "trend_state": "SIDEWAYS",
            },
            {
                "trend_state": "UP",
                "timestamp": NOW,
                "close": 1,
            },
        ),
        (
            lambda: TrendStateExitStrategy("TX"),
            {
                "trend_state": "UP",
                "timestamp": NOW,
                "close": 1,
            },
            {
                "trend_state": "DOWN",
                "timestamp": NOW,
                "close": 1,
            },
        ),
    ],
)
def test_explicit_codec_restores_next_transition_equivalent(
    factory,
    row1,
    row2,
):
    uninterrupted = factory()
    uninterrupted.on_bar(
        row1
    )

    state = (
        uninterrupted.export_state()
    )

    restored = factory()

    assert isinstance(
        restored,
        StatefulStrategy,
    )

    restored.restore_state(
        state
    )

    assert (
        restored.on_bar(
            row2
        )
        == uninterrupted.on_bar(
            row2
        )
    )


def test_strategy_codecs_reject_invalid_payload():
    for strategy in (
        EMACrossStrategy("TX"),
        TrendStateStrategy("TX"),
        TrendStateExitStrategy("TX"),
    ):
        with pytest.raises(
            ValueError
        ):
            strategy.restore_state(
                {
                    "schema_version": 999,
                }
            )


def test_strategy_state_snapshot_is_immutable_scoped_and_versioned():
    item = instance()
    snapshot = make_snapshot(
        item
    )

    with pytest.raises(
        ValidationError
    ):
        snapshot.timeframe = "5m"

    assert (
        snapshot
        .last_market_observation_revision_id
        == MOR1_A
    )

    assert (
        snapshot.last_market_observation_id
        == MOR1_A
    )


def test_valid_mor1_legacy_alias_normalizes_to_canonical():
    item = instance()

    snapshot = StrategyStateSnapshot(
        snapshot_id="SS-ALIAS",
        strategy_instance_id=(
            item.strategy_instance_id
        ),
        strategy_id=item.strategy_id,
        strategy_version=(
            item.strategy_version
        ),
        config_version=(
            item.config_version
        ),
        config_fingerprint=(
            item.config_fingerprint
        ),
        instrument_id=1,
        timeframe="1m",
        state_schema_version=1,
        last_market_observation_id=MOR1_A,
        captured_at=NOW,
        state_json={
            "schema_version": 1,
            "previous_ema20": 1.0,
            "previous_ema60": 2.0,
        },
    )

    assert (
        snapshot
        .last_market_observation_revision_id
        == MOR1_A
    )


def test_arbitrary_bar_id_cannot_become_recovery_authority():
    item = instance()

    with pytest.raises(
        ValidationError,
        match="mor1",
    ):
        StrategyStateSnapshot(
            snapshot_id="SS-BAR",
            strategy_instance_id=(
                item.strategy_instance_id
            ),
            strategy_id=item.strategy_id,
            strategy_version=(
                item.strategy_version
            ),
            config_version=(
                item.config_version
            ),
            config_fingerprint=(
                item.config_fingerprint
            ),
            instrument_id=1,
            timeframe="1m",
            state_schema_version=1,
            last_market_observation_id=(
                "BAR-1"
            ),
            captured_at=NOW,
            state_json={
                "schema_version": 1,
                "previous_ema20": 1.0,
                "previous_ema60": 2.0,
            },
        )


def test_legacy_canonical_disagreement_fails_closed():
    item = instance()

    values = (
        make_snapshot(
            item
        ).model_dump()
    )

    values[
        "last_market_observation_id"
    ] = MOR1_B

    with pytest.raises(
        ValidationError,
        match="disagree",
    ):
        StrategyStateSnapshot(
            **values
        )


def test_c17_state_schema_and_source_context_are_exact_recovery_authority() -> None:
    from strategy.instance import (
        CanonicalInstrumentBindingProvenance,
    )
    from strategy.recovery import (
        StrategyAuthorityRef,
        StrategyDurableStateReference,
        StrategyGoverningContext,
        StrategyGoverningTransitionAuthority,
        StrategyGoverningTransitionIntegrityError,
        StrategyStateSchemaReference,
        evaluate_governing_transition,
    )

    base = instance()
    item = base.model_copy(
        update={
            "instrument_binding_provenance": (
                CanonicalInstrumentBindingProvenance(
                    instrument_id=1,
                    authority_id="CANONICAL-INSTRUMENT-PROVISIONING",
                    authority_version="V1",
                    reference_id="BIND-C17-STATE",
                )
            )
        }
    )
    snapshot = make_snapshot(item)

    source = StrategyGoverningContext(
        strategy_instance_id=item.strategy_instance_id,
        strategy_id=item.strategy_id,
        config_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-CONFIG",
            authority_version="C1",
        ),
        config_version=item.config_version,
        config_fingerprint=item.config_fingerprint,
        implementation_revision=item.strategy_version,
        instrument_id=item.instrument_id,
        instrument_binding_provenance=(
            item.instrument_binding_provenance
        ),
        timeframe=item.timeframe,
        decision_policy_version="DP-1",
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id=item.strategy_id,
            schema_version=snapshot.state_schema_version,
        ),
    )
    target = source.model_copy(
        update={"decision_policy_version": "DP-2"}
    )
    authority = StrategyGoverningTransitionAuthority(
        transition_id="TR-C17-STATE",
        strategy_instance_id=item.strategy_instance_id,
        source_context=source,
        target_context=target,
        compatibility_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-COMPATIBILITY",
            authority_version="V1",
        ),
        transition_policy=StrategyAuthorityRef(
            authority_id="GOVERNING-TRANSITION",
            authority_version="V1",
        ),
    )
    durable = StrategyDurableStateReference(
        snapshot_id=snapshot.snapshot_id,
        strategy_instance_id=snapshot.strategy_instance_id,
        strategy_id=snapshot.strategy_id,
        config_version=snapshot.config_version,
        config_fingerprint=snapshot.config_fingerprint,
        implementation_revision=snapshot.strategy_version,
        instrument_id=snapshot.instrument_id,
        timeframe=snapshot.timeframe,
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id=snapshot.strategy_id,
            schema_version=snapshot.state_schema_version,
        ),
    )

    assert evaluate_governing_transition(
        authority=authority,
        source_instance=item,
        durable_state=durable,
    ).value == "PRE_TRANSITION"

    with pytest.raises(
        StrategyGoverningTransitionIntegrityError,
        match="PRE_TRANSITION durable state",
    ):
        evaluate_governing_transition(
            authority=authority,
            source_instance=item,
            durable_state=durable.model_copy(
                update={
                    "state_schema_reference": (
                        StrategyStateSchemaReference(
                            strategy_id=snapshot.strategy_id,
                            schema_version=2,
                        )
                    )
                }
            ),
        )
