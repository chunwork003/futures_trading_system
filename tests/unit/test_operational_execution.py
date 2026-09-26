from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from persistence.account import AccountPositionSnapshot
from persistence.contracts import PersistenceConflictError
from persistence.events import EventAppendResult, EventAppendStatus
from persistence.execution import ExecutionPersistenceService, order_event_as_trading_event
from trading.account import AccountPosition, PositionDirection
from trading.execution import (
    ExecutionTriggerRef, Fill, Order, OrderEvent, OrderIntent,
    OrderStateTransitionError, OrderStatus, OrderType,
    PositionEffect, validate_order_event_transition,
)

NOW = datetime(2026, 9, 25, 1, 0, tzinfo=timezone.utc)


def event(sequence=0, previous=None, status=OrderStatus.PENDING, **updates):
    values = dict(event_id=f"EV-{sequence}", order_id="ORD-1", correlation_id="CORR-1",
                  causation_id="INT-1" if sequence == 0 else f"EV-{sequence-1}",
                  idempotency_key=f"KEY-{sequence}", sequence=sequence,
                  previous_status=previous, status=status, occurred_at=NOW,
                  received_at=NOW)
    values.update(updates); return OrderEvent(**values)


def order(**updates):
    values = dict(order_id="ORD-1", intent_id="INT-1", correlation_id="CORR-1",
                  broker_client_order_ref="CLIENT-ORD-1",
                  instrument_id=1, contract_id=101, direction=PositionDirection.LONG,
                  position_effect=PositionEffect.OPEN, order_type=OrderType.MARKET,
                  quantity=2, status=OrderStatus.PENDING, created_at=NOW, updated_at=NOW)
    values.update(updates); return Order(**values)


def fill(**updates):
    values = dict(fill_id="FILL-1", order_id="ORD-1", event_id="EV-1",
                  correlation_id="CORR-1", causation_id="EV-1", quantity=1,
                  price=Decimal("20000.25"), occurred_at=NOW)
    values.update(updates); return Fill(**values)


def test_canonical_models_are_immutable_exact_and_utc() -> None:
    item = order(limit_price=Decimal("20000.25"))
    assert item.limit_price == Decimal("20000.25")
    with pytest.raises(ValidationError): item.status = OrderStatus.FILLED
    with pytest.raises(ValidationError): order(limit_price=20000.25)
    with pytest.raises(ValidationError): fill(occurred_at=datetime(2026, 1, 1))


def test_creation_and_exact_legal_transition_matrix() -> None:
    creation = event()
    validate_order_event_transition(None, creation)
    legal = {
        OrderStatus.PENDING: (OrderStatus.SUBMITTED, OrderStatus.CANCELLED, OrderStatus.REJECTED),
        OrderStatus.SUBMITTED: (OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED),
        OrderStatus.PARTIALLY_FILLED: (OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED, OrderStatus.CANCELLED),
    }
    for previous, targets in legal.items():
        prior = event(sequence=1, previous=OrderStatus.PENDING, status=previous)
        for target in targets:
            validate_order_event_transition(prior, event(sequence=2, previous=previous, status=target))


def test_sequence_gap_identity_illegal_and_terminal_transitions_reject() -> None:
    prior = event(sequence=1, previous=OrderStatus.PENDING, status=OrderStatus.SUBMITTED)
    for current in (
        event(sequence=3, previous=OrderStatus.SUBMITTED, status=OrderStatus.FILLED),
        event(sequence=2, previous=OrderStatus.PENDING, status=OrderStatus.FILLED),
        event(sequence=2, previous=OrderStatus.SUBMITTED, status=OrderStatus.PENDING),
    ):
        with pytest.raises(OrderStateTransitionError): validate_order_event_transition(prior, current)
    terminal = event(sequence=1, previous=OrderStatus.SUBMITTED, status=OrderStatus.FILLED)
    with pytest.raises(OrderStateTransitionError, match="terminal"):
        validate_order_event_transition(terminal, event(sequence=2, previous=OrderStatus.FILLED, status=OrderStatus.CANCELLED))


def test_order_event_ledger_mapping_preserves_provenance() -> None:
    mapped = order_event_as_trading_event(event())
    assert (mapped.source, mapped.entity_type, mapped.entity_id) == ("OMS", "ORDER", "ORD-1")
    assert mapped.idempotency_scope == "ORDER_EVENT:ORD-1"
    assert mapped.correlation_id == "CORR-1" and mapped.causation_id == "INT-1"


class Uow:
    def __init__(self): self.committed=False; self.rolled=False
    def __enter__(self): return self
    def commit(self): self.committed=True
    def rollback(self): self.rolled=True
    def __exit__(self, typ, exc, tb):
        if not self.committed: self.rolled=True
        return False


