
from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from persistence.strategy_state import (
    LegacyMarketObservationReferenceError,
    StrategyStateReferenceConflictError,
    StrategyStateSnapshot,
    normalize_market_observation_revision_id,
)
from strategy.instance import (
    StrategyInstance,
    canonical_config_json,
)


class PostgresStrategyInstanceRepository:
    def __init__(
        self,
        connection: Any,
    ) -> None:
        self._connection = connection

    def append(
        self,
        instance: StrategyInstance,
    ) -> None:
        with (
            self._connection.cursor()
            as cursor
        ):
            cursor.execute(
                """
                INSERT INTO trading.strategy_instances
                    (
                        strategy_instance_id,
                        strategy_id,
                        strategy_version,
                        config_version,
                        config_fingerprint,
                        instrument_id,
                        timeframe,
                        config_json,
                        instance_json
                    )
                VALUES
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    instance.strategy_instance_id,
                    instance.strategy_id,
                    instance.strategy_version,
                    instance.config_version,
                    instance.config_fingerprint,
                    instance.instrument_id,
                    instance.timeframe,
                    json.dumps(instance.config_json, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
                    instance.model_dump_json(),
                ),
            )

    def get(
        self,
        strategy_instance_id: str,
    ):
        with (
            self._connection.cursor()
            as cursor
        ):
            cursor.execute(
                """
                SELECT
                    strategy_instance_id,
                    strategy_id,
                    strategy_version,
                    config_version,
                    config_fingerprint,
                    instrument_id,
                    timeframe,
                    config_json,
                    instance_json
                FROM trading.strategy_instances
                WHERE strategy_instance_id=%s
                """,
                (
                    strategy_instance_id,
                ),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        payload = row[8]
        if isinstance(payload, str):
            instance = StrategyInstance.model_validate_json(payload)
        elif isinstance(payload, Mapping):
            instance = StrategyInstance.model_validate(payload)
        else:
            raise ValueError(
                "instance_json must contain structured StrategyInstance authority"
            )

        config_payload = row[7]
        if isinstance(config_payload, str):
            try:
                config_payload = json.loads(config_payload)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "structured config_json is not valid JSON authority"
                ) from exc

        structured_config = canonical_config_json(config_payload)
        structured = (
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            structured_config,
        )
        canonical = (
            instance.strategy_instance_id,
            instance.strategy_id,
            instance.strategy_version,
            instance.config_version,
            instance.config_fingerprint,
            instance.instrument_id,
            instance.timeframe,
            instance.config_json,
        )

        if instance.strategy_instance_id != strategy_instance_id:
            raise ValueError(
                "persisted StrategyInstance identity conflicts with requested identity"
            )
        if structured != canonical:
            raise ValueError(
                "persisted StrategyInstance structured authority conflicts "
                "with canonical instance_json"
            )

        return instance


class PostgresStrategyStateRepository:
    """Canonical mor1 structured column ??? strategy recovery authority?"""

    def __init__(
        self,
        connection: Any,
    ) -> None:
        self._connection = connection

    def append(
        self,
        snapshot: StrategyStateSnapshot,
    ) -> None:
        canonical = (
            snapshot
            .last_market_observation_revision_id
        )

        with (
            self._connection.cursor()
            as cursor
        ):
            cursor.execute(
                """
                INSERT INTO trading.strategy_state_snapshots
                    (
                        snapshot_id,
                        strategy_instance_id,
                        captured_at,
                        strategy_id,
                        strategy_version,
                        config_version,
                        config_fingerprint,
                        instrument_id,
                        timeframe,
                        state_schema_version,
                        last_market_observation_id,
                        last_market_observation_revision_id,
                        state_json,
                        snapshot_json
                    )
                VALUES
                    (
                        %s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s
                    )
                """,
                (
                    snapshot.snapshot_id,
                    snapshot.strategy_instance_id,
                    snapshot.captured_at,
                    snapshot.strategy_id,
                    snapshot.strategy_version,
                    snapshot.config_version,
                    snapshot.config_fingerprint,
                    snapshot.instrument_id,
                    snapshot.timeframe,
                    snapshot.state_schema_version,
                    canonical,
                    canonical,
                    json.dumps(snapshot.state_json, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
                    snapshot.model_dump_json(),
                ),
            )

    def latest(
        self,
        strategy_instance_id: str,
    ) -> (
        StrategyStateSnapshot
        | None
    ):
        with (
            self._connection.cursor()
            as cursor
        ):
            cursor.execute(
                """
                SELECT
                    last_market_observation_id,
                    last_market_observation_revision_id,
                    snapshot_json
                FROM trading.strategy_state_snapshots
                WHERE strategy_instance_id=%s
                ORDER BY
                    captured_at DESC,
                    snapshot_id DESC
                LIMIT 1
                """,
                (
                    strategy_instance_id,
                ),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        legacy_column = row[0]
        canonical_column = row[1]
        snapshot_payload = row[2]

        if canonical_column is None:
            raise (
                LegacyMarketObservationReferenceError(
                    "legacy-only strategy snapshot "
                    "cannot satisfy canonical "
                    "recovery authority"
                )
            )

        canonical = (
            normalize_market_observation_revision_id(
                canonical_column
            )
        )

        if legacy_column is None:
            raise (
                StrategyStateReferenceConflictError(
                    "canonical strategy snapshot "
                    "requires legacy compatibility "
                    "column mirror"
                )
            )

        legacy = (
            normalize_market_observation_revision_id(
                legacy_column
            )
        )

        if legacy != canonical:
            raise (
                StrategyStateReferenceConflictError(
                    "persisted legacy/canonical "
                    "market observation references "
                    "disagree"
                )
            )

        if isinstance(
            snapshot_payload,
            str,
        ):
            payload = json.loads(
                snapshot_payload
            )
        elif isinstance(
            snapshot_payload,
            Mapping,
        ):
            payload = dict(
                snapshot_payload
            )
        else:
            raise (
                StrategyStateReferenceConflictError(
                    "snapshot_json must contain "
                    "structured snapshot evidence"
                )
            )

        payload_canonical_raw = (
            payload.get(
                "last_market_observation_revision_id"
            )
        )

        payload_legacy_raw = (
            payload.pop(
                "last_market_observation_id",
                None,
            )
        )

        if (
            payload_canonical_raw
            is not None
        ):
            payload_canonical = (
                normalize_market_observation_revision_id(
                    payload_canonical_raw
                )
            )

            if (
                payload_canonical
                != canonical
            ):
                raise (
                    StrategyStateReferenceConflictError(
                        "snapshot_json canonical "
                        "reference disagrees with "
                        "structured column"
                    )
                )

        if (
            payload_legacy_raw
            is not None
        ):
            payload_legacy = (
                normalize_market_observation_revision_id(
                    payload_legacy_raw
                )
            )

            if payload_legacy != canonical:
                raise (
                    StrategyStateReferenceConflictError(
                        "snapshot_json legacy "
                        "reference disagrees with "
                        "canonical column"
                    )
                )

        payload[
            "last_market_observation_revision_id"
        ] = canonical

        return (
            StrategyStateSnapshot
            .model_validate(
                payload
            )
        )
