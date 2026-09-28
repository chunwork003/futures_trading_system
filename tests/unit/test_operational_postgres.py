from pathlib import Path

import pytest

from persistence.account import (
    AccountPositionSnapshot, BrokerObservationIntegrityError,
    BrokerPositionObservation, ExpectedSnapshotIntegrityError,
    ExpectedStateBaselineNotEstablishedError,
)
from persistence.postgres.account import (
    PostgresBrokerPositionObservationRepository,
    PostgresExpectedPositionSnapshotRepository,
)
from persistence.broker_action import (
    BrokerActionAttempt,
    BrokerActionKind,
    BrokerActionResolutionKind,
)
from persistence.postgres.broker_action import PostgresBrokerActionRepository
from persistence.broker_recovery import (
    AccountRecoveryControl,
    BrokerDiscoveryReceipt,
    BrokerReconstructionReceipt,
    BrokerReportApplication,
    BrokerReportApplicationStatus,
    BrokerReportConflictError,
    BrokerReportInboxEntry,
    RecoveryFenceConflictError,
    RecoveryEvidenceAppendStatus,
)
from persistence.postgres.broker_recovery import PostgresBrokerRecoveryRepository
from trading.account import BrokerAccount
from trading.broker_recovery import BrokerDealSetCompleteness, BrokerDiscoveryIntegrity, BrokerDiscoveryResult, BrokerReconstructionPlan, DiscoveryCompleteness, ExactMatchCardinality
from trading.execution import OrderStatus


def test_operational_migration_has_separate_tables_and_required_types_comments() -> None:
    sql = Path(
        "persistence/postgres/migrations/0002_operational_persistence.sql"
    ).read_text(encoding="utf-8")

    tables = (
        "orders",
        "fills",
        "expected_position_snapshots",
        "expected_position_snapshot_items",
        "broker_position_observations",
        "broker_position_observation_items",
        "account_snapshots",
        "reconciliation_case_history",
        "strategy_instances",
        "strategy_state_snapshots",
    )

    for table in tables:
        assert f"CREATE TABLE trading.{table}" in sql
        assert f"COMMENT ON TABLE trading.{table}" in sql

    for token in (
        "NUMERIC",
        "TIMESTAMPTZ",
        "JSONB",
        "PRIMARY KEY",
        "UNIQUE",
        "CHECK",
    ):
        assert token in sql

    assert "event_ledger" not in "\n".join(
        line
        for line in sql.splitlines()
        if line.startswith("CREATE TABLE")
    )


def test_expected_and_actual_storage_are_structurally_separate() -> None:
    sql = Path(
        "persistence/postgres/migrations/0002_operational_persistence.sql"
    ).read_text(encoding="utf-8")

    assert "trading.expected_position_snapshots" in sql
    assert "trading.broker_position_observations" in sql
    assert "UPDATE trading.reconciliation_case_history" not in sql
    assert "DELETE FROM" not in sql


class _Cursor:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=None):
        self.connection.last = (sql, params)

    def fetchone(self):
        return None


class _Connection:
    def __init__(self):
        self.last = None
        self.commits = 0

    def cursor(self):
        return _Cursor(self)

    def commit(self):
        self.commits += 1


def test_expected_repository_latest_as_of_order_and_loader_compatibility() -> None:
    connection = _Connection()
    repository = PostgresExpectedPositionSnapshotRepository(connection)

    with pytest.raises(
        ExpectedStateBaselineNotEstablishedError,
        match="baseline is not established",
    ):
        repository.load_positions(
            BrokerAccount(
                broker="SINOPAC",
                account_ref="A",
            )
        )

    assert (
        "effective_at DESC" in connection.last[0]
        and "recorded_at DESC" in connection.last[0]
        and "snapshot_id DESC" in connection.last[0]
    )

    repository.as_of(
        "SINOPAC",
        "A",
        __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ),
    )

    assert "effective_at<=%s" in connection.last[0]
    assert connection.commits == 0


