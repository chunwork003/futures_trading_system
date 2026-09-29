from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from persistence.reconciliation import (
    ReconciliationCaseVersion,
    reconciliation_blocker_semantic_fingerprint,
)
from persistence.postgres.reconciliation import PostgresReconciliationCaseRepository
from trading.account import AccountPosition, BrokerAccount, PositionDirection
from trading.reconciliation import (
    ReconciliationCaseError,
    ReconciliationCaseState,
    ReconciliationPolicy,
    ReconciliationStatus,
    compare_positions,
    create_reconciliation_case,
    resolve_reconciliation_case,
)

NOW = datetime(2026, 9, 27, tzinfo=timezone.utc)
ACCOUNT_A = BrokerAccount(broker="SINOPAC", account_ref="A")
ACCOUNT_B = BrokerAccount(broker="SINOPAC", account_ref="B")


def _case(account: BrokerAccount = ACCOUNT_A):
    position = AccountPosition(
        broker=account.broker,
        account_ref=account.account_ref,
        instrument_id=1,
        contract_id=2,
        direction=PositionDirection.LONG,
        quantity=1,
    )
    return create_reconciliation_case(
        case_id="CASE-1",
        account=account,
        result=compare_positions(position, None),
        policy=ReconciliationPolicy.STRICT_HALT,
    )


class _Connection:
    def __init__(self, rows):
        self.rows=list(rows); self.statements=[]; self.commits=0; self.rollbacks=0
    def cursor(self):
        owner=self
        class Cursor:
            def __enter__(self): return self
            def __exit__(self,*args): return False
            def execute(self,sql,params=None): owner.statements.append((sql,params))
            def fetchone(self): return owner.rows.pop(0)
            def fetchall(self): return owner.rows.pop(0)
        return Cursor()


def test_case_has_explicit_immutable_account_scope_and_resolution_preserves_it() -> None:
    case=_case()
    assert case.account == ACCOUNT_A
    assert resolve_reconciliation_case(case,resolution_note="reviewed").account == ACCOUNT_A
    with pytest.raises(ValidationError):
        case.account = ACCOUNT_B


def test_unknown_result_requires_explicit_account_scope() -> None:
    from trading.reconciliation import ReconciliationResult, ReconciliationStatus
    result=ReconciliationResult(status=ReconciliationStatus.UNKNOWN_EXTERNAL_STATE,expected=None,actual=None,evidence=("provider unavailable",))
    with pytest.raises(ReconciliationCaseError,match="account is required"):
        create_reconciliation_case(case_id="UNKNOWN",result=result,policy=ReconciliationPolicy.STRICT_HALT)


def test_version_identity_matches_embedded_case() -> None:
    with pytest.raises(ValidationError,match="case_id"):
        ReconciliationCaseVersion(case_id="OTHER",version=1,recorded_at=NOW,reconciliation_case=_case())


def test_postgres_append_rejects_cross_account_scope_drift_without_commit() -> None:
    connection=_Connection([("SINOPAC","A",4,3,0,True),("SINOPAC","B",None)])
    version=ReconciliationCaseVersion(case_id="CASE-1",version=2,recorded_at=NOW,reconciliation_case=_case())
    with pytest.raises(ReconciliationCaseError,match="scope"):
        PostgresReconciliationCaseRepository(connection).append(version)
    assert connection.commits == connection.rollbacks == 0


def test_d1b_case_append_locks_fence_before_material_and_advances_new_blocker() -> None:
    connection=_Connection([("SINOPAC","A",4,3,0,True),None,(1,)])
    version=ReconciliationCaseVersion(case_id="CASE-1",version=1,recorded_at=NOW,reconciliation_case=_case())
    PostgresReconciliationCaseRepository(connection).append(version)
    sqls=[sql for sql,_ in connection.statements]
    assert "account_recovery_controls" in sqls[0] and "FOR UPDATE" in sqls[0]
    assert "reconciliation_case_history" in sqls[1] and "FOR UPDATE" in sqls[1]
    assert sqls[2].startswith("INSERT INTO trading.reconciliation_case_history")
    assert "readiness_revision=readiness_revision+1" in sqls[3]
    assert not any("ingress_version" in sql for sql in sqls)
    assert connection.commits == connection.rollbacks == 0


