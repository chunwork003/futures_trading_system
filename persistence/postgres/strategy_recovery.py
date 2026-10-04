from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from persistence.contracts import normalize_stable_id
from persistence.strategy_recovery import (
    StrategyTransitionHeadConflictError,
    StrategyTransitionPersistenceIntegrityError,
)
from strategy.recovery import (
    StrategyGoverningTransitionAuthority,
    StrategyGoverningTransitionPhaseEvidence,
    StrategyGoverningTransitionPhaseKind,
    StrategyGoverningTransitionResolution,
    StrategyGoverningTransitionResolutionKind,
    StrategyGoverningTransitionResolutionReceipt,
    classify_governing_transition,
)


def _decode(model, payload: object, label: str):
    try:
        if isinstance(payload, str):
            return model.model_validate_json(payload)
        if isinstance(payload, Mapping):
            return model.model_validate(payload)
    except (TypeError, ValueError) as exc:
        raise StrategyTransitionPersistenceIntegrityError(
            f"{label} payload is invalid"
        ) from exc
    raise StrategyTransitionPersistenceIntegrityError(
        f"{label} payload must be structured JSON"
    )


def _json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


class PostgresStrategyGoverningTransitionRepository:
    """Pattern A adapter；semantic authority append-only，只有 resolution head 可 CAS。"""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def append_descriptor(
        self,
        authority: StrategyGoverningTransitionAuthority,
    ) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT strategy_instance_id, transition_json
                FROM trading.strategy_governing_transition_authorities
                WHERE transition_id=%s
                """,
                (authority.transition_id,),
            )
            row = cursor.fetchone()

            if row is not None:
                existing = _decode(
                    StrategyGoverningTransitionAuthority,
                    row[1],
                    "transition descriptor",
                )
                if (
                    row[0] != authority.strategy_instance_id
                    or existing != authority
                ):
                    raise StrategyTransitionPersistenceIntegrityError(
                        "existing transition identity has different immutable descriptor material"
                    )
                return

            cursor.execute(
                """
                INSERT INTO trading.strategy_governing_transition_authorities
                    (
                        transition_id,
                        strategy_instance_id,
                        source_config_version,
                        source_config_fingerprint,
                        source_implementation_revision,
                        source_instrument_id,
                        target_config_version,
                        target_config_fingerprint,
                        target_implementation_revision,
                        target_instrument_id,
                        transition_policy_id,
                        transition_policy_version,
                        transition_json
                    )
                VALUES
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    authority.transition_id,
                    authority.strategy_instance_id,
                    authority.source_context.config_version,
                    authority.source_context.config_fingerprint,
                    authority.source_context.implementation_revision,
                    authority.source_context.instrument_id,
                    authority.target_context.config_version,
                    authority.target_context.config_fingerprint,
                    authority.target_context.implementation_revision,
                    authority.target_context.instrument_id,
                    authority.transition_policy.authority_id,
                    authority.transition_policy.authority_version,
                    _json(authority.model_dump(mode="json")),
                ),
            )

    def append_phase_evidence(
        self,
        evidence: StrategyGoverningTransitionPhaseEvidence,
    ) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT strategy_instance_id, transition_json
                FROM trading.strategy_governing_transition_authorities
                WHERE transition_id=%s
                """,
                (evidence.transition_id,),
            )
            descriptor_row = cursor.fetchone()
            if descriptor_row is None:
                raise StrategyTransitionPersistenceIntegrityError(
                    "phase evidence references missing transition descriptor"
                )

            authority = _decode(
                StrategyGoverningTransitionAuthority,
                descriptor_row[1],
                "transition descriptor",
            )
            if (
                descriptor_row[0] != evidence.strategy_instance_id
                or authority.strategy_instance_id != evidence.strategy_instance_id
            ):
                raise StrategyTransitionPersistenceIntegrityError(
                    "phase evidence StrategyInstance identity mismatch"
                )

            cursor.execute(
                """
                SELECT strategy_instance_id, evidence_json
                FROM trading.strategy_governing_transition_phase_evidence
                WHERE transition_id=%s AND evidence_kind=%s
                """,
                (evidence.transition_id, evidence.kind.value),
            )
            existing_row = cursor.fetchone()

            if existing_row is not None:
                existing = _decode(
                    StrategyGoverningTransitionPhaseEvidence,
                    existing_row[1],
                    "transition phase evidence",
                )
                if (
                    existing_row[0] != evidence.strategy_instance_id
                    or existing != evidence
                ):
                    raise StrategyTransitionPersistenceIntegrityError(
                        "conflicting phase evidence for stable transition identity"
                    )
                return

            prior: list[StrategyGoverningTransitionPhaseEvidence] = []
            if (
                evidence.kind
                is StrategyGoverningTransitionPhaseKind.COMPLETION
            ):
                cursor.execute(
                    """
                    SELECT evidence_json
                    FROM trading.strategy_governing_transition_phase_evidence
                    WHERE transition_id=%s AND evidence_kind='BEGIN_EFFECTIVE'
                    """,
                    (evidence.transition_id,),
                )
                begin_row = cursor.fetchone()
                if begin_row is None:
                    raise StrategyTransitionPersistenceIntegrityError(
                        "COMPLETION requires existing BEGIN_EFFECTIVE evidence"
                    )
                prior.append(
                    _decode(
                        StrategyGoverningTransitionPhaseEvidence,
                        begin_row[0],
                        "BEGIN_EFFECTIVE evidence",
                    )
                )

            try:
                classify_governing_transition(
                    authority=authority,
                    phase_evidence=tuple(prior + [evidence]),
                )
            except ValueError as exc:
                raise StrategyTransitionPersistenceIntegrityError(
                    str(exc)
                ) from exc

            cursor.execute(
                """
                INSERT INTO trading.strategy_governing_transition_phase_evidence
                    (
                        evidence_id,
                        transition_id,
                        strategy_instance_id,
                        evidence_kind,
                        boundary_ref,
                        evidence_json
                    )
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (
                    evidence.evidence_id,
                    evidence.transition_id,
                    evidence.strategy_instance_id,
                    evidence.kind.value,
                    evidence.boundary_ref,
                    _json(evidence.model_dump(mode="json")),
                ),
            )

    def append_resolution(
        self,
        receipt: StrategyGoverningTransitionResolutionReceipt,
    ) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT strategy_instance_id, resolution_json
                FROM trading.strategy_governing_transition_resolution_receipts
                WHERE resolution_id=%s
                """,
                (receipt.resolution_id,),
            )
            existing_row = cursor.fetchone()

            if existing_row is not None:
                existing = _decode(
                    StrategyGoverningTransitionResolutionReceipt,
                    existing_row[1],
                    "transition resolution receipt",
                )
                if (
                    existing_row[0] != receipt.strategy_instance_id
                    or existing != receipt
                ):
                    raise StrategyTransitionPersistenceIntegrityError(
                        "existing transition resolution identity has different material"
                    )
                return

            if (
                receipt.resolution_kind
                is StrategyGoverningTransitionResolutionKind.ACTIVE_TRANSITION
            ):
                cursor.execute(
                    """
                    SELECT strategy_instance_id
                    FROM trading.strategy_governing_transition_authorities
                    WHERE transition_id=%s
                    """,
                    (receipt.transition_id,),
                )
                descriptor = cursor.fetchone()
                if (
                    descriptor is None
                    or descriptor[0] != receipt.strategy_instance_id
                ):
                    raise StrategyTransitionPersistenceIntegrityError(
                        "ACTIVE_TRANSITION resolution references missing descriptor"
                    )

            cursor.execute(
                """
                INSERT INTO trading.strategy_governing_transition_resolution_receipts
                    (
                        resolution_id,
                        strategy_instance_id,
                        resolution_revision,
                        resolution_kind,
                        transition_id,
                        effective_config_version,
                        effective_config_fingerprint,
                        resolution_authority_id,
                        resolution_authority_version,
                        currentness_evidence_ref,
                        resolution_json
                    )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    receipt.resolution_id,
                    receipt.strategy_instance_id,
                    receipt.resolution_revision,
                    receipt.resolution_kind.value,
                    receipt.transition_id,
                    receipt.effective_governing_context.config_version,
                    receipt.effective_governing_context.config_fingerprint,
                    receipt.resolution_authority.authority_id,
                    receipt.resolution_authority.authority_version,
                    receipt.currentness_evidence_ref,
                    _json(receipt.model_dump(mode="json")),
                ),
            )

    def advance_resolution_head(
        self,
        *,
        strategy_instance_id: str,
        resolution_id: str,
        expected_head_revision: int,
    ) -> int:
        strategy_instance_id = normalize_stable_id(strategy_instance_id)
        resolution_id = normalize_stable_id(resolution_id)
        if expected_head_revision < 0:
            raise ValueError("expected_head_revision must be non-negative")

        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT strategy_instance_id, resolution_revision
                FROM trading.strategy_governing_transition_resolution_receipts
                WHERE resolution_id=%s
                """,
                (resolution_id,),
            )
            receipt_row = cursor.fetchone()
            if (
                receipt_row is None
                or receipt_row[0] != strategy_instance_id
            ):
                raise StrategyTransitionPersistenceIntegrityError(
                    "resolution head target does not resolve exact StrategyInstance receipt"
                )

            target_revision = receipt_row[1]

            cursor.execute(
                """
                SELECT resolution_id, head_revision
                FROM trading.strategy_governing_transition_resolution_heads
                WHERE strategy_instance_id=%s
                FOR UPDATE
                """,
                (strategy_instance_id,),
            )
            head = cursor.fetchone()

            if head is None:
                if expected_head_revision != 0 or target_revision != 1:
                    raise StrategyTransitionHeadConflictError(
                        "transition resolution head revision conflict"
                    )
                cursor.execute(
                    """
                    INSERT INTO trading.strategy_governing_transition_resolution_heads
                        (strategy_instance_id, resolution_id, head_revision)
                    VALUES (%s,%s,1)
                    RETURNING head_revision
                    """,
                    (strategy_instance_id, resolution_id),
                )
                created = cursor.fetchone()
                if created is None or created[0] != 1:
                    raise StrategyTransitionHeadConflictError(
                        "transition resolution head creation failed"
                    )
                return 1

            current_resolution_id, current_revision = head
            if current_revision != expected_head_revision:
                raise StrategyTransitionHeadConflictError(
                    "transition resolution head revision conflict"
                )
            if current_resolution_id == resolution_id:
                if target_revision != current_revision:
                    raise StrategyTransitionPersistenceIntegrityError(
                        "current resolution receipt revision conflicts with head"
                    )
                return current_revision
            if target_revision != current_revision + 1:
                raise StrategyTransitionHeadConflictError(
                    "resolution revision must advance current head contiguously"
                )

            cursor.execute(
                """
                UPDATE trading.strategy_governing_transition_resolution_heads
                SET resolution_id=%s, head_revision=%s, recorded_at=CURRENT_TIMESTAMP
                WHERE strategy_instance_id=%s AND head_revision=%s
                RETURNING head_revision
                """,
                (
                    resolution_id,
                    target_revision,
                    strategy_instance_id,
                    expected_head_revision,
                ),
            )
            advanced = cursor.fetchone()
            if advanced is None or advanced[0] != target_revision:
                raise StrategyTransitionHeadConflictError(
                    "transition resolution head compare-and-swap failed"
                )
            return advanced[0]

    def current_resolution(
        self,
        strategy_instance_id: str,
    ) -> StrategyGoverningTransitionResolution | None:
        strategy_instance_id = normalize_stable_id(strategy_instance_id)

        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    h.resolution_id,
                    h.head_revision,
                    r.strategy_instance_id,
                    r.resolution_revision,
                    r.resolution_kind,
                    r.transition_id,
                    r.effective_config_version,
                    r.effective_config_fingerprint,
                    r.resolution_authority_id,
                    r.resolution_authority_version,
                    r.currentness_evidence_ref,
                    r.resolution_json
                FROM trading.strategy_governing_transition_resolution_heads h
                JOIN trading.strategy_governing_transition_resolution_receipts r
                    ON r.resolution_id=h.resolution_id
                    AND r.strategy_instance_id=h.strategy_instance_id
                WHERE h.strategy_instance_id=%s
                """,
                (strategy_instance_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None

            receipt = _decode(
                StrategyGoverningTransitionResolutionReceipt,
                row[11],
                "transition resolution receipt",
            )
            structured = (
                row[0], row[2], row[3], row[4], row[5],
                row[6], row[7], row[8], row[9], row[10],
            )
            canonical = (
                receipt.resolution_id,
                receipt.strategy_instance_id,
                receipt.resolution_revision,
                receipt.resolution_kind.value,
                receipt.transition_id,
                receipt.effective_governing_context.config_version,
                receipt.effective_governing_context.config_fingerprint,
                receipt.resolution_authority.authority_id,
                receipt.resolution_authority.authority_version,
                receipt.currentness_evidence_ref,
            )
            if structured != canonical:
                raise StrategyTransitionPersistenceIntegrityError(
                    "transition resolution structured authority conflicts with resolution_json"
                )
            if receipt.strategy_instance_id != strategy_instance_id:
                raise StrategyTransitionPersistenceIntegrityError(
                    "transition resolution head conflicts with requested StrategyInstance"
                )
            if row[1] != receipt.resolution_revision:
                raise StrategyTransitionPersistenceIntegrityError(
                    "transition resolution receipt is stale against current head"
                )

            if (
                receipt.resolution_kind
                is StrategyGoverningTransitionResolutionKind.NO_ACTIVE_TRANSITION
            ):
                return StrategyGoverningTransitionResolution(
                    receipt=receipt,
                    current_head_revision=row[1],
                )

            cursor.execute(
                """
                SELECT
                    strategy_instance_id,
                    source_config_version,
                    source_config_fingerprint,
                    source_implementation_revision,
                    source_instrument_id,
                    target_config_version,
                    target_config_fingerprint,
                    target_implementation_revision,
                    target_instrument_id,
                    transition_policy_id,
                    transition_policy_version,
                    transition_json
                FROM trading.strategy_governing_transition_authorities
                WHERE transition_id=%s
                """,
                (receipt.transition_id,),
            )
            descriptor_row = cursor.fetchone()
            if descriptor_row is None:
                raise StrategyTransitionPersistenceIntegrityError(
                    "current ACTIVE_TRANSITION descriptor is missing"
                )
            authority = _decode(
                StrategyGoverningTransitionAuthority,
                descriptor_row[11],
                "transition descriptor",
            )
            descriptor_structured = tuple(descriptor_row[:11])
            descriptor_canonical = (
                authority.strategy_instance_id,
                authority.source_context.config_version,
                authority.source_context.config_fingerprint,
                authority.source_context.implementation_revision,
                authority.source_context.instrument_id,
                authority.target_context.config_version,
                authority.target_context.config_fingerprint,
                authority.target_context.implementation_revision,
                authority.target_context.instrument_id,
                authority.transition_policy.authority_id,
                authority.transition_policy.authority_version,
            )
            if descriptor_structured != descriptor_canonical:
                raise StrategyTransitionPersistenceIntegrityError(
                    "transition descriptor structured authority conflicts with transition_json"
                )

            phase_evidence = []
            for kind in (
                StrategyGoverningTransitionPhaseKind.BEGIN_EFFECTIVE,
                StrategyGoverningTransitionPhaseKind.COMPLETION,
            ):
                cursor.execute(
                    """
                    SELECT strategy_instance_id, evidence_kind, evidence_json
                    FROM trading.strategy_governing_transition_phase_evidence
                    WHERE transition_id=%s AND evidence_kind=%s
                    """,
                    (authority.transition_id, kind.value),
                )
                phase_row = cursor.fetchone()
                if phase_row is None:
                    continue
                evidence = _decode(
                    StrategyGoverningTransitionPhaseEvidence,
                    phase_row[2],
                    "transition phase evidence",
                )
                if (
                    phase_row[0] != evidence.strategy_instance_id
                    or phase_row[1] != evidence.kind.value
                ):
                    raise StrategyTransitionPersistenceIntegrityError(
                        "transition phase structured authority conflicts with evidence_json"
                    )
                phase_evidence.append(evidence)

        try:
            return StrategyGoverningTransitionResolution(
                receipt=receipt,
                current_head_revision=row[1],
                transition_authority=authority,
                phase_evidence=tuple(phase_evidence),
            )
        except ValueError as exc:
            raise StrategyTransitionPersistenceIntegrityError(str(exc)) from exc


__all__ = ["PostgresStrategyGoverningTransitionRepository"]
