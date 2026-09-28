from __future__ import annotations

from datetime import datetime
from typing import Any

from persistence.account import (
    AccountPositionSnapshot,
    BrokerObservationIntegrityError,
    BrokerPositionObservation,
    ExpectedSnapshotIntegrityError,
    ExpectedStateBaselineNotEstablishedError,
    ExpectedStateRead,
    ExpectedStateReadError,
)
from trading.account import AccountSnapshot, BrokerAccount
from persistence.postgres.readiness_fence import PostgresRecoveryReadinessFenceRepository


class PostgresExpectedPositionSnapshotRepository:
    """PostgreSQL expected-state snapshot adapter。

    C01 responsibility：
    - decode durable complete snapshot。
    - distinguish explicit FLAT / expected positions。
    - fail closed when baseline evidence is missing。
    - preserve typed read / integrity failures。

    不負責：
    - initialization authority。
    - AccountStateHead / checkpoint。
    - RecoveryCut。
    """

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def append(
        self,
        snapshot: AccountPositionSnapshot,
    ) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trading.expected_position_snapshots
                    (
                        snapshot_id,
                        broker,
                        account_ref,
                        effective_at,
                        recorded_at,
                        source_event_id,
                        snapshot_json
                    )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    snapshot.snapshot_id,
                    snapshot.broker,
                    snapshot.account_ref,
                    snapshot.effective_at,
                    snapshot.recorded_at,
                    snapshot.source_event_id,
                    snapshot.model_dump_json(),
                ),
            )

            for index, position in enumerate(snapshot.positions):
                cursor.execute(
                    """
                    INSERT INTO trading.expected_position_snapshot_items
                        (
                            snapshot_id,
                            item_index,
                            instrument_id,
                            contract_id,
                            direction,
                            quantity
                        )
                    VALUES (%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        snapshot.snapshot_id,
                        index,
                        position.instrument_id,
                        position.contract_id,
                        position.direction.value,
                        position.quantity,
                    ),
                )

    def _one(
        self,
        condition: str,
        params: tuple[Any, ...],
    ) -> AccountPositionSnapshot | None:
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT snapshot_json
                    FROM trading.expected_position_snapshots
                    WHERE {condition}
                    ORDER BY
                        effective_at DESC,
                        recorded_at DESC,
                        snapshot_id DESC
                    LIMIT 1
                    """,
                    params,
                )
                row = cursor.fetchone()
        except Exception as exc:
            raise ExpectedStateReadError(
                "expected-state snapshot read failed"
            ) from exc

        if row is None:
            return None

        try:
            payload = row[0]

            if isinstance(payload, str):
                return AccountPositionSnapshot.model_validate_json(
                    payload
                )

            return AccountPositionSnapshot.model_validate(
                payload
            )
        except Exception as exc:
            raise ExpectedSnapshotIntegrityError(
                "expected-state snapshot failed canonical decode"
            ) from exc

    def latest(
        self,
        broker: str,
        account_ref: str,
    ) -> AccountPositionSnapshot | None:
        return self._one(
            "broker=%s AND account_ref=%s",
            (broker, account_ref),
        )

    def as_of(
        self,
        broker: str,
        account_ref: str,
        at: datetime,
    ) -> AccountPositionSnapshot | None:
        return self._one(
            "broker=%s AND account_ref=%s AND effective_at<=%s",
            (broker, account_ref, at),
        )

    def get_exact(self, *, snapshot_id: str, broker: str, account_ref: str) -> AccountPositionSnapshot | None:
        """只依 durable identity 與帳戶範圍讀取；不得退回 latest/as-of。"""
        snapshot = self._one("snapshot_id=%s AND broker=%s AND account_ref=%s", (snapshot_id, broker, account_ref))
        if snapshot is None:
            return None
        if snapshot.snapshot_id != snapshot_id:
            raise ExpectedSnapshotIntegrityError("expected-state snapshot exact identity mismatch")
        if snapshot.broker != broker or snapshot.account_ref != account_ref:
            raise ExpectedSnapshotIntegrityError("expected-state snapshot exact account scope mismatch")
        return snapshot

    def read_expected_state(
        self,
        account: BrokerAccount,
    ) -> ExpectedStateRead:
        """讀取 authoritative expected state；missing baseline 必須 fail closed。"""

        snapshot = self.latest(
            account.broker,
            account.account_ref,
        )

        if snapshot is None:
            raise ExpectedStateBaselineNotEstablishedError(
                "expected-state baseline is not established"
            )

        if (
            snapshot.broker != account.broker
            or snapshot.account_ref != account.account_ref
        ):
            raise ExpectedSnapshotIntegrityError(
                "expected-state snapshot account scope mismatch"
            )

        try:
            return ExpectedStateRead.from_snapshot(snapshot)
        except ValueError as exc:
            raise ExpectedSnapshotIntegrityError(
                "expected-state snapshot violates authority invariants"
            ) from exc

    def load_positions(
        self,
        account: BrokerAccount,
    ) -> tuple:
        """ExpectedPositionLoader compatibility。

        只有 durable explicit FLAT 可以回傳空 tuple。
        Missing baseline 不得再被解讀成 FLAT。
        """

        result = self.read_expected_state(account)

        return result.positions


