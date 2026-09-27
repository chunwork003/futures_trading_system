from __future__ import annotations

import json
from typing import Any

from persistence.broker_recovery import (
    AccountRecoveryControl, BrokerRecoveryRepository, BrokerReportApplication,
    BrokerReportConflictError, BrokerReportInboxEntry, BrokerReportIngressStatus,
    ExecutionContinuityEpoch, RecoveryFenceConflictError, SequenceGap,
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
                "SELECT generation,ingress_version,active FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s FOR UPDATE",
                (entry.broker, entry.account_ref),
            )
            control = cursor.fetchone()
            if control is None:
                raise RecoveryFenceConflictError("recovery control is missing")
            generation, ingress_version, active = control
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
                    "UPDATE trading.account_recovery_controls SET ingress_version=ingress_version+1 WHERE broker=%s AND account_ref=%s AND generation=%s AND ingress_version=%s AND active=TRUE RETURNING ingress_version",
                    (entry.broker, entry.account_ref, entry.generation, ingress_version),
                )
                if cursor.fetchone() is None:
                    raise RecoveryFenceConflictError("concurrent broker ingress frontier conflict")
            return BrokerReportIngressStatus.APPENDED

    def append_application(self, application: BrokerReportApplication) -> None:
        payload = json.loads(application.model_dump_json())
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT generation FROM trading.broker_report_inbox WHERE ingress_id=%s FOR UPDATE",
                (application.ingress_id,),
            )
            ingress = cursor.fetchone()
            if ingress is None or ingress[0] != application.generation:
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
                "INSERT INTO trading.broker_report_applications (application_id,ingress_id,generation,application_sequence,status,recorded_at,evidence_json,application_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (application.application_id, application.ingress_id, application.generation, application.application_sequence, application.status.value, application.recorded_at, json.dumps(application.evidence), json.dumps(payload)),
            )

    def append_sequence_gap(self, gap: SequenceGap) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute("INSERT INTO trading.broker_sequence_gaps (gap_id,broker,account_ref,detected_at,evidence) VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING gap_id", (gap.gap_id, gap.broker, gap.account_ref, gap.detected_at, gap.evidence))
            if cursor.fetchone() is None: raise BrokerReportConflictError("sequence gap identity conflict")

    def append_continuity_epoch(self, epoch: ExecutionContinuityEpoch) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute("INSERT INTO trading.execution_continuity_epochs (epoch_id,broker,account_ref,generation,trusted_current,historical_degradation,anchored_at,evidence_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING epoch_id", (epoch.epoch_id, epoch.broker, epoch.account_ref, epoch.generation, epoch.trusted_current, epoch.historical_degradation, epoch.anchored_at, json.dumps(epoch.evidence)))
            if cursor.fetchone() is None: raise BrokerReportConflictError("continuity epoch identity conflict")

    def get_control(self, account: BrokerAccount) -> AccountRecoveryControl | None:
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT broker,account_ref,generation,recovery_cut_revision,ingress_version,active,recorded_at FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s", (account.broker, account.account_ref))
            row = cursor.fetchone()
        return None if row is None else AccountRecoveryControl(broker=row[0], account_ref=row[1], generation=row[2], recovery_cut_revision=row[3], ingress_version=row[4], active=row[5], recorded_at=row[6])

    def begin_recovery(self, control: AccountRecoveryControl, *, expected_generation: int) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute("INSERT INTO trading.account_recovery_controls (broker,account_ref,generation,recovery_cut_revision,ingress_version,active,recorded_at) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (broker,account_ref) DO UPDATE SET generation=EXCLUDED.generation,recovery_cut_revision=EXCLUDED.recovery_cut_revision,ingress_version=EXCLUDED.ingress_version,active=TRUE,recorded_at=EXCLUDED.recorded_at WHERE trading.account_recovery_controls.generation=%s AND trading.account_recovery_controls.active=FALSE RETURNING generation", (control.broker, control.account_ref, control.generation, control.recovery_cut_revision, control.ingress_version, control.active, control.recorded_at, expected_generation))
            if cursor.fetchone() is None: raise RecoveryFenceConflictError("concurrent recovery generation conflict")

    def finalize_handoff(self, control: AccountRecoveryControl, *, expected_generation: int, expected_ingress_version: int) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute("UPDATE trading.account_recovery_controls c SET active=FALSE,recorded_at=%s WHERE c.broker=%s AND c.account_ref=%s AND c.generation=%s AND c.recovery_cut_revision=%s AND c.ingress_version=%s AND c.active=TRUE AND NOT EXISTS (SELECT 1 FROM trading.broker_report_inbox i WHERE i.broker=c.broker AND i.account_ref=c.account_ref AND i.generation=c.generation AND i.recovery_active_at_capture=TRUE AND NOT EXISTS (SELECT 1 FROM trading.broker_report_applications a WHERE a.ingress_id=i.ingress_id AND a.generation=i.generation AND a.status IN ('APPLIED','DUPLICATE','CORROBORATED') AND NOT EXISTS (SELECT 1 FROM trading.broker_report_applications newer WHERE newer.ingress_id=a.ingress_id AND newer.generation=a.generation AND newer.application_sequence>a.application_sequence))) RETURNING generation", (control.recorded_at, control.broker, control.account_ref, expected_generation, control.recovery_cut_revision, expected_ingress_version))
            if cursor.fetchone() is None: raise RecoveryFenceConflictError("stale fence or pending report blocks handoff")


__all__ = ["PostgresBrokerRecoveryRepository"]
