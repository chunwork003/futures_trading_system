# GAP-08 W4R PostgreSQL Gate Review RF02A

Status:

`RF02_COMPATIBILITY_FIXTURE_FK_BLOCKED / REAUTH_REQUIRED`

Governance baseline:

`cf58d3be5a946581d6276cec4f5b8d869882f625`

## Retained positive evidence

- strategy PostgreSQL JSONB unit regression: `40 passed`;
- real PostgreSQL 17 concurrency: `2 passed, 2 skipped`;
- PostgreSQL compatibility reached the strategy-state append path.

## Compatibility blocker

The operational persistence fixture now supplies a canonical-shaped
`last_market_observation_revision_id = mor1_<64 hex>`,
but that synthetic identity has no durable row in
`trading.market_observation_revisions`.

Migration 0004 intentionally enforces the FK from
`strategy_state_snapshots.last_market_observation_revision_id`
to `market_observation_revisions.observation_revision_id`.

This is a stale/incomplete integration fixture. The FK must not be weakened.

## Required bounded correction

Retain the already-materialized RF02 production and unit-test candidate unchanged.

Only in `tests/integration/test_operational_persistence.py`:
create a real accepted MarketObservation revision through the existing canonical
domain/repository path, then use that durable revision identity in
`StrategyStateSnapshot`.

No direct SQL bypass.
No FK removal.
No migration change.
No production semantic change.

After correction:
1. rerun PostgreSQL compatibility;
2. run one full regression;
3. exact three-file source/test scope;
4. one commit/push;
5. STOP for Result Intake and independent W4 review.