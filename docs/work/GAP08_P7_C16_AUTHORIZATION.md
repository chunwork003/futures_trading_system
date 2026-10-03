# GAP-08 P7 C16 Authorization

Decision ID:

`AUTH-P7-C16-01`

Decision:

`AUTHORIZE`

Authorization baseline:

`5682033fde26dff8a317dce11da227dc7b1b59e8`

Authorized leaf:

`C16 ONLY`

Leaf:

`Strategy Governing Identity + Canonical Binding`

C16 weight:

`5`

C16 source modification authorization:

`BOUNDED_AUTHORIZED_FOR_GAP08_P7_C16_ONLY`

## Authority boundary

```text
FULL_P7_RUNTIME_AUTHORIZATION = NOT_AUTHORIZED
CANONICAL_RUNTIME_AUTHORIZATION = NOT_AUTHORIZED

C17 = NOT_AUTHORIZED
C19 = NOT_AUTHORIZED
C20 = NOT_AUTHORIZED
C18 = NOT_AUTHORIZED

BROKER_IO = NOT_AUTHORIZED
PRODUCTION_ACTIVATION = NOT_AUTHORIZED

MIGRATION_SOURCE_MODIFICATION = DENY
MIGRATION_EXECUTION = DENY

ACTUAL_POSTGRESQL_ACCESS = DENY
V07 = OUT_OF_SCOPE
PG17_INTEGRATION = OUT_OF_SCOPE
PG18_INTEGRATION = OUT_OF_SCOPE
```

This authorization creates no architecture semantics. Frozen architecture is input.

## Frozen C16 contract

```text
strategy_instance_id
!= instrument_id
!= executable ContractSpec identity
!= config version
!= implementation revision
!= DecisionPolicyVersion

strategy_instance_id = opaque StrategyInstance lifecycle identity
instrument_id = canonical StrategyInstance instrument binding

instrument_id != automatically executable ContractSpec authority
symbol / alias != canonical binding authority
symbol / alias != broker execution authority
```

C16 must positively establish:

1. StrategyInstance lifecycle identity.
2. Exact immutable config version.
3. Exact canonical config content.
4. Exact config fingerprint integrity.
5. Exact StrategyDefinition identity.
6. Exact implementation revision.
7. Canonical instrument binding.
8. Immutable/auditable instrument-binding provenance.
9. Applicable state-schema reference where available.

State-schema ownership in C16 is resolve/reference only. Compatibility migration
eligibility and transition acceptance remain later-leaf responsibilities.

## Canonical binding provenance

Durable broker-neutral provenance must prove:

```text
which canonical instrument_id was bound
which approved reference/provisioning authority established that binding
which authority/version context was used
historical binding is restored from durable provenance
rather than re-resolved from today's alias table
```

Symbol, config hash, current alias resolver and current deployment are not binding authority.

Missing/conflicting required governing provenance fails closed.

## Contract selection guard

C16 does not own:

- alias registry architecture;
- continuous-contract resolution;
- rollover selection;
- listed-contract selection;
- broker contract-selection policy.

If executable ContractSpec authority is required but absent:

`FAIL CLOSED / NOT EXECUTION ELIGIBLE`

C16 must not manufacture a contract authority.

## Implementation revision / config rules

Current deployment revision is not governing revision.

Implementation mismatch without explicit authorized compatibility/transition authority
fails closed. C17 owns compatible transition semantics and is not authorized here.

```text
config_version != strategy_instance_id
config_fingerprint != strategy_instance_id
```

Config fingerprint is exact immutable config-content integrity evidence only.

Same committed config version with changed config content fails closed.

## Authorized runtime source scope

Existing runtime source:

- `strategy/instance.py`
- `strategy/registry.py`
- `persistence/strategy_state.py`
- `persistence/postgres/strategy_state.py`
- `persistence/recovery.py`

Optional new pure broker-neutral source:

- `strategy/governing.py`

The optional source may be created only when it materially reduces responsibility mixing.

## Authorized test scope

New dedicated test:

- `tests/unit/test_c16_strategy_governing_identity.py`

Compatibility/integration updates:

- `tests/unit/test_strategy_state_recovery.py`
- `tests/unit/test_strategy_registry.py`
- `tests/unit/test_recovery_orchestration.py`
- `tests/unit/test_operational_postgres.py`

