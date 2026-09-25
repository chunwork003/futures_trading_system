from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from persistence.account import AccountPositionSnapshot, BrokerPositionObservation, project_expected_position
from persistence.reconciliation import ReconciliationCaseVersion, blocking_case_state
from trading.account import AccountPosition, AccountSnapshot, BrokerPositionSnapshot, PositionDirection
from trading.execution import Fill, OrderIntent, PositionEffect, PositionEffectValidationError
from trading.reconciliation import ReconciliationCaseState, ReconciliationPolicy, create_reconciliation_case, compare_positions, resolve_reconciliation_case

NOW=datetime(2026,9,25,1,tzinfo=timezone.utc)


def intent(effect=PositionEffect.OPEN, direction=PositionDirection.LONG): return OrderIntent(intent_id="I",correlation_id="C",position_direction=direction,position_effect=effect,quantity=1)
def fill(quantity=1): return Fill(fill_id="F",order_id="O",event_id="E",correlation_id="C",causation_id="E",quantity=quantity,price=Decimal("1"),occurred_at=NOW)
def position(quantity=2,direction=PositionDirection.LONG): return AccountPosition(broker="SINOPAC",account_ref="A",instrument_id=1,contract_id=2,direction=direction,quantity=quantity)


def test_expected_projection_open_add_reduce_partial_close_and_flat() -> None:
    opened=project_expected_position(None,intent=intent(),fill=fill(),broker="SINOPAC",account_ref="A",instrument_id=1,contract_id=2)
    added=project_expected_position(opened,intent=intent(),fill=fill(2),broker="SINOPAC",account_ref="A",instrument_id=1,contract_id=2)
    reduced=project_expected_position(added,intent=intent(PositionEffect.REDUCE),fill=fill(),broker="SINOPAC",account_ref="A",instrument_id=1,contract_id=2)
    partial=project_expected_position(reduced,intent=intent(PositionEffect.CLOSE),fill=fill(),broker="SINOPAC",account_ref="A",instrument_id=1,contract_id=2)
    flat=project_expected_position(partial,intent=intent(PositionEffect.CLOSE),fill=fill(),broker="SINOPAC",account_ref="A",instrument_id=1,contract_id=2)
    assert [opened.quantity,added.quantity,reduced.quantity,partial.quantity] == [1,3,2,1]
    assert flat is None


def test_expected_projection_rejects_reverse_identity_and_invalid_reduce() -> None:
    with pytest.raises(PositionEffectValidationError, match="opposite"):
        project_expected_position(position(),intent=intent(direction=PositionDirection.SHORT),fill=fill(),broker="SINOPAC",account_ref="A",instrument_id=1,contract_id=2)
    with pytest.raises(PositionEffectValidationError, match="identity"):
        project_expected_position(position(),intent=intent(),fill=fill(),broker="SINOPAC",account_ref="OTHER",instrument_id=1,contract_id=2)
    with pytest.raises(PositionEffectValidationError, match="REDUCE"):
        project_expected_position(position(1),intent=intent(PositionEffect.REDUCE),fill=fill(),broker="SINOPAC",account_ref="A",instrument_id=1,contract_id=2)


def test_complete_expected_and_actual_batches_allow_explicit_flat() -> None:
    expected=AccountPositionSnapshot(snapshot_id="S",broker="sinopac",account_ref="A",effective_at=NOW,recorded_at=NOW,source_event_id="E",positions=())
    actual=BrokerPositionObservation(observation_id="B",broker="sinopac",account_ref="A",observed_at=NOW,recorded_at=NOW,positions=())
    assert expected.positions == actual.positions == ()
    bad=BrokerPositionSnapshot(broker="SINOPAC",account_ref="A",instrument_id=1,contract_id=2,direction=PositionDirection.LONG,quantity=1,observed_at=NOW+timedelta(seconds=1))
    with pytest.raises(ValidationError): BrokerPositionObservation(observation_id="B",broker="SINOPAC",account_ref="A",observed_at=NOW,recorded_at=NOW,positions=(bad,))


def test_account_snapshot_exact_money_utc_and_observation_required() -> None:
    snapshot=AccountSnapshot(snapshot_id="S",broker="sinopac",account_ref="A",observed_at=NOW,recorded_at=NOW,currency="twd",equity=Decimal("100.25"))
    assert snapshot.currency == "TWD" and snapshot.equity == Decimal("100.25")
    with pytest.raises(ValidationError): AccountSnapshot(snapshot_id="S",broker="S",account_ref="A",observed_at=NOW,recorded_at=NOW,currency="TWD")
    with pytest.raises(ValidationError): AccountSnapshot(snapshot_id="S",broker="S",account_ref="A",observed_at=NOW,recorded_at=NOW,currency="TWD",equity=100.0)


def test_reconciliation_case_history_is_append_only_versioned_and_non_corrective() -> None:
    result=compare_positions(position(),None)
    case=create_reconciliation_case(case_id="CASE",result=result,policy=ReconciliationPolicy.STRICT_HALT)
    v1=ReconciliationCaseVersion(case_id="CASE",version=1,recorded_at=NOW,reconciliation_case=case)
    resolved=resolve_reconciliation_case(case,resolution_note="reviewed")
    v2=ReconciliationCaseVersion(case_id="CASE",version=2,recorded_at=NOW,reconciliation_case=resolved,actor_ref="OPS")
    assert v1.reconciliation_case.state is ReconciliationCaseState.HALT
    assert v2.reconciliation_case.state is ReconciliationCaseState.RESOLVED
    assert blocking_case_state((v1,)) is ReconciliationCaseState.HALT
    assert blocking_case_state((v2,)) is None
