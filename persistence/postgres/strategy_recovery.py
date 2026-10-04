from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from persistence.contracts import normalize_stable_id
from persistence.strategy_recovery import (
    StrategyTransitionHeadConflictError,
    StrategyTransitionPersistenceIntegrityError,
)
from strategy.recovery import StrategyGoverningTransitionAuthority


def _decode_authority(
    payload: object,
) -> StrategyGoverningTransitionAuthority:
    if isinstance(payload, str):
        return StrategyGoverningTransitionAuthority.model_validate_json(payload)
    if isinstance(payload, Mapping):
        return StrategyGoverningTransitionAuthority.model_validate(payload)
    raise StrategyTransitionPersistenceIntegrityError(
        "transition_json must contain structured C17 authority"
    )


class PostgresStrategyGoverningTransitionRepository:
    """C17 PostgreSQL adapter；current authority 只由 exact head pointer 決定。"""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def append(
        self,
        authority: StrategyGoverningTransitionAuthority,
    ) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    strategy_instance_id,
                    transition_json
                FROM trading.strategy_governing_transition_authorities
                WHERE transition_id=%s
                """,
                (authority.transition_id,),
            )
            row = cursor.fetchone()

            if row is not None:
                existing = _decode_authority(row[1])
                if (
                    row[0] != authority.strategy_instance_id
                    or existing != authority
                ):
                    raise StrategyTransitionPersistenceIntegrityError(
                        "existing C17 transition identity has different authority material"
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
                    json.dumps(
                        authority.model_dump(mode="json"),
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    ),
                ),
            )

    def advance_head(
        self,
        *,
        strategy_instance_id: str,
        transition_id: str,
        expected_head_revision: int,
    ) -> int:
        strategy_instance_id = normalize_stable_id(strategy_instance_id)
        transition_id = normalize_stable_id(transition_id)
        if expected_head_revision < 0:
            raise ValueError("expected_head_revision must be non-negative")

        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT strategy_instance_id
                FROM trading.strategy_governing_transition_authorities
                WHERE transition_id=%s
                """,
                (transition_id,),
            )
            authority_row = cursor.fetchone()
            if (
                authority_row is None
                or authority_row[0] != strategy_instance_id
            ):
                raise StrategyTransitionPersistenceIntegrityError(
                    "transition head target does not resolve exact StrategyInstance authority"
                )

            cursor.execute(
                """
                SELECT
                    transition_id,
                    head_revision
                FROM trading.strategy_governing_transition_heads
                WHERE strategy_instance_id=%s
                FOR UPDATE
                """,
                (strategy_instance_id,),
            )
            head = cursor.fetchone()

            if head is None:
                if expected_head_revision != 0:
                    raise StrategyTransitionHeadConflictError(
                        "C17 transition head revision conflict"
                    )

                cursor.execute(
                    """
                    INSERT INTO trading.strategy_governing_transition_heads
                        (
                            strategy_instance_id,
                            transition_id,
                            head_revision
                        )
                    VALUES (%s,%s,1)
                    RETURNING head_revision
                    """,
                    (
                        strategy_instance_id,
                        transition_id,
                    ),
                )
                created = cursor.fetchone()
                if created is None or created[0] != 1:
                    raise StrategyTransitionHeadConflictError(
                        "C17 transition head creation failed"
                    )
                return 1

            current_transition_id = head[0]
            current_revision = head[1]

            if current_revision != expected_head_revision:
                raise StrategyTransitionHeadConflictError(
                    "C17 transition head revision conflict"
                )

            if current_transition_id == transition_id:
                return current_revision

            cursor.execute(
                """
                UPDATE trading.strategy_governing_transition_heads
                SET
                    transition_id=%s,
                    head_revision=head_revision+1,
                    recorded_at=CURRENT_TIMESTAMP
                WHERE
                    strategy_instance_id=%s
                    AND head_revision=%s
                RETURNING head_revision
                """,
                (
                    transition_id,
                    strategy_instance_id,
                    expected_head_revision,
                ),
            )
            advanced = cursor.fetchone()
            if advanced is None:
                raise StrategyTransitionHeadConflictError(
                    "C17 transition head compare-and-swap failed"
                )

            return advanced[0]

    def current(
        self,
        strategy_instance_id: str,
    ) -> StrategyGoverningTransitionAuthority | None:
        strategy_instance_id = normalize_stable_id(strategy_instance_id)

        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    h.transition_id,
                    h.head_revision,
                    a.strategy_instance_id,
                    a.source_config_version,
                    a.source_config_fingerprint,
                    a.source_implementation_revision,
                    a.source_instrument_id,
                    a.target_config_version,
                    a.target_config_fingerprint,
                    a.target_implementation_revision,
                    a.target_instrument_id,
                    a.transition_policy_id,
                    a.transition_policy_version,
                    a.transition_json
                FROM trading.strategy_governing_transition_heads h
                JOIN trading.strategy_governing_transition_authorities a
                    ON a.transition_id=h.transition_id
                    AND a.strategy_instance_id=h.strategy_instance_id
                WHERE h.strategy_instance_id=%s
                """,
                (strategy_instance_id,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        if row[1] < 1:
            raise StrategyTransitionPersistenceIntegrityError(
                "C17 transition head revision is invalid"
            )

        authority = _decode_authority(row[13])

        structured = (
            row[0],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
            row[9],
            row[10],
            row[11],
            row[12],
        )
        canonical = (
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
        )

        if authority.strategy_instance_id != strategy_instance_id:
            raise StrategyTransitionPersistenceIntegrityError(
                "C17 transition head conflicts with requested StrategyInstance"
            )

        if structured != canonical:
            raise StrategyTransitionPersistenceIntegrityError(
                "C17 transition structured authority conflicts with transition_json"
            )

        return authority


__all__ = [
    "PostgresStrategyGoverningTransitionRepository",
]