class Repo:
    def __init__(self, fail=None, duplicate=False): self.fail=fail; self.duplicate=duplicate; self.calls=[]
    def append(self, value):
        self.calls.append(value)
        if self.fail: raise RuntimeError(self.fail)
        if hasattr(value, "event_type"):
            return EventAppendResult(status=EventAppendStatus.DUPLICATE if self.duplicate else EventAppendStatus.APPENDED, event_id=value.event_id)
        return True
    def save(self, value, *, expected_version):
        self.calls.append(value)
        if self.fail: raise RuntimeError(self.fail)


@pytest.mark.parametrize("failure", ["fill", "order", "snapshot"])
def test_atomic_service_rolls_back_each_material_failure(failure: str) -> None:
    uow=Uow(); ledger=Repo(); fills=Repo("fail" if failure=="fill" else None)
    orders=Repo("fail" if failure=="order" else None); snapshots=Repo("fail" if failure=="snapshot" else None)
    service=ExecutionPersistenceService(uow_factory=lambda:uow, repositories=lambda _: (ledger,fills,orders,snapshots))
    snapshot=AccountPositionSnapshot(snapshot_id="S1", broker="SINOPAC", account_ref="A", effective_at=NOW, recorded_at=NOW, source_event_id="EV-0", positions=())
    with pytest.raises(RuntimeError):
        service.apply(event=event(), previous_event=None, fills=(fill(event_id="EV-0", causation_id="EV-0"),), order=order(), expected_version=-1, expected_snapshot=snapshot)
    assert uow.rolled and not uow.committed


def test_duplicate_event_has_no_duplicate_economic_effect() -> None:
    uow=Uow(); ledger=Repo(duplicate=True); fills=Repo(); orders=Repo(); snapshots=Repo()
    service=ExecutionPersistenceService(uow_factory=lambda:uow, repositories=lambda _: (ledger,fills,orders,snapshots))
    assert service.apply(event=event(), previous_event=None, fills=(fill(),), order=order(), expected_version=-1) is EventAppendStatus.DUPLICATE
    assert not fills.calls and not orders.calls and not uow.committed


def test_atomic_service_rejects_broken_provenance_chain() -> None:
    uow=Uow(); ledger=Repo(); fills=Repo(); orders=Repo(); snapshots=Repo()
    service=ExecutionPersistenceService(uow_factory=lambda:uow, repositories=lambda _: (ledger,fills,orders,snapshots))
    with pytest.raises(ValueError, match="causation"):
        service.apply(event=event(causation_id="WRONG"), previous_event=None, fills=(), order=order(), expected_version=-1)
    assert uow.rolled and not uow.committed


def test_material_fill_requires_complete_expected_snapshot() -> None:
    uow=Uow(); service=ExecutionPersistenceService(
        uow_factory=lambda:uow,
        repositories=lambda _: (Repo(),Repo(),Repo(),Repo()),
    )
    with pytest.raises(ValueError, match="complete expected-position snapshot"):
        service.apply(
            event=event(), previous_event=None,
            fills=(fill(event_id="EV-0",causation_id="EV-0"),),
            order=order(), expected_version=-1,
        )
    assert uow.rolled and not uow.committed


MOR1_A = "mor1_" + ("a" * 64)


def test_execution_trigger_ref_requires_exact_mor1():
    trigger = ExecutionTriggerRef(
        market_observation_revision_id=(
            MOR1_A
        )
    )

    assert (
        trigger.market_observation_revision_id
        == MOR1_A
    )

    with pytest.raises(
        ValidationError,
        match="mor1",
    ):
        ExecutionTriggerRef(
            market_observation_revision_id=(
                "BAR-1"
            )
        )


def test_order_intent_trigger_reference_is_optional_and_exact():
    plain = OrderIntent(
        intent_id="INT-C25-1",
        correlation_id="CORR-C25-1",
        position_direction=(
            PositionDirection.LONG
        ),
        position_effect=(
            PositionEffect.OPEN
        ),
        quantity=1,
    )

    assert (
        plain.execution_trigger_ref
        is None
    )

    trigger = ExecutionTriggerRef(
        market_observation_revision_id=(
            MOR1_A
        )
    )

    item = OrderIntent(
        intent_id="INT-C25-2",
        correlation_id="CORR-C25-2",
        position_direction=(
            PositionDirection.LONG
        ),
        position_effect=(
            PositionEffect.OPEN
        ),
        quantity=1,
        execution_trigger_ref=trigger,
    )

    assert (
        item.execution_trigger_ref
        == trigger
    )
