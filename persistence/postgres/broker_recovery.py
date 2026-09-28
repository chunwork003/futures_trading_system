from __future__ import annotations

import json
from typing import Any

from persistence.broker_recovery import (
    AccountRecoveryControl, BrokerRecoveryRepository, BrokerReportApplication,
    BrokerReportConflictError, BrokerReportInboxEntry, BrokerReportIngressStatus,
    ContinuityAuthorityConflictError, ContinuityTransitionReceipt,
    ExecutionContinuityEpoch, ExecutionContinuityHead,
    RecoveryFenceConflictError, SequenceGap,
)
from trading.account import BrokerAccount


class PostgresBrokerRecoveryRepository(BrokerRecoveryRepository):
    """PostgreSQL recovery evidence adapter；conditional writes 建立 race-safe fence，且不自行 commit。"""
    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def append_inbox(self, entry: BrokerReportInboxEntry) -> BrokerReportIngressStatus:
        payload = json.loads(entry.model_dump_json())
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT generation,ingress_version,readiness_revision,active FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s FOR UPDATE",
                (entry.broker, entry.account_ref),
            )
            control = cursor.fetchone()
            if control is None:
                raise RecoveryFenceConflictError("recovery control is missing")
            generation, ingress_version, readiness_revision, active = control
            if generation != entry.generation:
                raise RecoveryFenceConflictError("broker report generation is stale")
            cursor.execute(
                "INSERT INTO trading.broker_report_inbox (ingress_id,broker,account_ref,generation,recovery_active_at_capture,received_at,report_type,payload_fingerprint,report_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING ingress_id",
                (entry.ingress_id, entry.broker, entry.account_ref, entry.generation, active, entry.received_at, entry.report_type, entry.payload_fingerprint, json.dumps(payload)),
            )
            inserted = cursor.fetchone() is not None
            if not inserted:
                cursor.execute(
                    "SELECT report_json FROM trading.broker_report_inbox WHERE ingress_id=%s",
                    (entry.ingress_id,),
                )
                row = cursor.fetchone()
                if row is None or BrokerReportInboxEntry.model_validate(row[0]) != entry:
                    raise BrokerReportConflictError("broker report ingress identity conflict")
                return BrokerReportIngressStatus.DUPLICATE
            if active:
                cursor.execute(
                    "UPDATE trading.account_recovery_controls SET ingress_version=ingress_version+1,readiness_revision=readiness_revision+1 WHERE broker=%s AND account_ref=%s AND generation=%s AND ingress_version=%s AND readiness_revision=%s AND active=TRUE RETURNING ingress_version,readiness_revision",
                    (entry.broker, entry.account_ref, entry.generation, ingress_version, readiness_revision),
                )
                if cursor.fetchone() is None:
                    raise RecoveryFenceConflictError("concurrent broker ingress frontier conflict")
            return BrokerReportIngressStatus.APPENDED

    def append_application(self, application: BrokerReportApplication) -> None:
        payload = json.loads(application.model_dump_json())
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT broker,account_ref,generation FROM trading.broker_report_inbox WHERE ingress_id=%s FOR UPDATE",
                (application.ingress_id,),
            )
            ingress = cursor.fetchone()
            if ingress is None or ingress[2] != application.generation:
                raise BrokerReportConflictError("broker report application ingress generation mismatch")
            cursor.execute(
                "SELECT application_json FROM trading.broker_report_applications WHERE application_id=%s",
                (application.application_id,),
            )
            row = cursor.fetchone()
            if row is not None:
                if BrokerReportApplication.model_validate(row[0]) != application:
                    raise BrokerReportConflictError("broker report application identity conflict")
                return
            cursor.execute(
                "SELECT COALESCE(MAX(application_sequence),0) FROM trading.broker_report_applications WHERE ingress_id=%s AND generation=%s",
                (application.ingress_id, application.generation),
            )
            latest = cursor.fetchone()
            if latest is None or application.application_sequence != latest[0] + 1:
                raise BrokerReportConflictError("broker report application sequence must be contiguous")
            cursor.execute(
                "SELECT readiness_revision,active FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s AND generation=%s FOR UPDATE",
                (ingress[0], ingress[1], application.generation),
            )
            control=cursor.fetchone()
            if control is None:
                raise RecoveryFenceConflictError("recovery control is missing")
            readiness_revision, active=control
            cursor.execute(
                "INSERT INTO trading.broker_report_applications (application_id,ingress_id,generation,application_sequence,status,recorded_at,evidence_json,application_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (application.application_id, application.ingress_id, application.generation, application.application_sequence, application.status.value, application.recorded_at, json.dumps(application.evidence), json.dumps(payload)),
            )
            if active:
                cursor.execute(
                    "UPDATE trading.account_recovery_controls SET readiness_revision=readiness_revision+1 WHERE broker=%s AND account_ref=%s AND generation=%s AND readiness_revision=%s AND active=TRUE RETURNING readiness_revision",
                    (ingress[0], ingress[1], application.generation, readiness_revision),
                )
                if cursor.fetchone() is None:
                    raise RecoveryFenceConflictError("concurrent readiness frontier conflict")

    def append_sequence_gap(self, gap: SequenceGap) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT readiness_revision,active FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s FOR UPDATE", (gap.broker, gap.account_ref))
            control=cursor.fetchone()
            cursor.execute("INSERT INTO trading.broker_sequence_gaps (gap_id,broker,account_ref,detected_at,evidence) VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING gap_id", (gap.gap_id, gap.broker, gap.account_ref, gap.detected_at, gap.evidence))
            if cursor.fetchone() is None: raise BrokerReportConflictError("sequence gap identity conflict")
            if control is not None and control[1]:
                cursor.execute("UPDATE trading.account_recovery_controls SET readiness_revision=readiness_revision+1 WHERE broker=%s AND account_ref=%s AND readiness_revision=%s AND active=TRUE RETURNING readiness_revision", (gap.broker, gap.account_ref, control[0]))
                if cursor.fetchone() is None: raise RecoveryFenceConflictError("concurrent readiness frontier conflict")

    def append_continuity_epoch(self, epoch: ExecutionContinuityEpoch) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute("INSERT INTO trading.execution_continuity_epochs (epoch_id,broker,account_ref,generation,trusted_current,historical_degradation,anchored_at,evidence_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING epoch_id", (epoch.epoch_id, epoch.broker, epoch.account_ref, epoch.generation, epoch.trusted_current, epoch.historical_degradation, epoch.anchored_at, json.dumps(epoch.evidence)))
            if cursor.fetchone() is None: raise BrokerReportConflictError("continuity epoch identity conflict")

    def transition_continuity_head(self, *, epoch: ExecutionContinuityEpoch, head: ExecutionContinuityHead, receipt: ContinuityTransitionReceipt, expected_head_revision: int, expected_readiness_revision: int) -> None:
        """以 account control 與 continuity head 雙鎖/CAS 原子保存 epoch、receipt 及 current selector。"""
        payload = json.loads(receipt.model_dump_json())
        scope=(epoch.broker,epoch.account_ref,epoch.generation)
        if scope != (head.broker,head.account_ref,head.generation) or scope != (receipt.broker,receipt.account_ref,receipt.generation):
            raise ContinuityAuthorityConflictError("continuity transition account scope conflict")
        if epoch.epoch_id != head.current_epoch_id or epoch.epoch_id != receipt.current_epoch_id or head.transition_receipt_id != receipt.transition_id:
            raise ContinuityAuthorityConflictError("continuity transition identity coherence conflict")
        if head.head_revision != expected_head_revision + 1 or receipt.previous_head_revision != expected_head_revision or receipt.head_revision != head.head_revision:
            raise ContinuityAuthorityConflictError("continuity head revision coherence conflict")
        if head.readiness_revision != expected_readiness_revision + 1 or receipt.previous_readiness_revision != expected_readiness_revision or receipt.readiness_revision != head.readiness_revision:
            raise ContinuityAuthorityConflictError("continuity readiness revision coherence conflict")
        if head.recorded_at != receipt.recorded_at:
            raise ContinuityAuthorityConflictError("continuity recorded_at coherence conflict")
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT receipt_json FROM trading.continuity_transition_receipts WHERE transition_id=%s", (receipt.transition_id,))
            existing=cursor.fetchone()
            if existing is not None:
                if ContinuityTransitionReceipt.model_validate(existing[0]) != receipt:
                    raise ContinuityAuthorityConflictError("continuity transition identity conflict")
                cursor.execute("SELECT jsonb_build_object('epoch_id',epoch_id,'broker',broker,'account_ref',account_ref,'generation',generation,'trusted_current',trusted_current,'historical_degradation',historical_degradation,'anchored_at',anchored_at,'evidence',evidence_json) FROM trading.execution_continuity_epochs WHERE epoch_id=%s", (epoch.epoch_id,))
                durable_epoch=cursor.fetchone()
                if durable_epoch is None or ExecutionContinuityEpoch.model_validate(durable_epoch[0]) != epoch:
                    raise ContinuityAuthorityConflictError("continuity epoch material conflict")
                return
            cursor.execute("SELECT generation,recovery_cut_revision,ingress_version,readiness_revision,active FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s FOR UPDATE", (head.broker, head.account_ref))
            control = cursor.fetchone()
            cursor.execute("SELECT receipt_json FROM trading.continuity_transition_receipts WHERE transition_id=%s", (receipt.transition_id,))
            concurrent_existing=cursor.fetchone()
            if concurrent_existing is not None:
                if ContinuityTransitionReceipt.model_validate(concurrent_existing[0]) != receipt:
                    raise ContinuityAuthorityConflictError("continuity transition identity conflict")
                cursor.execute("SELECT jsonb_build_object('epoch_id',epoch_id,'broker',broker,'account_ref',account_ref,'generation',generation,'trusted_current',trusted_current,'historical_degradation',historical_degradation,'anchored_at',anchored_at,'evidence',evidence_json) FROM trading.execution_continuity_epochs WHERE epoch_id=%s", (epoch.epoch_id,))
                durable_epoch=cursor.fetchone()
                if durable_epoch is None or ExecutionContinuityEpoch.model_validate(durable_epoch[0]) != epoch:
                    raise ContinuityAuthorityConflictError("continuity epoch material conflict")
                return
            if control != (head.generation,receipt.recovery_cut_revision,receipt.ingress_version,expected_readiness_revision,True):
                raise ContinuityAuthorityConflictError("continuity readiness CAS conflict")
            cursor.execute("SELECT head_revision,current_epoch_id FROM trading.execution_continuity_heads WHERE broker=%s AND account_ref=%s FOR UPDATE", (head.broker, head.account_ref))
            current = cursor.fetchone()
            actual_revision = 0 if current is None else current[0]
            actual_epoch = None if current is None else current[1]
            if actual_revision != expected_head_revision or receipt.previous_epoch_id != actual_epoch:
                raise ContinuityAuthorityConflictError("continuity head CAS conflict")
            cursor.execute("INSERT INTO trading.execution_continuity_epochs (epoch_id,broker,account_ref,generation,trusted_current,historical_degradation,anchored_at,evidence_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING epoch_id", (epoch.epoch_id, epoch.broker, epoch.account_ref, epoch.generation, epoch.trusted_current, epoch.historical_degradation, epoch.anchored_at, json.dumps(epoch.evidence)))
            if cursor.fetchone() is None:
                cursor.execute("SELECT jsonb_build_object('epoch_id',epoch_id,'broker',broker,'account_ref',account_ref,'generation',generation,'trusted_current',trusted_current,'historical_degradation',historical_degradation,'anchored_at',anchored_at,'evidence',evidence_json) FROM trading.execution_continuity_epochs WHERE epoch_id=%s", (epoch.epoch_id,))
                durable_epoch=cursor.fetchone()
                if durable_epoch is None or ExecutionContinuityEpoch.model_validate(durable_epoch[0]) != epoch:
                    raise ContinuityAuthorityConflictError("continuity epoch material conflict")
            cursor.execute("INSERT INTO trading.continuity_transition_receipts (transition_id,broker,account_ref,generation,previous_epoch_id,current_epoch_id,previous_head_revision,head_revision,previous_readiness_revision,readiness_revision,recovery_cut_fingerprint,anchor_fingerprint,recovery_cut_revision,ingress_version,account_revision,expected_snapshot_id,authority_commit_id,gap_set_fingerprint,producer_id,contract_version,evidence_id,recorded_at,evidence_json,receipt_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING transition_id", (receipt.transition_id,receipt.broker,receipt.account_ref,receipt.generation,receipt.previous_epoch_id,receipt.current_epoch_id,receipt.previous_head_revision,receipt.head_revision,receipt.previous_readiness_revision,receipt.readiness_revision,receipt.recovery_cut_fingerprint,receipt.anchor_fingerprint,receipt.recovery_cut_revision,receipt.ingress_version,receipt.account_revision,receipt.expected_snapshot_id,receipt.authority_commit_id,receipt.gap_set_fingerprint,receipt.producer_id,receipt.contract_version,receipt.evidence_id,receipt.recorded_at,json.dumps(receipt.evidence),json.dumps(payload)))
            if cursor.fetchone() is None:
                cursor.execute("SELECT receipt_json FROM trading.continuity_transition_receipts WHERE transition_id=%s", (receipt.transition_id,))
                row=cursor.fetchone()
                if row is None or ContinuityTransitionReceipt.model_validate(row[0]) != receipt:
                    raise ContinuityAuthorityConflictError("continuity transition identity conflict")
                return
            cursor.execute("INSERT INTO trading.execution_continuity_heads (broker,account_ref,generation,current_epoch_id,transition_receipt_id,head_revision,readiness_revision,recorded_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (broker,account_ref) DO UPDATE SET generation=EXCLUDED.generation,current_epoch_id=EXCLUDED.current_epoch_id,transition_receipt_id=EXCLUDED.transition_receipt_id,head_revision=EXCLUDED.head_revision,readiness_revision=EXCLUDED.readiness_revision,recorded_at=EXCLUDED.recorded_at WHERE trading.execution_continuity_heads.head_revision=%s RETURNING head_revision", (head.broker,head.account_ref,head.generation,head.current_epoch_id,head.transition_receipt_id,head.head_revision,head.readiness_revision,head.recorded_at,expected_head_revision))
            if cursor.fetchone() is None:
                raise ContinuityAuthorityConflictError("continuity head CAS conflict")
            cursor.execute("UPDATE trading.account_recovery_controls SET readiness_revision=readiness_revision+1 WHERE broker=%s AND account_ref=%s AND generation=%s AND readiness_revision=%s AND active=TRUE RETURNING readiness_revision", (head.broker,head.account_ref,head.generation,expected_readiness_revision))
            advanced=cursor.fetchone()
            if advanced is None or advanced[0] != head.readiness_revision:
                raise ContinuityAuthorityConflictError("continuity readiness CAS conflict")

    def get_control(self, account: BrokerAccount) -> AccountRecoveryControl | None:
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT broker,account_ref,generation,recovery_cut_revision,ingress_version,readiness_revision,active,recorded_at FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s", (account.broker, account.account_ref))
            row = cursor.fetchone()
        return None if row is None else AccountRecoveryControl(broker=row[0], account_ref=row[1], generation=row[2], recovery_cut_revision=row[3], ingress_version=row[4], readiness_revision=row[5], active=row[6], recorded_at=row[7])

    def begin_recovery(self, control: AccountRecoveryControl, *, expected_generation: int) -> None:
        if control.readiness_revision != 0:
            raise RecoveryFenceConflictError("fresh recovery readiness revision must be zero")
        with self._connection.cursor() as cursor:
            cursor.execute("INSERT INTO trading.account_recovery_controls (broker,account_ref,generation,recovery_cut_revision,ingress_version,readiness_revision,active,recorded_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (broker,account_ref) DO UPDATE SET generation=EXCLUDED.generation,recovery_cut_revision=EXCLUDED.recovery_cut_revision,ingress_version=EXCLUDED.ingress_version,readiness_revision=EXCLUDED.readiness_revision,active=TRUE,recorded_at=EXCLUDED.recorded_at WHERE trading.account_recovery_controls.generation=%s AND trading.account_recovery_controls.active=FALSE RETURNING generation", (control.broker, control.account_ref, control.generation, control.recovery_cut_revision, control.ingress_version, control.readiness_revision, control.active, control.recorded_at, expected_generation))
            if cursor.fetchone() is None: raise RecoveryFenceConflictError("concurrent recovery generation conflict")

    def finalize_handoff(self, control: AccountRecoveryControl, *, expected_generation: int, expected_ingress_version: int, expected_readiness_revision: int) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute("UPDATE trading.account_recovery_controls c SET active=FALSE,recorded_at=%s WHERE c.broker=%s AND c.account_ref=%s AND c.generation=%s AND c.recovery_cut_revision=%s AND c.ingress_version=%s AND c.readiness_revision=%s AND c.active=TRUE AND NOT EXISTS (SELECT 1 FROM trading.broker_report_inbox i WHERE i.broker=c.broker AND i.account_ref=c.account_ref AND i.generation=c.generation AND i.recovery_active_at_capture=TRUE AND NOT EXISTS (SELECT 1 FROM trading.broker_report_applications a WHERE a.ingress_id=i.ingress_id AND a.generation=i.generation AND a.status IN ('APPLIED','DUPLICATE','CORROBORATED') AND NOT EXISTS (SELECT 1 FROM trading.broker_report_applications newer WHERE newer.ingress_id=a.ingress_id AND newer.generation=a.generation AND newer.application_sequence>a.application_sequence))) RETURNING generation", (control.recorded_at, control.broker, control.account_ref, expected_generation, control.recovery_cut_revision, expected_ingress_version, expected_readiness_revision))
            if cursor.fetchone() is None: raise RecoveryFenceConflictError("stale fence or pending report blocks handoff")


__all__ = ["PostgresBrokerRecoveryRepository"]
