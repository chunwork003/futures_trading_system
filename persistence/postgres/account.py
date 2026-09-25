from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from persistence.account import AccountPositionSnapshot, BrokerPositionObservation
from trading.account import AccountSnapshot


class PostgresExpectedPositionSnapshotRepository:
    def __init__(self, connection: Any) -> None: self._connection = connection
    def append(self, snapshot: AccountPositionSnapshot) -> None:
        with self._connection.cursor() as c:
            c.execute("INSERT INTO trading.expected_position_snapshots (snapshot_id, broker, account_ref, effective_at, recorded_at, source_event_id, snapshot_json) VALUES (%s,%s,%s,%s,%s,%s,%s)", (snapshot.snapshot_id, snapshot.broker, snapshot.account_ref, snapshot.effective_at, snapshot.recorded_at, snapshot.source_event_id, snapshot.model_dump_json()))
            for index, position in enumerate(snapshot.positions):
                c.execute("INSERT INTO trading.expected_position_snapshot_items (snapshot_id,item_index,instrument_id,contract_id,direction,quantity) VALUES (%s,%s,%s,%s,%s,%s)", (snapshot.snapshot_id,index,position.instrument_id,position.contract_id,position.direction.value,position.quantity))
    def _one(self, condition: str, params: tuple[Any, ...]):
        with self._connection.cursor() as c:
            c.execute(f"SELECT snapshot_json FROM trading.expected_position_snapshots WHERE {condition} ORDER BY effective_at DESC, recorded_at DESC, snapshot_id DESC LIMIT 1", params); row=c.fetchone()
        if row is None: return None
        return AccountPositionSnapshot.model_validate_json(row[0]) if isinstance(row[0], str) else AccountPositionSnapshot.model_validate(row[0])
    def latest(self, broker: str, account_ref: str): return self._one("broker=%s AND account_ref=%s", (broker, account_ref))
    def as_of(self, broker: str, account_ref: str, at: datetime): return self._one("broker=%s AND account_ref=%s AND effective_at<=%s", (broker, account_ref, at))
    def load_positions(self, account):
        """ExpectedPositionLoader compatibility；空/缺少 snapshot 均以明確 FLAT collection 回傳。"""
        snapshot = self.latest(account.broker, account.account_ref)
        return () if snapshot is None else snapshot.positions


class PostgresBrokerPositionObservationRepository:
    def __init__(self, connection: Any) -> None: self._connection = connection
    def append(self, observation: BrokerPositionObservation) -> None:
        with self._connection.cursor() as c:
            c.execute("INSERT INTO trading.broker_position_observations (observation_id, broker, account_ref, observed_at, recorded_at, observation_json) VALUES (%s,%s,%s,%s,%s,%s)", (observation.observation_id, observation.broker, observation.account_ref, observation.observed_at, observation.recorded_at, observation.model_dump_json()))
            for index, position in enumerate(observation.positions):
                c.execute("INSERT INTO trading.broker_position_observation_items (observation_id,item_index,instrument_id,contract_id,direction,quantity,average_price) VALUES (%s,%s,%s,%s,%s,%s,%s)", (observation.observation_id,index,position.instrument_id,position.contract_id,position.direction.value,position.quantity,position.average_price))


class PostgresAccountSnapshotRepository:
    def __init__(self, connection: Any) -> None: self._connection = connection
    def append(self, snapshot: AccountSnapshot) -> None:
        with self._connection.cursor() as c:
            c.execute("INSERT INTO trading.account_snapshots (snapshot_id, broker, account_ref, observed_at, recorded_at, cash_balance, equity, available_funds, margin_used, snapshot_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (snapshot.snapshot_id, snapshot.broker, snapshot.account_ref, snapshot.observed_at, snapshot.recorded_at, snapshot.cash_balance, snapshot.equity, snapshot.available_funds, snapshot.margin_used, snapshot.model_dump_json()))