def test_exact_snapshot_and_observation_reads_are_identity_and_account_scoped() -> None:
    connection = _Connection()
    assert PostgresExpectedPositionSnapshotRepository(connection).get_exact(
        snapshot_id="SNAP-1", broker="SINOPAC", account_ref="A"
    ) is None
    assert "snapshot_id=%s AND broker=%s AND account_ref=%s" in connection.last[0]
    assert PostgresBrokerPositionObservationRepository(connection).get_exact(
        observation_id="OBS-1", broker="SINOPAC", account_ref="A"
    ) is None
    assert "observation_id=%s AND broker=%s AND account_ref=%s" in connection.last[0]


def test_w4r_b1_migration_adds_positive_receipts_without_backfill() -> None:
    sql = Path("persistence/postgres/migrations/0009_trusted_readiness_authority.sql").read_text(encoding="utf-8")
    for table in ("broker_discovery_receipts", "broker_reconstruction_receipts"):
        assert f"CREATE TABLE trading.{table}" in sql
        assert f"COMMENT ON TABLE trading.{table}" in sql
    assert "result_fingerprint" in sql and "output_fingerprint" in sql
    assert "deal_set_completeness" in sql and "COMPLETE" in sql
    assert "INSERT INTO" not in sql


class _ReturningCursor(_Cursor):
    def fetchone(self):
        return (1,)


class _ReturningConnection(_Connection):
    def __init__(self):
        super().__init__(); self.statements = []

    def cursor(self):
        connection = self
        class Cursor(_ReturningCursor):
            def execute(self, sql, params=None):
                connection.last = (sql, params)
                connection.statements.append((sql, params))
        return Cursor(self)


def _broker_attempt() -> BrokerActionAttempt:
    return BrokerActionAttempt(
        attempt_id="ATTEMPT-1", broker="SINOPAC", account_ref="A",
        order_id="ORDER-1", action=BrokerActionKind.SUBMIT,
        broker_client_order_ref="CLIENT-1", command_id="COMMAND-1",
        correlation_id="CORR-1", authorization_id="AUTH-1",
        created_at=__import__("datetime").datetime(
            2026, 9, 27, tzinfo=__import__("datetime").timezone.utc
        ),
    )


def test_broker_action_postgres_conditional_writes_encode_retry_eligibility() -> None:
    connection = _ReturningConnection()
    repository = PostgresBrokerActionRepository(connection)
    item = _broker_attempt()

    repository.reserve_head(item, expected_version=3)
    reserve_sql, reserve_params = connection.last
    assert "unresolved_attempt_id IS NULL" in reserve_sql
    assert "automatic_invocation_eligible=TRUE" in reserve_sql
    assert "automatic_invocation_eligible=FALSE" in reserve_sql
    assert reserve_params[-1] == 3

    material_sql = None
    for kind in (
        BrokerActionResolutionKind.SUCCEEDED,
        BrokerActionResolutionKind.FAILED,
    ):
        repository.resolve_head(item, resolution_kind=kind, expected_version=4)
        current_sql, material_params = connection.last
        assert "unresolved_attempt_id=NULL" in current_sql
        assert "automatic_invocation_eligible=%s" in current_sql
        assert material_params[0] is False
        material_sql = current_sql

    repository.resolve_head(
        item, resolution_kind=BrokerActionResolutionKind.NOT_DISPATCHED,
        expected_version=5,
    )
    retry_sql, retry_params = connection.last
    assert retry_sql == material_sql
    assert retry_params[0] is True
    assert connection.commits == 0


def test_broker_action_migration_encodes_durable_eligibility_without_manual_override() -> None:
    sql = Path(
        "persistence/postgres/migrations/0006_broker_action_safety.sql"
    ).read_text(encoding="utf-8")
    assert "automatic_invocation_eligible BOOLEAN NOT NULL DEFAULT FALSE" in sql
    assert "unresolved_attempt_id IS NULL OR automatic_invocation_eligible = FALSE" in sql
    assert "NOT_DISPATCHED" in sql
    assert "manual_override" not in sql.lower()