def test_d1b_case_audit_only_version_does_not_advance_readiness() -> None:
    original=ReconciliationCaseVersion(case_id="CASE-1",version=1,recorded_at=NOW,reconciliation_case=_case(),actor_ref="A")
    audit_only=original.model_copy(update={"version":2,"actor_ref":"B","evidence":("audit",)})
    connection=_Connection([("SINOPAC","A",4,3,7,True),("SINOPAC","A",original.model_dump(mode="json"))])
    PostgresReconciliationCaseRepository(connection).append(audit_only)
    assert not any("readiness_revision=readiness_revision+1" in sql for sql,_ in connection.statements)


def test_d1b_case_resolution_advances_readiness_once() -> None:
    original=ReconciliationCaseVersion(case_id="CASE-1",version=1,recorded_at=NOW,reconciliation_case=_case())
    resolved=ReconciliationCaseVersion(case_id="CASE-1",version=2,recorded_at=NOW,reconciliation_case=resolve_reconciliation_case(_case(),resolution_note="reviewed"))
    connection=_Connection([("SINOPAC","A",4,3,2,True),("SINOPAC","A",original.model_dump(mode="json")),(3,)])
    PostgresReconciliationCaseRepository(connection).append(resolved)
    assert sum("readiness_revision=readiness_revision+1" in sql for sql,_ in connection.statements) == 1


def test_d1b_case_material_transition_advances_but_inactive_control_does_not() -> None:
    original=ReconciliationCaseVersion(case_id="CASE-1",version=1,recorded_at=NOW,reconciliation_case=_case())
    changed=original.model_copy(update={"version":2,"reconciliation_case":_case().model_copy(update={"policy":ReconciliationPolicy.MANUAL_REVIEW})})
    active=_Connection([("SINOPAC","A",4,3,8,True),("SINOPAC","A",original.model_dump(mode="json")),(9,)])
    PostgresReconciliationCaseRepository(active).append(changed)
    assert sum("readiness_revision=readiness_revision+1" in sql for sql,_ in active.statements) == 1
    inactive=_Connection([None,("SINOPAC","A",original.model_dump(mode="json"))])
    PostgresReconciliationCaseRepository(inactive).append(changed)
    assert not any("readiness_revision=readiness_revision+1" in sql for sql,_ in inactive.statements)


def test_unresolved_query_is_exact_account_scoped_and_legacy_ambiguity_fails() -> None:
    empty=_Connection([(False,),[]])
    assert PostgresReconciliationCaseRepository(empty).unresolved(ACCOUNT_A) == ()
    sql,params=empty.statements[1]
    assert "broker=%s AND account_ref=%s" in sql
    assert params == ("SINOPAC","A")
    ambiguous=_Connection([(True,)])
    with pytest.raises(ReconciliationCaseError,match="legacy"):
        PostgresReconciliationCaseRepository(ambiguous).unresolved(ACCOUNT_A)


def test_case_is_control_evidence_without_economic_or_broker_actions() -> None:
    case=_case()
    for name in ("submit","cancel","repair","advance_account_head"):
        assert not hasattr(case,name)


def test_c1_semantic_fingerprint_excludes_audit_wrapper_metadata() -> None:
    original=ReconciliationCaseVersion(case_id="CASE-1",version=1,recorded_at=NOW,reconciliation_case=_case(),actor_ref="A",evidence=("first",))
    audit_only=original.model_copy(update={"version":2,"recorded_at":datetime(2026,9,28,tzinfo=timezone.utc),"actor_ref":"B","evidence":("second",)})
    assert reconciliation_blocker_semantic_fingerprint((original,)) == reconciliation_blocker_semantic_fingerprint((audit_only,))


def test_c1_semantic_fingerprint_changes_with_readiness_material() -> None:
    original=ReconciliationCaseVersion(case_id="CASE-1",version=1,recorded_at=NOW,reconciliation_case=_case())
    changed_result=original.model_copy(update={"reconciliation_case":_case().model_copy(update={"result":_case().result.model_copy(update={"status":ReconciliationStatus.QUANTITY_MISMATCH})})})
    changed_policy=original.model_copy(update={"reconciliation_case":_case().model_copy(update={"policy":ReconciliationPolicy.MANUAL_REVIEW})})
    changed_state=original.model_copy(update={"reconciliation_case":_case().model_copy(update={"state":ReconciliationCaseState.REVIEW_REQUIRED})})
    baseline=reconciliation_blocker_semantic_fingerprint((original,))
    assert reconciliation_blocker_semantic_fingerprint((changed_result,)) != baseline
    assert reconciliation_blocker_semantic_fingerprint((changed_policy,)) != baseline
    assert reconciliation_blocker_semantic_fingerprint((changed_state,)) != baseline
