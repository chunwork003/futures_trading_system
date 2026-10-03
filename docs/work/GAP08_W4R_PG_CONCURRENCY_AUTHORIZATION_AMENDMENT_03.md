# GAP-08 W4R PostgreSQL Gate Authorization Amendment 03

Status:

`BOUNDED_AUTHORIZED_FOR_W4R_PG_RF02_JSONB_AND_FK_FIXTURE_ONLY`

Prior governance baseline:

`cf58d3be5a946581d6276cec4f5b8d869882f625`

## Writable source/test files

- `persistence/postgres/strategy_state.py`
- `tests/integration/test_operational_persistence.py`
- `tests/unit/test_operational_postgres.py`

Exactly these three files remain the RF02 source/test commit scope.

## Retained production correction

Keep the already-materialized deterministic JSON serialization for:
- `StrategyInstance.config_json`
- `StrategyStateSnapshot.state_json`

## Additional fixture authorization

Only `tests/integration/test_operational_persistence.py` may be extended to create
a durable accepted MarketObservation revision using the existing canonical APIs
and `PostgresMarketObservationAcceptanceRepository.process_candidate()`.

The returned accepted revision identity must be used as
`last_market_observation_revision_id`.

No raw SQL shortcut.
No migration change.
No FK weakening.
No additional production file.
No RF03.
No W4 closure by executor.
No P7.

## Retained evidence

- RF02 JSONB unit: `40 passed`
- PG17 concurrency: `2 passed, 2 skipped`

Remaining gates:
- PostgreSQL compatibility
- exactly one full regression
- one source/test commit/push
- STOP