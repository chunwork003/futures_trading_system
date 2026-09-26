from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import json
from typing import Any, Mapping

from domain.market_observation import (
    CONTENT_SCHEMA_VERSION,
    CanonicalMarketObservationContent,
    MarketObservationContentFingerprint,
    MarketObservationLogicalKey,
    MarketObservationRevisionId,
    canonicalize_market_observation_content,
    canonicalize_market_observation_logical_key,
)
from domain.market_observation_acceptance import (
    MarketObservationAcceptancePolicy,
    MarketObservationCandidateEvidence,
    MarketObservationDecisionKind,
    MarketObservationRevision,
    MarketObservationRoutingRole,
    MarketObservationSourcePolicyRule,
    evaluate_market_observation_candidate,
)
from persistence.market_observation import (
    MarketObservationAcceptanceResult,
    MarketObservationCandidateConflictError,
    MarketObservationCandidateDecisionEvidence,
    MarketObservationDecisionConflictError,
    MarketObservationIdentityConflictError,
    MarketObservationPolicyConflictError,
)


def _json_default(value: object) -> object:
    """Persistence JSON representation；不參與 C23 identity hashing。"""

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, Mapping):
        return dict(value)

    if isinstance(
        value,
        (
            MarketObservationContentFingerprint,
            MarketObservationRevisionId,
        ),
    ):
        return value.value

    raise TypeError(
        f"unsupported persistence JSON value: {type(value)!r}"
    )


