from datetime import datetime, timezone
from decimal import Decimal

import pytest

from persistence.account import AccountPositionSnapshot
from persistence.account_authority import AccountAuthorityCommit
from persistence.broker_recovery import BrokerRecoveryExecutionService
from trading.account import PositionDirection
from trading.broker_recovery import (
    BrokerDealEvidence,
    BrokerDealIdentity,
    BrokerRecoveryIntegrityError,
    reconstruct_broker_order,
)
from trading.execution import (
    Fill,
    Order,
    OrderEvent,
    OrderEventProvenance,
    OrderStatus,
    OrderType,
    PositionEffect,
    validate_order_event_transition,
)

NOW = datetime(2026, 9, 27, tzinfo=timezone.utc)


def order(**updates):
    values = dict(
        order_id="ORDER-1", intent_id="INT-1", correlation_id="CORR-1",
        broker_client_order_ref="CLIENT-1", instrument_id=1, contract_id=101,
        direction=PositionDirection.LONG, position_effect=PositionEffect.OPEN,
        order_type=OrderType.MARKET, quantity=2, status=OrderStatus.PENDING,
        created_at=NOW, updated_at=NOW,
    )
    values.update(updates)
    return Order(**values)


def deal(deal_id="D1", quantity=1, price=Decimal("100"), **updates):
    values = dict(
        identity=BrokerDealIdentity(broker="SINOPAC", account_ref="A", deal_id=deal_id),
        order_id="ORDER-1", broker_client_order_ref="CLIENT-1", quantity=quantity,
        price=price, occurred_at=NOW, identity_verified=True,
    )
    values.update(updates)
    return BrokerDealEvidence(**values)


def event(sequence, previous, status, **updates):
    values = dict(
        event_id=f"EVENT-{sequence}", order_id="ORDER-1", correlation_id="CORR-1",
        causation_id="EVENT-0", idempotency_key=f"KEY-{sequence}", sequence=sequence,
        previous_status=previous, status=status, occurred_at=NOW, received_at=NOW,
        provenance=OrderEventProvenance.BROKER_DISCOVERY,
    )
    values.update(updates)
    return OrderEvent(**values)


def test_recovery_provenance_and_direct_pending_fill_transitions_are_explicit():
    assert {item.value for item in OrderEventProvenance} == {
        "LOCAL_OMS", "BROKER_CALLBACK", "BROKER_DISCOVERY"
    }
    prior = event(0, None, OrderStatus.PENDING, causation_id="INT-1")
    for status in (OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED):
        validate_order_event_transition(prior, event(1, OrderStatus.PENDING, status))


def test_reconstruction_requires_exact_verified_deal_identity():
    with pytest.raises(BrokerRecoveryIntegrityError, match="not verified"):
        deal(identity_verified=False)


def test_new_exact_deal_builds_fill_and_partial_economics():
    plan = reconstruct_broker_order(
        order=order(), local_fills=(), evidence=(deal(),),
        event_id="EVENT-1", correlation_id="CORR-1",
    )
    assert plan.status is OrderStatus.PARTIALLY_FILLED
    assert plan.filled_quantity == 1
    assert plan.average_fill_price == Decimal("100")
    assert plan.accepted_fills[0].broker_deal_id == "D1"


def test_complete_fill_set_drives_exact_weighted_economics():
    local = Fill(
        fill_id="F0", order_id="ORDER-1", event_id="EVENT-0",
        correlation_id="CORR-1", causation_id="EVENT-0", quantity=1,
        price=Decimal("100"), occurred_at=NOW, broker_deal_id="D0",
    )
    plan = reconstruct_broker_order(
        order=order(status=OrderStatus.PARTIALLY_FILLED, filled_quantity=1,
                    average_fill_price=Decimal("100")),
        local_fills=(local,), evidence=(deal("D1", price=Decimal("102")),),
        event_id="EVENT-2", correlation_id="CORR-1",
    )
    assert plan.status is OrderStatus.FILLED
    assert plan.filled_quantity == 2
    assert plan.average_fill_price == Decimal("101")


def test_duplicate_deal_is_corroborating_but_conflict_fails_closed():
    local = Fill(
        fill_id="F1", order_id="ORDER-1", event_id="EVENT-1",
        correlation_id="CORR-1", causation_id="EVENT-1", quantity=1,
        price=Decimal("100"), occurred_at=NOW, broker_deal_id="D1",
    )
    same = reconstruct_broker_order(
        order=order(status=OrderStatus.PARTIALLY_FILLED, filled_quantity=1,
                    average_fill_price=Decimal("100")),
        local_fills=(local,), evidence=(deal(),), event_id="EVENT-2",
        correlation_id="CORR-1",
    )
    assert same.accepted_fills == () and same.filled_quantity == 1
    with pytest.raises(BrokerRecoveryIntegrityError, match="conflicts"):
        reconstruct_broker_order(
            order=order(), local_fills=(local,),
            evidence=(deal(price=Decimal("101")),), event_id="EVENT-2",
            correlation_id="CORR-1",
        )