def test_broker_recovery_migration_separates_inbox_control_and_continuity() -> None:
    sql = Path(
        "persistence/postgres/migrations/0007_broker_recovery_evidence.sql"
    ).read_text(encoding="utf-8")
    for table in (
        "broker_report_inbox",
        "broker_report_applications",
        "account_recovery_controls",
        "execution_continuity_epochs",
        "broker_sequence_gaps",
    ):
        assert f"CREATE TABLE trading.{table}" in sql
        assert f"COMMENT ON TABLE trading.{table}" in sql
    assert "TIMESTAMPTZ" in sql
    assert "JSONB" in sql
    assert "account_state_heads" not in sql
    assert "recovery_active_at_capture BOOLEAN NOT NULL" in sql
    assert "application_sequence BIGINT NOT NULL" in sql
    assert "UNIQUE (ingress_id, generation, application_sequence)" in sql
    assert "FOREIGN KEY (ingress_id, generation)" in sql


def test_broker_recovery_handoff_is_one_conditional_write_without_commit() -> None:
    connection = _ReturningConnection()
    repository = PostgresBrokerRecoveryRepository(connection)
    control = AccountRecoveryControl(
        broker="SINOPAC",
        account_ref="A",
        generation=4,
        recovery_cut_revision=8,
        ingress_version=12,
        active=False,
        recorded_at=__import__("datetime").datetime(
            2026, 9, 27, tzinfo=__import__("datetime").timezone.utc
        ),
    )

    repository.finalize_handoff(
        control,
        expected_generation=4,
        expected_ingress_version=12,
        expected_readiness_revision=0,
    )

    sql, params = connection.last
    assert "generation=%s" in sql
    assert "recovery_cut_revision=%s" in sql
    assert "ingress_version=%s" in sql
    assert "active=TRUE" in sql
    assert "NOT EXISTS" in sql
    assert params[1:] == ("SINOPAC", "A", 4, 8, 12, 0)
    assert connection.commits == 0


class _QueueConnection(_Connection):
    def __init__(self, rows):
        super().__init__(); self.rows=list(rows); self.statements=[]
    def cursor(self):
        connection=self
        class Cursor(_Cursor):
            def execute(self, sql, params=None):
                connection.last=(sql,params); connection.statements.append((sql,params))
            def fetchone(self):
                return connection.rows.pop(0)
        return Cursor(self)


def _recovery_entry():
    return BrokerReportInboxEntry(
        ingress_id="IN-1",broker="SINOPAC",account_ref="A",generation=4,
        received_at=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc),
        report_type="ORDER",payload_fingerprint="FP-1",payload_json={"status":"Submitted"},
    )


def _discovery_receipt():
    now=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc)
    account=BrokerAccount(broker="SINOPAC",account_ref="A")
    result=BrokerDiscoveryResult(discovery_run_id="DISCOVERY-1",account=account,required_scope="ALL",horizon_start=now,horizon_end=now,refreshed_at=now,completeness=DiscoveryCompleteness.COMPLETE,exact_matches=(),cardinality=ExactMatchCardinality.ZERO,integrity=BrokerDiscoveryIntegrity.CONSISTENT,evidence=("complete",))
    return BrokerDiscoveryReceipt(discovery_run_id="DISCOVERY-1",account=account,generation=4,result=result,producer_id="RECOVERY",contract_version="W4R-B1-V1",recorded_at=now)


def _reconstruction_receipt(**updates):
    now=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc)
    plan=BrokerReconstructionPlan(status=OrderStatus.PENDING,accepted_fills=(),filled_quantity=0,average_fill_price=None,material_change=False)
    values=dict(reconstruction_receipt_id="RECON-1",account=BrokerAccount(broker="SINOPAC",account_ref="A"),generation=4,recovery_cut_fingerprint="CUT",discovery_run_id="DISCOVERY-1",order_id="ORDER-1",broker_deals=(),local_fill_ids=(),lifecycle_evidence=None,plan=plan,deal_set_completeness=BrokerDealSetCompleteness.COMPLETE,authority_commit_id="COMMIT-1",producer_id="RECOVERY",contract_version="W4R-B1-V1",recorded_at=now)
    values.update(updates); return BrokerReconstructionReceipt(**values)


