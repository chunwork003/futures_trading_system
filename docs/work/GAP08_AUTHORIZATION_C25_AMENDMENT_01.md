# GAP-08 C25 Authorization Scope Amendment 01

## Status

AUTHORIZED_SCOPE_AMENDMENT。

Base authorization：

`docs/work/GAP08_AUTHORIZATION_C25.md`

Base Authorization Baseline：

`40de893fe19f24567891733c14cd0c5e4c28532b`

Authorized leaf remains：

C25 — Durable-before-Strategy Delivery / Revision Ref Migration。

Runtime Authorization remains：

BOUNDED_AUTHORIZED_C25_ONLY。

## Reason

Repository precheck found an existing recovery unit test outside the original C25 test scope：

`tests/unit/test_recovery_orchestration.py`

Historical behavior still uses：

`StrategyStateSnapshot(... last_market_observation_id="BAR-1")`

and：

`recover_runtime(... required_market_observation_id="BAR-1")`

to authorize READY。

That behavior conflicts with frozen C25 semantics：

- canonical recovery authority is `last_market_observation_revision_id`。
- canonical recovery input is `required_market_observation_revision_id`。
- exact C23 `MarketObservationRevisionId` / mor1 semantics are required。
- arbitrary legacy ID MUST NOT authorize READY。
- no legacy BAR ID may be fabricated into a mor1 ID。

## Additional Authorized Existing Test

Exactly one additional existing test is authorized：

`tests/unit/test_recovery_orchestration.py`

Purpose：

- migrate recovery orchestration tests to exact mor1 revision references。
- verify canonical exact match may proceed。
- verify canonical mismatch HALTs。
- verify arbitrary legacy ID cannot authorize READY。
- preserve existing account/reconciliation sequencing behavior。

## Runtime Scope

Existing C25 runtime scope is unchanged。

Authorized existing runtime：

- `trading/execution.py`
- `persistence/market_observation.py`
- `persistence/postgres/market_observation.py`
- `persistence/strategy_state.py`
- `persistence/postgres/strategy_state.py`
- `persistence/recovery.py`

Authorized NEW runtime：

- `persistence/market_observation_delivery.py`
- `persistence/postgres/migrations/0004_strategy_market_observation_revision_ref.sql`

Authorized existing tests：

- `tests/unit/test_strategy_state_recovery.py`
- `tests/unit/test_operational_execution.py`
- `tests/unit/test_recovery_orchestration.py`

Authorized NEW tests：

- `tests/unit/test_c25_market_observation_delivery.py`
- `tests/unit/test_c25_revision_reference_migration.py`

No other runtime/test file is authorized。

## Integration Boundary

`tests/integration/test_operational_persistence.py`

remains NOT_AUTHORIZED for modification。

Actual PostgreSQL / V07 remain NOT_AUTHORIZED。

The historical integration fixture using arbitrary observation IDs is therefore not rewritten under C25。

Migration creation：

AUTHORIZED_FOR_0004_ONLY。

Migration execution：

NOT_AUTHORIZED。

Historical migrations 0001 / 0002 / 0003：

IMMUTABLE。

## Other Boundaries

C02：

NOT_AUTHORIZED。

C05：

NOT_AUTHORIZED。

C18：

NOT_AUTHORIZED。

V05：

NOT_AUTHORIZED。

V07：

NOT_AUTHORIZED。

Broker I/O：

NOT_AUTHORIZED。

Market-data network I/O：

NOT_AUTHORIZED。

R14 completeness：

NOT_IMPLEMENTED。

K520：

NOT_IMPLEMENTED / GAP-09-owned。

## Effective Authorization Baseline

The commit containing this amendment becomes the effective C25 runtime execution baseline。

Base authorization + Amendment 01 together define the effective C25 execution envelope。

After successful C25 runtime execution：

commit / push / report / STOP。

A docs-only C25 closure remains required。