All other tests are read-only. If an additional test file is required:

`STOP / SCOPE_REAUTHORIZATION_REQUIRED`

## Explicit read-only scope

- `domain/instruments.py`
- `domain/contracts.py`
- `domain/broker_instruments.py`
- `strategy/state.py`
- `persistence/postgres/recovery.py`
- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `trading/**`
- `adapters/**`
- `backtest/**`
- `docs/adr/**`
- `persistence/postgres/migrations/**`

No broker mapping or contract-selection implementation may be modified.

## Migration / environment boundary

```text
MIGRATION_SOURCE_MODIFICATION = DENY
MIGRATION_EXECUTION = DENY
ACTUAL_POSTGRESQL_ACCESS = DENY
POSTGRES17_TEST_DSN = DO_NOT_USE
POSTGRES18_TEST_DSN = DO_NOT_USE
PRODUCTION_DSN = DO_NOT_USE
```

C16 should use existing durable `strategy_instances.instance_json`,
`strategy_state_snapshots.snapshot_json` and existing structured identity columns.

If a schema migration is necessary:

`STOP / MIGRATION_REAUTHORIZATION_REQUIRED / RETURN_TO_ARCHITECT`

## Broker boundary

```text
BROKER_IO = DENY
SHIOAJI_IO = DENY
PAPER_BROKER_VERIFICATION = DENY
V01-V05 = OUT_OF_SCOPE
```

## Mandatory counterexamples

The C16 candidate must cover at least:

- same config fingerprint + different strategy_instance_id does not merge lifecycle identity;
- same config_version + changed config_json => fail closed;
- config_json != config_fingerprint => fail closed;
- governing implementation revision != current registered implementation revision,
  without transition authority => fail closed;
- StrategyInstance instrument_id != StrategyStateSnapshot instrument_id => fail closed;
- required durable binding provenance missing => fail closed;
- binding provenance conflicts with canonical instrument_id => fail closed;
- alias/display-symbol drift does not remap historical canonical instrument binding;
- symbol-only changes do not create canonical binding or broker execution authority;
- missing executable ContractSpec authority is never manufactured by C16.

## PostgreSQL repository contract

Fake/unit PostgreSQL tests must establish:

- append persists exact immutable StrategyInstance authority JSON;
- get reconstructs exact governing identity/provenance;
- structured columns vs canonical payload conflict => fail closed;
- no silent JSON/column fallback precedence.

## Recovery integration boundary

`persistence/recovery.py` may only add C16 pure identity/binding validation:

- resolve exact StrategyInstance governing identity;
- validate exact config/implementation/binding provenance;
- fail closed before strategy restore.

It must not add C17 transition orchestration, C18 readiness composition, C19 K520
logic, C20 completeness authority, or new BrokerAccount readiness semantics.

## Test gates

1. `tests/unit/test_c16_strategy_governing_identity.py`
2. `tests/unit/test_strategy_registry.py`
3. `tests/unit/test_strategy_state_recovery.py`
4. `tests/unit/test_recovery_orchestration.py`
5. C16-related cases in `tests/unit/test_operational_postgres.py`
6. one final full regression

Full regression must not access actual PostgreSQL or broker systems.

## Correction budget

Maximum two scope-internal implementation correction cycles.

Architecture ambiguity is not a correction-cycle issue. Any architecture contradiction,
migration need, broker I/O need, actual PostgreSQL need, or runtime source need outside
the authorized scope requires immediate STOP and reauthorization.

## Commit / acceptance

This authorization becomes effective only after the docs-only authorization commit is
pushed. That exact commit becomes `C16_EXECUTION_BASELINE`.

After C16 implementation and all gates PASS, one runtime commit is allowed:

`feat(recovery): implement C16 strategy governing identity`

Executor completion means:

```text
C16_IMPLEMENTATION = COMPLETE_CANDIDATE
C16_TESTS = PASS
C16_REVIEW = REQUIRED
C16_ACCEPTED = NO
```

Accepted correction core remains `93 / 113` until independent semantic review passes.

After the runtime candidate commit/push/report:

`STOP / INDEPENDENT_C16_SEMANTIC_REVIEW`