def test_postgres_trusted_receipt_append_locks_active_generation_and_advances_once() -> None:
    receipt=_discovery_receipt()
    connection=_QueueConnection([None,(4,20,True),None,(receipt.discovery_run_id,),(21,)])
    status=PostgresBrokerRecoveryRepository(connection).append_discovery_receipt(receipt)
    assert status is RecoveryEvidenceAppendStatus.APPENDED
    sqls=[sql for sql,_ in connection.statements]
    assert any("account_recovery_controls" in sql and "FOR UPDATE" in sql for sql in sqls)
    assert "active=TRUE" in sqls[-1]
    assert "readiness_revision=readiness_revision+1" in sqls[-1]
    assert connection.commits == 0


def test_postgres_trusted_receipt_duplicate_is_idempotent_without_readiness_advance() -> None:
    receipt=_reconstruction_receipt()
    connection=_QueueConnection([(receipt.model_dump(mode="json"),)])
    status=PostgresBrokerRecoveryRepository(connection).append_reconstruction_receipt(receipt)
    assert status is RecoveryEvidenceAppendStatus.DUPLICATE
    assert not any("readiness_revision=readiness_revision+1" in sql for sql,_ in connection.statements)


def test_postgres_trusted_receipt_conflict_or_inactive_generation_fails_closed() -> None:
    receipt=_discovery_receipt()
    conflict=_QueueConnection([({"different":True},)])
    with pytest.raises(BrokerReportConflictError):
        PostgresBrokerRecoveryRepository(conflict).append_discovery_receipt(receipt)
    inactive=_QueueConnection([None,(4,20,False)])
    with pytest.raises(RecoveryFenceConflictError,match="active generation"):
        PostgresBrokerRecoveryRepository(inactive).append_discovery_receipt(receipt)


def test_historical_and_concurrent_exact_receipt_replay_bypasses_current_generation() -> None:
    receipt=_discovery_receipt()
    historical=_QueueConnection([(receipt.model_dump(mode="json"),)])
    assert PostgresBrokerRecoveryRepository(historical).append_discovery_receipt(receipt) is RecoveryEvidenceAppendStatus.DUPLICATE
    assert len(historical.statements) == 1
    concurrent=_QueueConnection([None,(4,20,True),(receipt.model_dump(mode="json"),)])
    assert PostgresBrokerRecoveryRepository(concurrent).append_discovery_receipt(receipt) is RecoveryEvidenceAppendStatus.DUPLICATE
    assert not any("readiness_revision=readiness_revision+1" in sql for sql,_ in concurrent.statements)


def test_exact_reads_reject_decoded_identity_and_account_mismatch() -> None:
    now=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc)
    expected=AccountPositionSnapshot(snapshot_id="OTHER",broker="SINOPAC",account_ref="A",effective_at=now,recorded_at=now,source_event_id="EVENT",positions=())
    with pytest.raises(ExpectedSnapshotIntegrityError,match="identity"):
        PostgresExpectedPositionSnapshotRepository(_QueueConnection([(expected.model_dump(mode="json"),)])).get_exact(snapshot_id="SNAP-1",broker="SINOPAC",account_ref="A")
    wrong_expected=expected.model_copy(update={"snapshot_id":"SNAP-1","account_ref":"B"})
    with pytest.raises(ExpectedSnapshotIntegrityError,match="scope"):
        PostgresExpectedPositionSnapshotRepository(_QueueConnection([(wrong_expected.model_dump(mode="json"),)])).get_exact(snapshot_id="SNAP-1",broker="SINOPAC",account_ref="A")
    actual=BrokerPositionObservation(observation_id="OTHER",broker="SINOPAC",account_ref="A",observed_at=now,recorded_at=now,positions=())
    with pytest.raises(BrokerObservationIntegrityError,match="identity"):
        PostgresBrokerPositionObservationRepository(_QueueConnection([(actual.model_dump(mode="json"),)])).get_exact(observation_id="OBS-1",broker="SINOPAC",account_ref="A")
    wrong_actual=actual.model_copy(update={"observation_id":"OBS-1","account_ref":"B"})
    with pytest.raises(BrokerObservationIntegrityError,match="scope"):
        PostgresBrokerPositionObservationRepository(_QueueConnection([(wrong_actual.model_dump(mode="json"),)])).get_exact(observation_id="OBS-1",broker="SINOPAC",account_ref="A")