def test_duplicate_evidence_identity_with_conflicting_content_rejected():
    with pytest.raises(BrokerRecoveryIntegrityError, match="conflicting content"):
        reconstruct_broker_order(
            order=order(), local_fills=(),
            evidence=(deal(), deal(price=Decimal("101"))),
            event_id="EVENT-1", correlation_id="CORR-1",
        )


def test_terminal_economics_are_sealed():
    with pytest.raises(BrokerRecoveryIntegrityError, match="sealed"):
        reconstruct_broker_order(
            order=order(status=OrderStatus.FILLED, filled_quantity=2,
                        average_fill_price=Decimal("100")),
            local_fills=(), evidence=(deal(),), event_id="EVENT-3",
            correlation_id="CORR-1",
        )


def test_terminal_exact_duplicate_is_corroborating_without_enrichment():
    local = Fill(
        fill_id="F1", order_id="ORDER-1", event_id="EVENT-1",
        correlation_id="CORR-1", causation_id="EVENT-1", quantity=1,
        price=Decimal("100"), occurred_at=NOW, broker_deal_id="D1",
    )
    plan = reconstruct_broker_order(
        order=order(status=OrderStatus.FILLED, quantity=1, filled_quantity=1,
                    average_fill_price=Decimal("100")),
        local_fills=(local,), evidence=(deal(),), event_id="EVENT-3",
        correlation_id="CORR-1",
    )
    assert plan.accepted_fills == ()


class FillRepo:
    def __init__(self, fills=()): self.fills = fills
    def list_by_order(self, order_id): return self.fills


class Participant:
    def __init__(self, calls, name): self.calls, self.name = calls, name
    def apply(self): self.calls.append(self.name)


class ExecutionService:
    def __init__(self, calls): self.calls = calls; self.kwargs = None
    def participant(self, **kwargs):
        self.kwargs = kwargs
        return Participant(self.calls, "execution")


class AuthorityService:
    def __init__(self): self.calls = []
    def commit(self, mutation, *, participant_factory):
        for participant in participant_factory(object()): participant.apply()
        self.calls.append(mutation)
        return "receipt"


def mutation(snapshot="SNAP-2"):
    return AccountAuthorityCommit(
        authority_commit_id="AUTH-2", mutation_fingerprint="FP-2",
        broker="SINOPAC", account_ref="A", expected_head_revision=5,
        expected_snapshot_id=snapshot, recorded_at=NOW,
    )


def test_recovery_material_and_action_resolution_share_authority_boundary():
    calls = []
    authority = AuthorityService(); execution = ExecutionService(calls)
    service = BrokerRecoveryExecutionService(
        authority_service=authority, execution_service=execution,
        fill_repository=lambda _: FillRepo(),
    )
    snapshot = AccountPositionSnapshot(
        snapshot_id="SNAP-2", broker="SINOPAC", account_ref="A",
        effective_at=NOW, recorded_at=NOW, source_event_id="EVENT-1", positions=(),
    )
    result = service.commit(
        mutation=mutation(), previous_event=event(0, None, OrderStatus.PENDING, causation_id="INT-1"),
        event=event(1, OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED),
        order=order(status=OrderStatus.PARTIALLY_FILLED, filled_quantity=1,
                    average_fill_price=Decimal("100"), version=1),
        expected_version=0, evidence=(deal(),), expected_snapshot=snapshot,
        prior_expected_snapshot_id="SNAP-1",
        additional_participants=lambda _: (Participant(calls, "action-resolution"),),
    )
    assert result == "receipt"
    assert calls == ["execution", "action-resolution"]
    assert execution.kwargs["fills"][0].broker_deal_id == "D1"


def test_status_only_carries_forward_exact_snapshot_and_no_broker_io_surface():
    service = BrokerRecoveryExecutionService(
        authority_service=AuthorityService(), execution_service=ExecutionService([]),
        fill_repository=lambda _: FillRepo(),
    )
    with pytest.raises(ValueError, match="carry forward"):
        service.commit(
            mutation=mutation("DIFFERENT"),
            previous_event=event(0, None, OrderStatus.PENDING, causation_id="INT-1"),
            event=event(1, OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED),
            order=order(status=OrderStatus.PARTIALLY_FILLED, version=1),
            expected_version=0, evidence=(), expected_snapshot=None,
            prior_expected_snapshot_id="SNAP-1",
        )
    assert not hasattr(service, "broker") and not hasattr(service, "submit")
