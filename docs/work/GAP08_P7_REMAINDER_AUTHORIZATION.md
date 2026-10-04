# GAP-08 P7 Remainder Authorization

## Formal Decision

```text
DECISION_ID = AUTH-P7-REMAINDER-01
DECISION = AUTHORIZE
ARCHITECTURE_SPEC = ARCH-P7-REMAINDER-01
ARCHITECTURE_SPEC_STATUS = FROZEN
PREAUTH_DIFF_REVIEW = PASS
ARCHITECTURE_CONTRADICTION = NONE
ARCHITECTURE_DECISION_AUTHORITY = NONE
```

Authorization baseline:
`6fdbad779749ac61f52ccde32fe3f3ffef591fd4`

Expected parent commit:
`docs(closure): accept GAP-08 P7 C16`

## Authorized Bounded Wave

```text
C17 -> C19 -> C20 -> C18
C17 = 4
C19 = 3
C20 = 3
C18 = 5
TOTAL = 15
```

Current accepted correction core remains `98 / 113` until final independent P7 remainder semantic review PASS.

## Effectivity Rule

Runtime/source modification is authorized only after this docs-only authorization commit is pushed to `master`. The exact pushed SHA becomes `P7_REMAINDER_EXECUTION_BASELINE`. Authorization docs and runtime source must not be mixed in one commit.

## Frozen Dependency / Sequence Model

Execution sequence: `C17 -> C19 -> C20 -> C18`.

```text
C17 <- C16
C19 <- C16
C20 <- C23
C18 <- accepted W4R-D rescope + C16 + C17 + C19 + C20 + C25
```

C18 original C15 dependency remains `SATISFIED_BY_ACCEPTED_W4R_D_RESCOPE`. C16, C15, W4, W4R and R05-R14 must not be reopened.

## Exact Runtime Writable Manifest

After authorization effectivity only:

- `strategy/recovery.py`
- `persistence/strategy_recovery.py`
- `persistence/postgres/strategy_recovery.py`
- `persistence/recovery.py`
- `persistence/postgres/migrations/0010_strategy_governing_transition_authority.sql`

No other runtime source is writable. Accepted C16 sources `strategy/instance.py` and `strategy/registry.py` are FROZEN / READ_ONLY.

## Exact Test Writable Manifest

- `tests/unit/test_c17_strategy_governing_transition.py`
- `tests/unit/test_c19_k520_applicability.py`
- `tests/unit/test_c20_completeness_required.py`
- `tests/unit/test_c18_strategy_recovery_readiness.py`
- `tests/unit/test_p7_remainder_integration.py`
- `tests/unit/test_recovery_orchestration.py`
- `tests/unit/test_strategy_state_recovery.py`
- `tests/unit/test_operational_postgres.py`

All other tests are read-only.

## C17 Frozen Semantics

Only `PRE_TRANSITION`, `TRANSITION_IN_PROGRESS`, `POST_TRANSITION` are valid conceptual recovery classifications. `TRANSITION_IN_PROGRESS` is never StrategyTradingReady or DecisionCohortTradingReady. Current deployment/latest config/latest implementation/restart process state/wall clock are not authority.

Only migration source `0010_strategy_governing_transition_authority.sql` may be created/extended for C17. Migrations `0001-0009` are read-only. Migration execution, historical backfill/rewrite, actual PostgreSQL, PG17, PG18 and V07 are denied/out-of-scope.

## C19 Frozen Semantics

Classification is `NOT_APPLICABLE_PROVEN`, `REQUIRED`, or `UNKNOWN`. `REQUIRED` is a valid result meaning approved K520/GAP-09 evidence is required before StrategyTradingReady. `UNKNOWN` fails closed. C19 does not implement GAP-09/K520 engine/feature-state persistence/full reconstruction.

## C20 Frozen Semantics

Completeness requirement authority is distinct from completeness evidence authority. Unknown requirement => NOT_READY. TEST/SANDBOX/PRODUCTION authority classes do not promote across environments. C20 does not implement GAP-DATA-001 full detector or production data-health service.

## C18 Frozen Semantics

`BrokerAccountExecutionReady != StrategyRestoreValid != StrategyTradingReady != DecisionCohortTradingReady`. Required cohort membership must come from exact authoritative governing DecisionPolicyVersion evidence, not loaded/restored strategy lists. P7 may consume DecisionPolicy authority seams but does not own DecisionPolicy business semantics. Missing authoritative production cohort authority may validly yield `DecisionCohortTradingReady = FALSE`.

Before StrategyTradingReady AND DecisionCohortTradingReady, startup catch-up must not emit normal broker-bound actions, normal material PENDING, broker side effects, or promote historical signals into current tradable decisions.

## Source Responsibility

`strategy/recovery.py` owns pure broker-neutral strategy recovery semantics. `persistence/strategy_recovery.py` owns ports/repository contracts. `persistence/postgres/strategy_recovery.py` owns PostgreSQL strategy-recovery adaptation and exact provenance validation. `persistence/recovery.py` is bounded orchestration only.

## One-Wave Execution Model

```text
C17 -> targeted gate -> commit/push -> INTERNAL_WAVE_FROZEN
C19 -> targeted gate -> commit/push -> INTERNAL_WAVE_FROZEN
C20 -> targeted gate -> commit/push -> INTERNAL_WAVE_FROZEN
C18 -> targeted gate -> commit/push -> INTERNAL_WAVE_FROZEN
P7 remainder integration gate
ONE final full repository regression
STOP
INDEPENDENT P7 REMAINDER SEMANTIC REVIEW
```

Internal freeze is not acceptance and credits no weight.

## Correction Budget

Each leaf: max 2 scope-internal correction cycles. Remainder integration: max 1. Final full regression: max 1 bounded correction cycle caused directly by authorized remainder-wave changes.

## Mandatory Stop Conditions

STOP if implementation requires architecture semantic change, a fourth C17 state, accepted C16 modification, C15/W4 reopen, migration beyond 0010, migration execution, historical backfill/rewrite, actual PostgreSQL, Broker/Shioaji I/O, GAP-09 implementation, GAP-DATA-001 implementation, DecisionPolicy business/domain implementation, runtime outside manifest, or test outside manifest.

## Explicit Deny

```text
P7_FULL_AUTHORIZATION = NOT_AUTHORIZED
CANONICAL_RUNTIME_AUTHORIZATION = NOT_AUTHORIZED
BROKER_IO = DENIED
SHIOAJI_IO = DENIED
PRODUCTION_ACTIVATION = NOT_AUTHORIZED
ACTUAL_POSTGRESQL = DENIED
MIGRATION_EXECUTION = DENIED
P8 = OUT_OF_SCOPE
P9/V07 = OUT_OF_SCOPE
```

Even after all remainder implementation/tests pass, C17/C19/C20/C18 remain not accepted and accepted correction core remains `98 / 113` until independent P7 remainder semantic review PASS. Even `113 / 113 ACCEPTED` does not automatically close GAP-08; final independent GAP-08 closure review remains required.