def test_postgres_new_ingress_locks_control_and_atomically_advances_frontier_once() -> None:
    connection=_QueueConnection([(4,12,20,True),("IN-1",),(13,21)])
    repository=PostgresBrokerRecoveryRepository(connection)
    repository.append_inbox(_recovery_entry())
    sqls=[sql for sql,_ in connection.statements]
    assert any("account_recovery_controls" in sql and "FOR UPDATE" in sql for sql in sqls)
    assert "recovery_active_at_capture" in sqls[1]
    assert "ingress_version=ingress_version+1" in sqls[2]
    assert "readiness_revision=readiness_revision+1" in sqls[2]
    assert "active=TRUE" in sqls[2]
    assert connection.commits == 0


def test_postgres_duplicate_ingress_does_not_advance_frontier() -> None:
    entry=_recovery_entry()
    connection=_QueueConnection([(4,12,20,True),None,(entry.model_dump(mode="json"),)])
    repository=PostgresBrokerRecoveryRepository(connection)
    repository.append_inbox(entry)
    assert not any("ingress_version=ingress_version+1" in sql for sql,_ in connection.statements)
    assert not any("readiness_revision=readiness_revision+1" in sql for sql,_ in connection.statements)
    assert connection.commits == 0


def test_postgres_inactive_control_accepts_only_same_generation_without_frontier_advance() -> None:
    entry=_recovery_entry()
    connection=_QueueConnection([(4,12,20,False),("IN-1",)])
    repository=PostgresBrokerRecoveryRepository(connection)
    repository.append_inbox(entry)
    assert not any("ingress_version=ingress_version+1" in sql for sql,_ in connection.statements)
    assert not any("readiness_revision=readiness_revision+1" in sql for sql,_ in connection.statements)
    wrong=_QueueConnection([(5,12,20,False)])
    with pytest.raises(RecoveryFenceConflictError,match="stale"):
        PostgresBrokerRecoveryRepository(wrong).append_inbox(entry)
    assert not any("broker_report_inbox" in sql and "INSERT" in sql for sql,_ in wrong.statements)


def test_postgres_application_identity_is_idempotent_and_sequence_is_durable() -> None:
    application=BrokerReportApplication(
        application_id="APP-1",ingress_id="IN-1",generation=4,
        application_sequence=2,status=BrokerReportApplicationStatus.APPLIED,
        recorded_at=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc),
        evidence=("exact current disposition",),
    )
    connection=_QueueConnection([("SINOPAC","A",4),None,(1,),(20,True),(21,)])
    PostgresBrokerRecoveryRepository(connection).append_application(application)
    assert "broker_report_inbox" in connection.statements[0][0]
    assert "FOR UPDATE" in connection.statements[0][0]
    assert "MAX(application_sequence)" in connection.statements[2][0]
    assert "FOR UPDATE" in connection.statements[3][0]
    assert "application_json" in connection.statements[4][0]
    assert connection.commits == 0


def test_postgres_application_duplicate_and_sequence_conflicts_fail_closed() -> None:
    application=BrokerReportApplication(
        application_id="APP-1",ingress_id="IN-1",generation=4,
        application_sequence=1,status=BrokerReportApplicationStatus.APPLIED,
        recorded_at=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc),
        evidence=("exact current disposition",),
    )
    duplicate=_QueueConnection([("SINOPAC","A",4),(application.model_dump(mode="json"),)])
    PostgresBrokerRecoveryRepository(duplicate).append_application(application)
    assert len(duplicate.statements)==2 and duplicate.commits==0

    gap=_QueueConnection([("SINOPAC","A",4),None,(1,)])
    with pytest.raises(BrokerReportConflictError,match="contiguous"):
        PostgresBrokerRecoveryRepository(gap).append_application(
            application.model_copy(update={"application_id":"APP-3","application_sequence":3})
        )
    assert not any("INSERT INTO trading.broker_report_applications" in sql for sql,_ in gap.statements)


