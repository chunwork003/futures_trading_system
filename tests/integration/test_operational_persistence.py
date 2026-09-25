import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from persistence.account import AccountPositionSnapshot
from persistence.postgres.account import PostgresExpectedPositionSnapshotRepository
from persistence.postgres.driver import connect_postgres
from persistence.postgres.execution import PostgresFillRepository, PostgresOrderRepository
from persistence.postgres.migrations import discover_migrations, run_migrations
from persistence.postgres.strategy_state import PostgresStrategyInstanceRepository, PostgresStrategyStateRepository
from persistence.strategy_state import StrategyStateSnapshot
from strategy.instance import StrategyInstance, config_fingerprint
from trading.account import AccountPosition, PositionDirection
from trading.execution import Fill, Order, OrderStatus, OrderType, PositionEffect


@pytest.mark.parametrize(("major", "variable"), [(17, "POSTGRES17_TEST_DSN"), (18, "POSTGRES18_TEST_DSN")])
def test_operational_repositories_and_rollback_smoke(major: int, variable: str) -> None:
    dsn=os.environ.get(variable)
    if not dsn: pytest.skip(f"{variable} is not configured; compatibility remains PENDING")
    connection=connect_postgres(dsn); now=datetime.now(timezone.utc)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW server_version_num"); assert int(cursor.fetchone()[0])//10000 == major
        run_migrations(connection,discover_migrations(Path("persistence/postgres/migrations")))
        order=Order(order_id=f"PG{major}-O",intent_id="I",correlation_id="C",instrument_id=1,contract_id=None,direction=PositionDirection.LONG,position_effect=PositionEffect.OPEN,order_type=OrderType.MARKET,quantity=1,status=OrderStatus.PENDING,created_at=now,updated_at=now)
        PostgresOrderRepository(connection).save(order,expected_version=-1)
        fill=Fill(fill_id=f"PG{major}-F",order_id=order.order_id,event_id="E",correlation_id="C",causation_id="E",quantity=1,price=Decimal("1"),occurred_at=now)
        assert PostgresFillRepository(connection).append(fill)
        position=AccountPosition(broker="SINOPAC",account_ref="A",instrument_id=1,contract_id=None,direction=PositionDirection.LONG,quantity=1)
        snapshot=AccountPositionSnapshot(snapshot_id=f"PG{major}-S",broker="SINOPAC",account_ref="A",effective_at=now,recorded_at=now,source_event_id="E",positions=(position,))
        PostgresExpectedPositionSnapshotRepository(connection).append(snapshot)
        config={"symbol":"TX","timeframe":"1m"}; fingerprint=config_fingerprint(config)
        instance=StrategyInstance(strategy_instance_id=f"PG{major}-SI",strategy_id="EMA_CROSS",strategy_version="1.0.0",config_version="C1",config_fingerprint=fingerprint,instrument_id=1,timeframe="1m",config_json=config)
        PostgresStrategyInstanceRepository(connection).append(instance)
        state=StrategyStateSnapshot(snapshot_id=f"PG{major}-SS",strategy_instance_id=instance.strategy_instance_id,strategy_id=instance.strategy_id,strategy_version=instance.strategy_version,config_version=instance.config_version,config_fingerprint=fingerprint,instrument_id=1,timeframe="1m",state_schema_version=1,last_market_observation_id="BAR",captured_at=now,state_json={"schema_version":1,"previous_ema20":None,"previous_ema60":None})
        PostgresStrategyStateRepository(connection).append(state)
        assert PostgresStrategyStateRepository(connection).latest(instance.strategy_instance_id) == state
    finally:
        connection.rollback(); connection.close()
