from datetime import datetime, timezone

import pytest

from persistence.account_authority import (
    AccountAuthorityCommit,
    AccountAuthorityCommitService,
    AccountStateHead,
)
from persistence.events import EventAppendResult, EventAppendStatus
from persistence.execution import DurablePendingSubmissionService, ExecutionPersistenceService
from persistence.strategy_state import StrategyStateSnapshot
from trading.account import PositionDirection
from trading.execution import Order, OrderEvent, OrderStatus, OrderType, PositionEffect


NOW = datetime(2026, 9, 27, 2, tzinfo=timezone.utc)


class Uow:
    def __init__(self): self.committed = False; self.rolled = False; self.active = False
    def __enter__(self): self.active = True; return self
    def commit(self): self.committed = True
    def rollback(self): self.rolled = True
    def __exit__(self, typ, exc, tb):
        self.active = False
        if not self.committed: self.rolled = True
        return False


class AuthorityRepo:
    def __init__(self):
        self.head = AccountStateHead(broker="SINOPAC", account_ref="A", current_revision=1, initialized=True)
        self.receipt = None; self.checkpoint = None
    def get_receipt(self, value): return self.receipt
    def lock_head(self, broker, account_ref): return self.head
    def lock_or_create_reserved_head(self, broker, account_ref): return self.head
    def get_head(self, broker, account_ref): return self.head
    def get_checkpoint(self, broker, account_ref, revision): return self.checkpoint
    def append_checkpoint(self, value): self.checkpoint = value
    def advance_head(self, value, *, expected_revision): self.head = value
    def append_receipt(self, value): self.receipt = value


class Repo:
    def __init__(self, fail=False): self.values = []; self.fail = fail
    def append(self, value):
        if self.fail: raise RuntimeError("material write failed")
        self.values.append(value)
        if hasattr(value, "event_type"):
            return EventAppendResult(status=EventAppendStatus.APPENDED, event_id=value.event_id)
        return True
    def save(self, value, *, expected_version):
        if self.fail: raise RuntimeError("material write failed")
        self.values.append(value)


def pending_order() -> Order:
    return Order(
        order_id="ORD-1", intent_id="INT-1", correlation_id="CORR-1",
        broker_client_order_ref="CLIENT-1", instrument_id=1, contract_id=101,
        direction=PositionDirection.LONG, position_effect=PositionEffect.OPEN,
        order_type=OrderType.MARKET, quantity=1, status=OrderStatus.PENDING,
        created_at=NOW, updated_at=NOW,
    )


def pending_event() -> OrderEvent:
    return OrderEvent(
        event_id="EV-0", order_id="ORD-1", correlation_id="CORR-1",
        causation_id="INT-1", idempotency_key="PENDING-1", sequence=0,
        previous_status=None, status=OrderStatus.PENDING,
        occurred_at=NOW, received_at=NOW,
    )


def mutation() -> AccountAuthorityCommit:
    return AccountAuthorityCommit(
        authority_commit_id="AUTH-C05-1", mutation_fingerprint="FP-C05-1",
        broker="SINOPAC", account_ref="A", expected_head_revision=1,
        expected_snapshot_id="EXPECTED-SNAPSHOT-1", recorded_at=NOW,
    )


def strategy_snapshot() -> StrategyStateSnapshot:
    return StrategyStateSnapshot(
        snapshot_id="STRATEGY-SNAPSHOT-1", strategy_instance_id="INSTANCE-1",
        strategy_id="EMA_CROSS", strategy_version="1", config_version="1",
        config_fingerprint="FINGERPRINT", instrument_id=1, timeframe="1m",
        state_schema_version=1,
        last_market_observation_revision_id="mor1_" + "a" * 64,
        captured_at=NOW, state_json={"previous_ema20": "1"},
    )


def build(*, strategy_fail=False, order_fail=False):
    uow = Uow(); authority = AuthorityRepo()
    ledger, fills, orders, snapshots = Repo(), Repo(), Repo(order_fail), Repo()
    strategies = Repo(strategy_fail)
    execution = ExecutionPersistenceService(
        uow_factory=lambda: uow,
        repositories=lambda _: (ledger, fills, orders, snapshots),
    )
    service = DurablePendingSubmissionService(
        authority_service=AccountAuthorityCommitService(
            uow_factory=lambda: uow, repository=lambda _: authority,
        ),
        execution_service=execution,
        strategy_repository=lambda _: strategies,
    )
    return service, uow, authority, ledger, orders, strategies


def test_pending_order_and_material_strategy_state_share_authority_commit() -> None:
    service, uow, authority, ledger, orders, strategies = build()
    receipt = service.commit_pending(
        mutation=mutation(), event=pending_event(), order=pending_order(),
        material_strategy_snapshots=(strategy_snapshot(),),
    )
    assert receipt.committed_revision == 2
    assert receipt.expected_snapshot_id == "EXPECTED-SNAPSHOT-1"
    assert authority.checkpoint.expected_snapshot_id == "EXPECTED-SNAPSHOT-1"
    assert ledger.values and orders.values and strategies.values
    assert orders.values[0].broker_client_order_ref == "CLIENT-1"
    assert uow.committed and not uow.active


def test_hold_only_evaluation_is_not_persisted_implicitly() -> None:
    service, _, _, _, _, strategies = build()
    service.commit_pending(mutation=mutation(), event=pending_event(), order=pending_order())
    assert strategies.values == []


@pytest.mark.parametrize("failure", ["order", "strategy"])
def test_material_failure_rolls_back_complete_boundary_without_broker_io(failure: str) -> None:
    service, uow, _, _, _, _ = build(
        order_fail=failure == "order", strategy_fail=failure == "strategy"
    )
    with pytest.raises(RuntimeError, match="material write failed"):
        service.commit_pending(
            mutation=mutation(), event=pending_event(), order=pending_order(),
            material_strategy_snapshots=(strategy_snapshot(),),
        )
    assert uow.rolled and not uow.committed and not uow.active
    assert not hasattr(service, "submit") and not hasattr(service, "broker")


def test_duplicate_authority_receipt_does_not_repeat_material_effects() -> None:
    service, _, _, ledger, orders, strategies = build()
    first = service.commit_pending(
        mutation=mutation(), event=pending_event(), order=pending_order(),
        material_strategy_snapshots=(strategy_snapshot(),),
    )
    second = service.commit_pending(
        mutation=mutation(), event=pending_event(), order=pending_order(),
        material_strategy_snapshots=(strategy_snapshot(),),
    )
    assert second == first
    assert len(ledger.values) == len(orders.values) == len(strategies.values) == 1