def test_postgres_handoff_uses_exact_generation_latest_sequence_not_timestamp() -> None:
    connection=_ReturningConnection()
    repository=PostgresBrokerRecoveryRepository(connection)
    control=AccountRecoveryControl(
        broker="SINOPAC",account_ref="A",generation=4,recovery_cut_revision=8,
        ingress_version=12,active=False,
        recorded_at=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc),
    )
    repository.finalize_handoff(control,expected_generation=4,expected_ingress_version=12,expected_readiness_revision=0)
    sql,_=connection.last
    assert "a.generation=i.generation" in sql
    assert "newer.application_sequence>a.application_sequence" in sql
    assert "recorded_at>" not in sql


def test_trusted_readiness_migration_has_explicit_head_receipts_without_epoch_backfill() -> None:
    sql=Path("persistence/postgres/migrations/0009_trusted_readiness_authority.sql").read_text(encoding="utf-8")
    assert "ADD COLUMN readiness_revision BIGINT" in sql
    assert "CREATE TABLE trading.execution_continuity_heads" in sql
    assert "CREATE TABLE trading.continuity_transition_receipts" in sql
    assert "current_epoch_id" in sql and "head_revision" in sql
    assert "previous_readiness_revision" in sql
    assert "transition_receipt_id" in sql
    assert "FOREIGN KEY (broker, account_ref, generation, current_epoch_id)" in sql
    assert "FOREIGN KEY (transition_receipt_id, broker, account_ref, generation, current_epoch_id, head_revision, readiness_revision)" in sql
    for field in ("recovery_cut_fingerprint","anchor_fingerprint","ingress_version","account_revision","expected_snapshot_id","authority_commit_id","gap_set_fingerprint","producer_id","contract_version","evidence_id"):
        assert field in sql
    assert "COMMENT ON TABLE trading.execution_continuity_heads" in sql
    assert "COMMENT ON TABLE trading.continuity_transition_receipts" in sql
    assert "INSERT INTO trading.execution_continuity_heads" not in sql
    assert "UPDATE trading.execution_continuity_epochs" not in sql


def test_postgres_continuity_transition_uses_head_and_readiness_cas_without_commit() -> None:
    from persistence.broker_recovery import ContinuityTransitionReceipt, ExecutionContinuityHead
    epoch=__import__("persistence.broker_recovery",fromlist=["ExecutionContinuityEpoch"]).ExecutionContinuityEpoch(
        epoch_id="EPOCH-10",broker="SINOPAC",account_ref="A",generation=4,
        trusted_current=False,historical_degradation=True,anchored_at=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc),evidence=("explicit",),
    )
    head=ExecutionContinuityHead(broker="SINOPAC",account_ref="A",generation=4,current_epoch_id="EPOCH-10",transition_receipt_id="TR-3",head_revision=3,readiness_revision=21,recorded_at=epoch.anchored_at)
    receipt=ContinuityTransitionReceipt(transition_id="TR-3",broker="SINOPAC",account_ref="A",generation=4,previous_epoch_id="EPOCH-2",current_epoch_id="EPOCH-10",previous_head_revision=2,head_revision=3,previous_readiness_revision=20,readiness_revision=21,recovery_cut_fingerprint="CUT-FP",anchor_fingerprint="ANCHOR-FP",recovery_cut_revision=8,ingress_version=12,account_revision=8,expected_snapshot_id="SNAP-8",authority_commit_id="COMMIT-8",gap_set_fingerprint="GAPS-FP",producer_id="RECOVERY",contract_version="W4R-A-V1",evidence_id="EVIDENCE-3",recorded_at=epoch.anchored_at,evidence=("explicit",))
    connection=_QueueConnection([None,(4,8,12,20,True),None,(2,"EPOCH-2"),("EPOCH-10",),("TR-3",),(3,),(21,)])
    PostgresBrokerRecoveryRepository(connection).transition_continuity_head(epoch=epoch,head=head,receipt=receipt,expected_head_revision=2,expected_readiness_revision=20)
    sqls=[sql for sql,_ in connection.statements]
    assert any("account_recovery_controls" in sql and "FOR UPDATE" in sql for sql in sqls)
    assert any("execution_continuity_heads" in sql and "head_revision=%s" in sql for sql in sqls)
    assert any("continuity_transition_receipts" in sql for sql in sqls)
    assert any("readiness_revision=readiness_revision+1" in sql for sql in sqls)
    assert connection.commits == 0