class PostgresBrokerPositionObservationRepository:
    def __init__(self, connection: Any) -> None:
        self._connection = connection
        self._readiness_fence = PostgresRecoveryReadinessFenceRepository(connection)

    def append(
        self,
        observation: BrokerPositionObservation,
    ) -> None:
        token = self._readiness_fence.lock_active(
            BrokerAccount(broker=observation.broker, account_ref=observation.account_ref)
        )
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trading.broker_position_observations
                    (
                        observation_id,
                        broker,
                        account_ref,
                        observed_at,
                        recorded_at,
                        observation_json
                    )
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (
                    observation.observation_id,
                    observation.broker,
                    observation.account_ref,
                    observation.observed_at,
                    observation.recorded_at,
                    observation.model_dump_json(),
                ),
            )

            for index, position in enumerate(observation.positions):
                cursor.execute(
                    """
                    INSERT INTO trading.broker_position_observation_items
                        (
                            observation_id,
                            item_index,
                            instrument_id,
                            contract_id,
                            direction,
                            quantity,
                            average_price
                        )
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        observation.observation_id,
                        index,
                        position.instrument_id,
                        position.contract_id,
                        position.direction.value,
                        position.quantity,
                        position.average_price,
                    ),
                )
        if token is not None:
            self._readiness_fence.advance_locked(token)

    def get_exact(self, *, observation_id: str, broker: str, account_ref: str) -> BrokerPositionObservation | None:
        """讀取指定 observation；missing/wrong scope 均不得形成 positive authority。"""
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT observation_json FROM trading.broker_position_observations WHERE observation_id=%s AND broker=%s AND account_ref=%s", (observation_id, broker, account_ref))
            row = cursor.fetchone()
        if row is None:
            return None
        try:
            payload = row[0]
            observation = BrokerPositionObservation.model_validate_json(payload) if isinstance(payload, str) else BrokerPositionObservation.model_validate(payload)
        except Exception as exc:
            raise BrokerObservationIntegrityError("broker-position observation failed canonical decode") from exc
        if observation.observation_id != observation_id:
            raise BrokerObservationIntegrityError("broker-position observation exact identity mismatch")
        if observation.broker != broker or observation.account_ref != account_ref:
            raise BrokerObservationIntegrityError("broker-position observation exact account scope mismatch")
        return observation


class PostgresAccountSnapshotRepository:
    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def append(
        self,
        snapshot: AccountSnapshot,
    ) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO trading.account_snapshots
                    (
                        snapshot_id,
                        broker,
                        account_ref,
                        observed_at,
                        recorded_at,
                        cash_balance,
                        equity,
                        available_funds,
                        margin_used,
                        snapshot_json
                    )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    snapshot.snapshot_id,
                    snapshot.broker,
                    snapshot.account_ref,
                    snapshot.observed_at,
                    snapshot.recorded_at,
                    snapshot.cash_balance,
                    snapshot.equity,
                    snapshot.available_funds,
                    snapshot.margin_used,
                    snapshot.model_dump_json(),
                ),
            )