def _json_dumps(value: object) -> str:
    return json.dumps(
        value,
        default=_json_default,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _key_signature(
    key: MarketObservationLogicalKey,
) -> tuple[object, ...]:
    return (
        key.instrument_id,
        key.contract_id,
        key.timeframe,
        key.interval_start_at,
    )


def _content_signature(
    content: CanonicalMarketObservationContent,
) -> tuple[object, ...]:
    return (
        CONTENT_SCHEMA_VERSION,
        content.open,
        content.high,
        content.low,
        content.close,
        content.volume,
        content.amount,
        content.trade_count,
        content.tick_count,
        content.trade_date,
        content.session_ref,
    )


def _policy_payload(
    policy: MarketObservationAcceptancePolicy,
) -> dict[str, object]:
    return {
        "policy_id": policy.policy_id,
        "version": policy.version,
        "scope_ref": policy.scope_ref,
        "source_rules": [
            {
                "source_id": rule.source_id,
                "evidence_eligible": rule.evidence_eligible,
                "can_seed_initial_truth": rule.can_seed_initial_truth,
                "authoritative_for_scope": rule.authoritative_for_scope,
                "can_accept_formal_correction": (
                    rule.can_accept_formal_correction
                ),
            }
            for rule in policy.source_rules
        ],
    }


def _candidate_payload(
    candidate: MarketObservationCandidateEvidence,
) -> dict[str, object]:
    return {
        "candidate_id": candidate.candidate_id,
        "logical_key": {
            "instrument_id": candidate.logical_key.instrument_id,
            "contract_id": candidate.logical_key.contract_id,
            "timeframe": candidate.logical_key.timeframe,
            "interval_start_at": (
                candidate.logical_key.interval_start_at.isoformat()
            ),
        },
        "content": {
            "open": candidate.content.open,
            "high": candidate.content.high,
            "low": candidate.content.low,
            "close": candidate.content.close,
            "volume": candidate.content.volume,
            "amount": candidate.content.amount,
            "trade_count": candidate.content.trade_count,
            "tick_count": candidate.content.tick_count,
            "trade_date": candidate.content.trade_date,
            "session_ref": candidate.content.session_ref,
        },
        "content_schema_version": CONTENT_SCHEMA_VERSION,
        "content_fingerprint": candidate.content_fingerprint.value,
        "observation_revision_id": candidate.observation_revision_id.value,
        "source_id": candidate.source_id,
        "routing_role": candidate.routing_role.value,
        "source_record_ref": candidate.source_record_ref,
        "formal_correction_ref": candidate.formal_correction_ref,
        "received_at": candidate.received_at,
        "provenance_json": dict(candidate.provenance_json),
        "acceptance_policy_id": candidate.acceptance_policy_id,
        "acceptance_policy_version": candidate.acceptance_policy_version,
        "acceptance_scope_ref": candidate.acceptance_scope_ref,
    }


def _revision_payload(
    revision: MarketObservationRevision,
) -> dict[str, object]:
    return {
        "observation_revision_id": (
            revision.observation_revision_id.value
        ),
        "logical_key": {
            "instrument_id": revision.logical_key.instrument_id,
            "contract_id": revision.logical_key.contract_id,
            "timeframe": revision.logical_key.timeframe,
            "interval_start_at": (
                revision.logical_key.interval_start_at.isoformat()
            ),
        },
        "content": {
            "open": revision.content.open,
            "high": revision.content.high,
            "low": revision.content.low,
            "close": revision.content.close,
            "volume": revision.content.volume,
            "amount": revision.content.amount,
            "trade_count": revision.content.trade_count,
            "tick_count": revision.content.tick_count,
            "trade_date": revision.content.trade_date,
            "session_ref": revision.content.session_ref,
        },
        "content_schema_version": CONTENT_SCHEMA_VERSION,
        "content_fingerprint": revision.content_fingerprint.value,
        "revision_seq": revision.revision_seq,
        "supersedes_revision_id": (
            None
            if revision.supersedes_revision_id is None
            else revision.supersedes_revision_id.value
        ),
        "accepted_at": revision.accepted_at,
        "acceptance_policy_id": revision.acceptance_policy_id,
        "acceptance_policy_version": (
            revision.acceptance_policy_version
        ),
        "acceptance_scope_ref": revision.acceptance_scope_ref,
    }


def _decision_payload(
    decision: MarketObservationCandidateDecisionEvidence,
) -> dict[str, object]:
    return {
        "decision_id": decision.decision_id,
        "candidate_id": decision.candidate_id,
        "decision_kind": decision.decision_kind.value,
        "decided_at": decision.decided_at,
        "linked_revision_id": (
            None
            if decision.linked_revision_id is None
            else decision.linked_revision_id.value
        ),
        "reason": decision.reason,
        "acceptance_policy_id": decision.acceptance_policy_id,
        "acceptance_policy_version": (
            decision.acceptance_policy_version
        ),
        "acceptance_scope_ref": decision.acceptance_scope_ref,
    }


def _policy_signature(
    policy: MarketObservationAcceptancePolicy,
) -> tuple[object, ...]:
    return (
        policy.policy_id,
        policy.version,
        policy.scope_ref,
        _json_dumps(_policy_payload(policy)),
    )


def _candidate_signature(
    candidate: MarketObservationCandidateEvidence,
) -> tuple[object, ...]:
    return (
        candidate.candidate_id,
        *_key_signature(candidate.logical_key),
        *_content_signature(candidate.content),
        candidate.content_fingerprint.value,
        candidate.observation_revision_id.value,
        candidate.source_id,
        candidate.routing_role.value,
        candidate.source_record_ref,
        candidate.formal_correction_ref,
        candidate.received_at,
        _json_dumps(dict(candidate.provenance_json)),
        candidate.acceptance_policy_id,
        candidate.acceptance_policy_version,
        candidate.acceptance_scope_ref,
    )


def _revision_signature(
    revision: MarketObservationRevision,
) -> tuple[object, ...]:
    return (
        revision.observation_revision_id.value,
        *_key_signature(revision.logical_key),
        *_content_signature(revision.content),
        revision.content_fingerprint.value,
        revision.revision_seq,
        (
            None
            if revision.supersedes_revision_id is None
            else revision.supersedes_revision_id.value
        ),
        revision.accepted_at,
        revision.acceptance_policy_id,
        revision.acceptance_policy_version,
        revision.acceptance_scope_ref,
    )


def _decision_signature(
    decision: MarketObservationCandidateDecisionEvidence,
) -> tuple[object, ...]:
    return (
        decision.decision_id,
        decision.candidate_id,
        decision.decision_kind.value,
        decision.decided_at,
        (
            None
            if decision.linked_revision_id is None
            else decision.linked_revision_id.value
        ),
        decision.reason,
        decision.acceptance_policy_id,
        decision.acceptance_policy_version,
        decision.acceptance_scope_ref,
    )


def classify_market_observation_revision_collision(
    *,
    persisted_signature: tuple[object, ...] | None,
    attempted_revision: MarketObservationRevision,
) -> bool:
    """回傳 False 表示 exact idempotent duplicate；不同 evidence 為 integrity conflict。"""

    if persisted_signature is None:
        raise MarketObservationIdentityConflictError(
            "revision insert conflicted on a database uniqueness constraint "
            "without an exact observation_revision_id match"
        )

    if persisted_signature == _revision_signature(
        attempted_revision
    ):
        return False

    raise MarketObservationIdentityConflictError(
        "observation_revision_id maps to different canonical evidence"
    )


class PostgresMarketObservationAcceptanceRepository:
    """C24 PostgreSQL adapter；所有 transaction commit/rollback 由 caller UoW 控制。"""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def append_policy(
        self,
        policy: MarketObservationAcceptancePolicy,
    ) -> bool:
        payload = _policy_payload(policy)

        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trading.market_observation_acceptance_policies
                    (
                        policy_id,
                        version,
                        scope_ref,
                        policy_json
                    )
                VALUES (%s,%s,%s,%s)
                ON CONFLICT DO NOTHING
                RETURNING policy_id
                """,
                (
                    policy.policy_id,
                    policy.version,
                    policy.scope_ref,
                    _json_dumps(payload),
                ),
            )

            if cursor.fetchone() is not None:
                return True

            cursor.execute(
                """
                SELECT
                    policy_id,
                    version,
                    scope_ref,
                    policy_json::text
                FROM trading.market_observation_acceptance_policies
                WHERE policy_id=%s AND version=%s
                """,
                (
                    policy.policy_id,
                    policy.version,
                ),
            )

            row = cursor.fetchone()

        if row is None:
            raise MarketObservationPolicyConflictError(
                "policy insert conflicted without exact policy identity"
            )

        persisted_json = row[3]

        if not isinstance(persisted_json, str):
            persisted_json = _json_dumps(persisted_json)

        persisted = (
            row[0],
            row[1],
            row[2],
            _json_dumps(json.loads(persisted_json)),
        )

        if persisted != _policy_signature(policy):
            raise MarketObservationPolicyConflictError(
                "policy identity/version maps to different immutable evidence"
            )

        return False

    def _ensure_and_lock_head(
        self,
        logical_key: MarketObservationLogicalKey,
    ) -> tuple[int, str | None, int, bool, str | None]:
        key = _key_signature(logical_key)

        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trading.market_observation_heads
                    (
                        instrument_id,
                        contract_id,
                        timeframe,
                        interval_start_at,
                        current_revision_id,
                        revision_seq,
                        quarantined,
                        quarantine_reason
                    )
                VALUES (%s,%s,%s,%s,NULL,0,FALSE,NULL)
                ON CONFLICT DO NOTHING
                RETURNING head_id
                """,
                key,
            )
            cursor.fetchone()

            cursor.execute(
                """
                SELECT
                    head_id,
                    current_revision_id,
                    revision_seq,
                    quarantined,
                    quarantine_reason
                FROM trading.market_observation_heads
                WHERE instrument_id=%s
                  AND contract_id IS NOT DISTINCT FROM %s
                  AND timeframe=%s
                  AND interval_start_at=%s
                FOR UPDATE
                """,
                key,
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "market observation logical-key head could not be locked"
            )

        return (
            int(row[0]),
            row[1],
            int(row[2]),
            bool(row[3]),
            row[4],
        )

    def _append_candidate(
        self,
        candidate: MarketObservationCandidateEvidence,
    ) -> bool:
        payload = _candidate_payload(candidate)

        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trading.market_observation_candidates
                    (
                        candidate_id,
                        instrument_id,
                        contract_id,
                        timeframe,
                        interval_start_at,
                        content_schema_version,
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                        volume,
                        amount,
                        trade_count,
                        tick_count,
                        trade_date,
                        session_ref,
                        content_fingerprint,
                        observation_revision_id,
                        source_id,
                        routing_role,
                        source_record_ref,
                        formal_correction_ref,
                        received_at,
                        provenance_json,
                        acceptance_policy_id,
                        acceptance_policy_version,
                        acceptance_scope_ref,
                        candidate_json
                    )
                VALUES
                    (
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s
                    )
                ON CONFLICT DO NOTHING
                RETURNING candidate_id
                """,
                (
                    candidate.candidate_id,
                    candidate.logical_key.instrument_id,
                    candidate.logical_key.contract_id,
                    candidate.logical_key.timeframe,
                    candidate.logical_key.interval_start_at,
                    CONTENT_SCHEMA_VERSION,
                    candidate.content.open,
                    candidate.content.high,
                    candidate.content.low,
                    candidate.content.close,
                    candidate.content.volume,
                    candidate.content.amount,
                    candidate.content.trade_count,
                    candidate.content.tick_count,
                    candidate.content.trade_date,
                    candidate.content.session_ref,
                    candidate.content_fingerprint.value,
                    candidate.observation_revision_id.value,
                    candidate.source_id,
                    candidate.routing_role.value,
                    candidate.source_record_ref,
                    candidate.formal_correction_ref,
                    candidate.received_at,
                    _json_dumps(dict(candidate.provenance_json)),
                    candidate.acceptance_policy_id,
                    candidate.acceptance_policy_version,
                    candidate.acceptance_scope_ref,
                    _json_dumps(payload),
                ),
            )

            if cursor.fetchone() is not None:
                return True

            cursor.execute(
                """
                SELECT
                    candidate_id,
                    instrument_id,
                    contract_id,
                    timeframe,
                    interval_start_at,
                    content_schema_version,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume,
                    amount,
                    trade_count,
                    tick_count,
                    trade_date,
                    session_ref,
                    content_fingerprint,
                    observation_revision_id,
                    source_id,
                    routing_role,
                    source_record_ref,
                    formal_correction_ref,
                    received_at,
                    provenance_json::text,
                    acceptance_policy_id,
                    acceptance_policy_version,
                    acceptance_scope_ref
                FROM trading.market_observation_candidates
                WHERE candidate_id=%s
                """,
                (candidate.candidate_id,),
            )

            row = cursor.fetchone()

        if row is None:
            raise MarketObservationCandidateConflictError(
                "candidate insert conflicted without exact candidate identity"
            )

        persisted = (
            *row[:23],
            _json_dumps(json.loads(row[23])),
            *row[24:],
        )

        expected = _candidate_signature(candidate)

        if persisted != expected:
            raise MarketObservationCandidateConflictError(
                "candidate_id maps to different immutable evidence"
            )

        return False

    def _load_revision(
        self,
        revision_id: str,
    ) -> MarketObservationRevision:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    observation_revision_id,
                    instrument_id,
                    contract_id,
                    timeframe,
                    interval_start_at,
                    content_schema_version,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume,
                    amount,
                    trade_count,
                    tick_count,
                    trade_date,
                    session_ref,
                    content_fingerprint,
                    revision_seq,
                    supersedes_revision_id,
                    accepted_at,
                    acceptance_policy_id,
                    acceptance_policy_version,
                    acceptance_scope_ref
                FROM trading.market_observation_revisions
                WHERE observation_revision_id=%s
                """,
                (revision_id,),
            )

            row = cursor.fetchone()

        if row is None:
            raise MarketObservationIdentityConflictError(
                "head references missing accepted revision"
            )

        logical_key = canonicalize_market_observation_logical_key(
            instrument_id=row[1],
            contract_id=row[2],
            requires_contract_id=(row[2] is not None),
            timeframe=row[3],
            interval_start_at=row[4],
        )

        if row[5] != CONTENT_SCHEMA_VERSION:
            raise MarketObservationIdentityConflictError(
                "unsupported persisted content schema version"
            )

        content = canonicalize_market_observation_content(
            open=row[6],
            high=row[7],
            low=row[8],
            close=row[9],
            volume=row[10],
            amount=row[11],
            trade_count=row[12],
            tick_count=row[13],
            trade_date=row[14],
            session_ref=row[15],
        )

        return MarketObservationRevision(
            observation_revision_id=(
                MarketObservationRevisionId(row[0])
            ),
            logical_key=logical_key,
            content=content,
            content_fingerprint=(
                MarketObservationContentFingerprint(row[16])
            ),
            revision_seq=row[17],
            supersedes_revision_id=(
                None
                if row[18] is None
                else MarketObservationRevisionId(row[18])
            ),
            accepted_at=row[19],
            acceptance_policy_id=row[20],
            acceptance_policy_version=row[21],
            acceptance_scope_ref=row[22],
        )

    def _revision_persisted_signature(
        self,
        revision_id: str,
    ) -> tuple[object, ...] | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    observation_revision_id,
                    instrument_id,
                    contract_id,
                    timeframe,
                    interval_start_at,
                    content_schema_version,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume,
                    amount,
                    trade_count,
                    tick_count,
                    trade_date,
                    session_ref,
                    content_fingerprint,
                    revision_seq,
                    supersedes_revision_id,
                    accepted_at,
                    acceptance_policy_id,
                    acceptance_policy_version,
                    acceptance_scope_ref
                FROM trading.market_observation_revisions
                WHERE observation_revision_id=%s
                """,
                (revision_id,),
            )

            row = cursor.fetchone()

        return None if row is None else tuple(row)

    def _append_revision(
        self,
        revision: MarketObservationRevision,
    ) -> bool:
        payload = _revision_payload(revision)

        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trading.market_observation_revisions
                    (
                        observation_revision_id,
                        instrument_id,
                        contract_id,
                        timeframe,
                        interval_start_at,
                        content_schema_version,
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                        volume,
                        amount,
                        trade_count,
                        tick_count,
                        trade_date,
                        session_ref,
                        content_fingerprint,
                        revision_seq,
                        supersedes_revision_id,
                        accepted_at,
                        acceptance_policy_id,
                        acceptance_policy_version,
                        acceptance_scope_ref,
                        revision_json
                    )
                VALUES
                    (
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s
                    )
                ON CONFLICT DO NOTHING
                RETURNING observation_revision_id
                """,
                (
                    revision.observation_revision_id.value,
                    revision.logical_key.instrument_id,
                    revision.logical_key.contract_id,
                    revision.logical_key.timeframe,
                    revision.logical_key.interval_start_at,
                    CONTENT_SCHEMA_VERSION,
                    revision.content.open,
                    revision.content.high,
                    revision.content.low,
                    revision.content.close,
                    revision.content.volume,
                    revision.content.amount,
                    revision.content.trade_count,
                    revision.content.tick_count,
                    revision.content.trade_date,
                    revision.content.session_ref,
                    revision.content_fingerprint.value,
                    revision.revision_seq,
                    (
                        None
                        if revision.supersedes_revision_id is None
                        else revision.supersedes_revision_id.value
                    ),
                    revision.accepted_at,
                    revision.acceptance_policy_id,
                    revision.acceptance_policy_version,
                    revision.acceptance_scope_ref,
                    _json_dumps(payload),
                ),
            )

            if cursor.fetchone() is not None:
                return True

        persisted = self._revision_persisted_signature(
            revision.observation_revision_id.value
        )

        return classify_market_observation_revision_collision(
            persisted_signature=persisted,
            attempted_revision=revision,
        )

    def _append_decision(
        self,
        decision: MarketObservationCandidateDecisionEvidence,
    ) -> bool:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trading.market_observation_candidate_decisions
                    (
                        decision_id,
                        candidate_id,
                        decision_kind,
                        decided_at,
                        linked_revision_id,
                        reason,
                        acceptance_policy_id,
                        acceptance_policy_version,
                        acceptance_scope_ref,
                        decision_json
                    )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING
                RETURNING decision_id
                """,
                (
                    decision.decision_id,
                    decision.candidate_id,
                    decision.decision_kind.value,
                    decision.decided_at,
                    (
                        None
                        if decision.linked_revision_id is None
                        else decision.linked_revision_id.value
                    ),
                    decision.reason,
                    decision.acceptance_policy_id,
                    decision.acceptance_policy_version,
                    decision.acceptance_scope_ref,
                    _json_dumps(_decision_payload(decision)),
                ),
            )

            if cursor.fetchone() is not None:
                return True

            cursor.execute(
                """
                SELECT
                    decision_id,
                    candidate_id,
                    decision_kind,
                    decided_at,
                    linked_revision_id,
                    reason,
                    acceptance_policy_id,
                    acceptance_policy_version,
                    acceptance_scope_ref
                FROM trading.market_observation_candidate_decisions
                WHERE decision_id=%s
                """,
                (decision.decision_id,),
            )

            row = cursor.fetchone()

        if row is None or tuple(row) != _decision_signature(decision):
            raise MarketObservationDecisionConflictError(
                "decision_id maps to different immutable evidence"
            )

        return False

    def _append_revision_evidence(
        self,
        *,
        candidate_id: str,
        revision_id: MarketObservationRevisionId,
        evidence_kind: str,
        recorded_at: datetime,
    ) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trading.market_observation_revision_evidence
                    (
                        candidate_id,
                        observation_revision_id,
                        evidence_kind,
                        recorded_at
                    )
                VALUES (%s,%s,%s,%s)
                ON CONFLICT DO NOTHING
                """,
                (
                    candidate_id,
                    revision_id.value,
                    evidence_kind,
                    recorded_at,
                ),
            )

    def _set_accepted_head(
        self,
        *,
        head_id: int,
        revision: MarketObservationRevision,
    ) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE trading.market_observation_heads
                SET
                    current_revision_id=%s,
                    revision_seq=%s,
                    quarantined=FALSE,
                    quarantine_reason=NULL
                WHERE head_id=%s
                """,
                (
                    revision.observation_revision_id.value,
                    revision.revision_seq,
                    head_id,
                ),
            )

    def _set_quarantine_head(
        self,
        *,
        head_id: int,
        reason: str,
    ) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE trading.market_observation_heads
                SET
                    quarantined=TRUE,
                    quarantine_reason=%s
                WHERE head_id=%s
                """,
                (
                    reason,
                    head_id,
                ),
            )

    def process_candidate(
        self,
        *,
        policy: MarketObservationAcceptancePolicy,
        candidate: MarketObservationCandidateEvidence,
        decision_id: str,
        decided_at: datetime,
    ) -> MarketObservationAcceptanceResult:
        """Caller UoW 內 atomically preserve candidate/decision/revision/head。"""

        self.append_policy(policy)

        (
            head_id,
            current_revision_id,
            current_revision_seq,
            _was_quarantined,
            _quarantine_reason,
        ) = self._ensure_and_lock_head(candidate.logical_key)

        try:
            self._append_candidate(candidate)
        except MarketObservationCandidateConflictError as error:
            decision = MarketObservationCandidateDecisionEvidence(
                decision_id=decision_id,
                candidate_id=candidate.candidate_id,
                decision_kind=(
                    MarketObservationDecisionKind.IDENTITY_CONFLICT
                ),
                decided_at=decided_at,
                linked_revision_id=(
                    None
                    if current_revision_id is None
                    else MarketObservationRevisionId(
                        current_revision_id
                    )
                ),
                reason="CANDIDATE_IDENTITY_CONFLICT",
                acceptance_policy_id=policy.policy_id,
                acceptance_policy_version=policy.version,
                acceptance_scope_ref=policy.scope_ref,
            )

            self._append_decision(decision)
            self._set_quarantine_head(
                head_id=head_id,
                reason="CANDIDATE_IDENTITY_CONFLICT",
            )

            return MarketObservationAcceptanceResult(
                decision=decision,
                accepted_revision=None,
                current_revision_id=(
                    None
                    if current_revision_id is None
                    else MarketObservationRevisionId(
                        current_revision_id
                    )
                ),
                current_revision_seq=current_revision_seq,
                quarantined=True,
                integrity_error=error,
            )

        current_revision = (
            None
            if current_revision_id is None
            else self._load_revision(current_revision_id)
        )

        plan = evaluate_market_observation_candidate(
            policy=policy,
            candidate=candidate,
            current_revision=current_revision,
            accepted_at=decided_at,
        )

        decision = MarketObservationCandidateDecisionEvidence(
            decision_id=decision_id,
            candidate_id=candidate.candidate_id,
            decision_kind=plan.decision_kind,
            decided_at=decided_at,
            linked_revision_id=plan.linked_revision_id,
            reason=plan.quarantine_reason,
            acceptance_policy_id=policy.policy_id,
            acceptance_policy_version=policy.version,
            acceptance_scope_ref=policy.scope_ref,
        )

        if plan.accepted_revision is not None:
            try:
                self._append_revision(plan.accepted_revision)
            except MarketObservationIdentityConflictError as error:
                conflict_decision = (
                    MarketObservationCandidateDecisionEvidence(
                        decision_id=decision_id,
                        candidate_id=candidate.candidate_id,
                        decision_kind=(
                            MarketObservationDecisionKind.IDENTITY_CONFLICT
                        ),
                        decided_at=decided_at,
                        linked_revision_id=(
                            None
                            if current_revision is None
                            else current_revision.observation_revision_id
                        ),
                        reason="REVISION_IDENTITY_CONFLICT",
                        acceptance_policy_id=policy.policy_id,
                        acceptance_policy_version=policy.version,
                        acceptance_scope_ref=policy.scope_ref,
                    )
                )

                self._append_decision(conflict_decision)
                self._set_quarantine_head(
                    head_id=head_id,
                    reason="REVISION_IDENTITY_CONFLICT",
                )

                return MarketObservationAcceptanceResult(
                    decision=conflict_decision,
                    accepted_revision=None,
                    current_revision_id=(
                        None
                        if current_revision is None
                        else current_revision.observation_revision_id
                    ),
                    current_revision_seq=current_revision_seq,
                    quarantined=True,
                    integrity_error=error,
                )

            self._append_decision(decision)
            self._append_revision_evidence(
                candidate_id=candidate.candidate_id,
                revision_id=(
                    plan.accepted_revision.observation_revision_id
                ),
                evidence_kind="ACCEPTED",
                recorded_at=decision.decided_at,
            )
            self._set_accepted_head(
                head_id=head_id,
                revision=plan.accepted_revision,
            )

            return MarketObservationAcceptanceResult(
                decision=decision,
                accepted_revision=plan.accepted_revision,
                current_revision_id=(
                    plan.accepted_revision.observation_revision_id
                ),
                current_revision_seq=(
                    plan.accepted_revision.revision_seq
                ),
                quarantined=False,
            )

        self._append_decision(decision)

        if (
            plan.decision_kind
            is MarketObservationDecisionKind.CORROBORATED_EXISTING
        ):
            if plan.linked_revision_id is None:
                raise RuntimeError(
                    "corroboration requires existing revision"
                )

            self._append_revision_evidence(
                candidate_id=candidate.candidate_id,
                revision_id=plan.linked_revision_id,
                evidence_kind="CORROBORATED",
                recorded_at=decision.decided_at,
            )

            return MarketObservationAcceptanceResult(
                decision=decision,
                accepted_revision=None,
                current_revision_id=plan.linked_revision_id,
                current_revision_seq=current_revision_seq,
                quarantined=False,
            )

        if plan.quarantine_reason is None:
            raise RuntimeError(
                "quarantine decision requires explicit reason"
            )

        self._set_quarantine_head(
            head_id=head_id,
            reason=plan.quarantine_reason,
        )

        return MarketObservationAcceptanceResult(
            decision=decision,
            accepted_revision=None,
            current_revision_id=(
                None
                if current_revision is None
                else current_revision.observation_revision_id
            ),
            current_revision_seq=current_revision_seq,
            quarantined=True,
        )


__all__ = [
    "PostgresMarketObservationAcceptanceRepository",
    "classify_market_observation_revision_collision",
]