def test_postgres_exact_historical_transition_replay_returns_before_cas() -> None:
    from persistence.broker_recovery import ContinuityTransitionReceipt, ExecutionContinuityEpoch, ExecutionContinuityHead
    now=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc)
    receipt=ContinuityTransitionReceipt(transition_id="TR-1",broker="SINOPAC",account_ref="A",generation=4,previous_epoch_id=None,current_epoch_id="EPOCH-1",previous_head_revision=0,head_revision=1,previous_readiness_revision=0,readiness_revision=1,recovery_cut_fingerprint="CUT",anchor_fingerprint="ANCHOR",recovery_cut_revision=8,ingress_version=0,account_revision=8,expected_snapshot_id="SNAP",authority_commit_id="COMMIT",gap_set_fingerprint="GAPS",producer_id="RECOVERY",contract_version="V1",evidence_id="EV-1",recorded_at=now,evidence=("exact",))
    epoch=ExecutionContinuityEpoch(epoch_id="EPOCH-1",broker="SINOPAC",account_ref="A",generation=4,trusted_current=True,historical_degradation=False,anchored_at=now,evidence=("exact",))
    head=ExecutionContinuityHead(broker="SINOPAC",account_ref="A",generation=4,current_epoch_id="EPOCH-1",transition_receipt_id="TR-1",head_revision=1,readiness_revision=1,recorded_at=now)
    connection=_QueueConnection([(receipt.model_dump(mode="json"),),(epoch.model_dump(mode="json"),)])
    PostgresBrokerRecoveryRepository(connection).transition_continuity_head(epoch=epoch,head=head,receipt=receipt,expected_head_revision=0,expected_readiness_revision=0)
    assert len(connection.statements)==2
    assert "continuity_transition_receipts" in connection.statements[0][0]
    assert "execution_continuity_epochs" in connection.statements[1][0]
    assert connection.commits == 0

    for durable in (
        epoch.model_copy(update={"trusted_current":False}),
        epoch.model_copy(update={"evidence":("different",)}),
    ):
        conflict=_QueueConnection([(receipt.model_dump(mode="json"),),(durable.model_dump(mode="json"),)])
        with pytest.raises(__import__("persistence.broker_recovery",fromlist=["ContinuityAuthorityConflictError"]).ContinuityAuthorityConflictError,match="epoch"):
            PostgresBrokerRecoveryRepository(conflict).transition_continuity_head(epoch=epoch,head=head,receipt=receipt,expected_head_revision=0,expected_readiness_revision=0)


def test_postgres_existing_exact_epoch_is_reused_for_new_transition() -> None:
    from persistence.broker_recovery import ContinuityTransitionReceipt, ExecutionContinuityEpoch, ExecutionContinuityHead
    now=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc)
    epoch=ExecutionContinuityEpoch(epoch_id="EPOCH-2",broker="SINOPAC",account_ref="A",generation=4,trusted_current=True,historical_degradation=False,anchored_at=now,evidence=("exact",))
    head=ExecutionContinuityHead(broker="SINOPAC",account_ref="A",generation=4,current_epoch_id="EPOCH-2",transition_receipt_id="TR-2",head_revision=2,readiness_revision=2,recorded_at=now)
    receipt=ContinuityTransitionReceipt(transition_id="TR-2",broker="SINOPAC",account_ref="A",generation=4,previous_epoch_id="EPOCH-1",current_epoch_id="EPOCH-2",previous_head_revision=1,head_revision=2,previous_readiness_revision=1,readiness_revision=2,recovery_cut_fingerprint="CUT",anchor_fingerprint="ANCHOR",recovery_cut_revision=8,ingress_version=12,account_revision=8,expected_snapshot_id="SNAP",authority_commit_id="COMMIT",gap_set_fingerprint="GAPS",producer_id="RECOVERY",contract_version="V1",evidence_id="EV-2",recorded_at=now,evidence=("exact",))
    connection=_QueueConnection([None,(4,8,12,1,True),None,(1,"EPOCH-1"),None,(epoch.model_dump(mode="json"),),("TR-2",),(2,),(2,)])
    PostgresBrokerRecoveryRepository(connection).transition_continuity_head(epoch=epoch,head=head,receipt=receipt,expected_head_revision=1,expected_readiness_revision=1)
    assert any("SELECT" in sql and "execution_continuity_epochs" in sql for sql,_ in connection.statements)
    assert connection.commits == 0


