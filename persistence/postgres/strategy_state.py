from __future__ import annotations

from typing import Any

from persistence.strategy_state import StrategyStateSnapshot
from strategy.instance import StrategyInstance


class PostgresStrategyInstanceRepository:
    def __init__(self, connection: Any) -> None: self._connection = connection
    def append(self, instance: StrategyInstance) -> None:
        with self._connection.cursor() as c: c.execute("INSERT INTO trading.strategy_instances (strategy_instance_id,strategy_id,strategy_version,config_version,config_fingerprint,instrument_id,timeframe,config_json,instance_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (instance.strategy_instance_id,instance.strategy_id,instance.strategy_version,instance.config_version,instance.config_fingerprint,instance.instrument_id,instance.timeframe,instance.config_json,instance.model_dump_json()))
    def get(self, strategy_instance_id: str):
        with self._connection.cursor() as c: c.execute("SELECT instance_json FROM trading.strategy_instances WHERE strategy_instance_id=%s", (strategy_instance_id,)); row=c.fetchone()
        if row is None: return None
        return StrategyInstance.model_validate_json(row[0]) if isinstance(row[0], str) else StrategyInstance.model_validate(row[0])


class PostgresStrategyStateRepository:
    def __init__(self, connection: Any) -> None: self._connection = connection
    def append(self, snapshot: StrategyStateSnapshot) -> None:
        with self._connection.cursor() as c: c.execute("INSERT INTO trading.strategy_state_snapshots (snapshot_id,strategy_instance_id,captured_at,strategy_id,strategy_version,config_version,config_fingerprint,instrument_id,timeframe,state_schema_version,last_market_observation_id,state_json,snapshot_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (snapshot.snapshot_id,snapshot.strategy_instance_id,snapshot.captured_at,snapshot.strategy_id,snapshot.strategy_version,snapshot.config_version,snapshot.config_fingerprint,snapshot.instrument_id,snapshot.timeframe,snapshot.state_schema_version,snapshot.last_market_observation_id,snapshot.state_json,snapshot.model_dump_json()))
    def latest(self, strategy_instance_id: str):
        with self._connection.cursor() as c: c.execute("SELECT snapshot_json FROM trading.strategy_state_snapshots WHERE strategy_instance_id=%s ORDER BY captured_at DESC, snapshot_id DESC LIMIT 1", (strategy_instance_id,)); row=c.fetchone()
        if row is None: return None
        return StrategyStateSnapshot.model_validate_json(row[0]) if isinstance(row[0], str) else StrategyStateSnapshot.model_validate(row[0])