def test_postgres_begin_recovery_rejects_nonzero_readiness_before_sql() -> None:
    now=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc)
    control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=2,recovery_cut_revision=8,ingress_version=0,readiness_revision=1,active=True,recorded_at=now)
    connection=_QueueConnection([])
    with pytest.raises(RecoveryFenceConflictError,match="zero"):
        PostgresBrokerRecoveryRepository(connection).begin_recovery(control,expected_generation=1)
    assert connection.statements == []


def test_local_recovery_migration_scopes_reconciliation_cases_without_backfill() -> None:
    sql=Path("persistence/postgres/migrations/0008_local_recovery_reconciliation.sql").read_text(encoding="utf-8")
    assert "ADD COLUMN broker TEXT" in sql
    assert "ADD COLUMN account_ref TEXT" in sql
    assert "enforce_reconciliation_case_scope" in sql
    assert "reconciliation_case_account_latest_idx" in sql
    assert "UPDATE trading.reconciliation_case_history" not in sql
    assert "COMMENT ON COLUMN trading.reconciliation_case_history.broker" in sql


def test_postgres_recovery_loader_establishes_read_only_repeatable_snapshot() -> None:
    from persistence.postgres.recovery import PostgresExecutionStateLoader
    source=__import__("inspect").getsource(PostgresExecutionStateLoader.load)
    assert "REPEATABLE READ READ ONLY" in source
    assert "except ValidationError" in source
    assert "TypeError" not in source and "IndexError" not in source


def test_local_recovery_migration_has_formal_run_boundary_and_atomic_terminal_audit() -> None:
    sql=Path("persistence/postgres/migrations/0008_local_recovery_reconciliation.sql").read_text(encoding="utf-8")
    assert "CREATE TABLE trading.reconciliation_runs" in sql
    assert "CREATE TABLE trading.reconciliation_run_outcomes" in sql
    assert "run_id TEXT PRIMARY KEY" in sql
    assert "REFERENCES trading.reconciliation_runs(run_id)" in sql
    assert "technical_outcome" in sql and "input_qualification" in sql
    assert "COMMENT ON TABLE trading.reconciliation_run_outcomes" in sql


def test_postgres_account_readiness_gate_revalidates_revision_and_nonrevision_witness() -> None:
    from persistence.postgres.recovery import PostgresAccountReadinessGate, _read_currentness_witness, _read_order_witness, _read_report_witness, _read_unresolved_actions
    source=__import__("inspect").getsource(PostgresAccountReadinessGate.revalidate)
    report_source=__import__("inspect").getsource(_read_report_witness)
    order_source=__import__("inspect").getsource(_read_order_witness)
    assert "account_state_heads" in source
    assert "account_recovery_controls" in source
    assert "broker_report_inbox" in report_source
    assert "application_sequence DESC" in report_source
    assert "broker_action_heads h JOIN trading.orders" in order_source
    assert "h.broker=%s AND h.account_ref=%s" in order_source
    assert "projection_json->>'broker'" not in order_source
    for material in ("fill_id","quantity","price","occurred_at","event_id","sequence","causation_id","payload_json"):
        assert material in order_source
    assert "h.broker=%s AND h.account_ref=%s" in order_source
    currentness_source=__import__("inspect").getsource(_read_currentness_witness)
    assert "execution_continuity_epochs" in currentness_source
    assert "broker_sequence_gaps" in currentness_source
    assert "reconciliation_case_history" in currentness_source
    assert "broker_action_heads" in __import__("inspect").getsource(_read_unresolved_actions)
    assert "advance_head" not in source
