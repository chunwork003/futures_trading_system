# GAP-08 P7 Remainder Authorization Amendment 01

## Decision

```text
DECISION_ID = AUTH-P7-REMAINDER-01-AMENDMENT-01
DECISION = AUTHORIZE
RF01_CORRECTION = BOUNDED_AUTHORIZED_AFTER_DOCS_MATERIALIZATION
ARCH-P7-REMAINDER-01 = FROZEN
RUNTIME_BASELINE = 3c36e87efe94ab6fedcc0389c9eb37ac4d5df1f5
ARCHITECTURE_CONTRADICTION = NO
ARCHITECT_DECISION_REQUIRED = NO
NEW_ADR_REQUIRED = NO
ACCEPTED_CORRECTION_CORE = 98 / 113
P7_REMAINDER_WEIGHT = NOT_CREDITED
```

## RF01-01 Frozen Contract

Selected pattern:

```text
PATTERN A
IMMUTABLE TRANSITION DESCRIPTOR
+
APPEND-ONLY PHASE / BOUNDARY EVIDENCE
```

One stable `transition_id` is preserved across PRE_TRANSITION -> TRANSITION_IN_PROGRESS -> POST_TRANSITION.
The immutable descriptor contains stable transition definition only.
BEGIN_EFFECTIVE and COMPLETION are append-only durable evidence under the same transition identity.
Identical retry is idempotent; conflicting descriptor/BEGIN/COMPLETION fails closed.
COMPLETION requires BEGIN and exact target-compatible durable state.
No wall-clock/latest-row authority and no historical rewrite.

## Transition Resolution

Use immutable `StrategyGoverningTransitionResolutionReceipt` with:

```text
ACTIVE_TRANSITION
NO_ACTIVE_TRANSITION
```

`NO_ACTIVE_TRANSITION` is not a fourth C17 state.

Positive no-active-transition authority:

```text
STRATEGY-GOVERNING-TRANSITION-RESOLUTION / V1
```

Only the immutable receipt selected by the exact current CAS resolution head is current.
Missing/unavailable/stale/mismatched resolver/head/receipt is not positive proof of no transition and yields StrategyTradingReady = FALSE.

## Migration 0010

Migration source may be corrected for Pattern A because 0010 has not been executed.
It must support immutable descriptor, append-only BEGIN, append-only COMPLETION,
append-only resolution receipt, and CAS current-resolution head.

```text
0010 EXECUTION = DENIED
ACTUAL POSTGRESQL = DENIED
HISTORICAL BACKFILL = DENIED
HISTORICAL AUTHORITY REWRITE = DENIED
0001-0009 = READ_ONLY
```

## RF01-02 Frozen Contract

C19 trusted output becomes an evaluated receipt equivalent to `K520ApplicabilityReceipt`,
retaining classification plus exact effective `StrategyGoverningContext`,
feature-dependency authority, horizons, observation frontiers/currentness,
causal frontier, and proof authority.

C20 trusted output becomes an evaluated receipt equivalent to `CompletenessReadinessReceipt`,
retaining readiness, requirement classification, exact governing context,
consumer/scope/stream/horizon, policy/version, authority class,
evaluated/current world, evaluated/current frontier, currentness,
requirement authority and evidence authority.

C18 trusted readiness consumes exact transition resolution + exact C19 receipt + exact C20 receipt.
It resolves effective governing context first and requires restore/C19/C20/K520 evidence to exact-bind to it.
Any mismatch fails closed.
TEST/SANDBOX readiness cannot promote into PRODUCTION.

## RF01-03 Frozen Contract

Production cohort readiness uses:

```text
AUTHORITATIVE PROVIDER / RESOLVER LOOKUP
```

The trusted boundary calls `DecisionCohortAuthorityProvider`/resolver itself.
Caller-created membership is not production authority by itself.
Resolved membership must exact-bind cohort identity, DecisionPolicy identity/version,
policy authority/version, authority class, required StrategyInstance membership,
membership authority/version and evaluated/current currentness.

Caller cannot shrink authoritative SI-1 + SI-2 to SI-1.
Missing/unavailable/stale/wrong provider result yields DecisionCohortTradingReady = FALSE.

## Exact Runtime Writable Manifest

```text
strategy/recovery.py
persistence/strategy_recovery.py
persistence/postgres/strategy_recovery.py
persistence/recovery.py
persistence/postgres/migrations/0010_strategy_governing_transition_authority.sql
```

`strategy/instance.py`, `strategy/registry.py`, and all other runtime sources remain read-only.

## Exact Test Writable Manifest

```text
tests/unit/test_c17_strategy_governing_transition.py
tests/unit/test_c19_k520_applicability.py
tests/unit/test_c20_completeness_required.py
tests/unit/test_c18_strategy_recovery_readiness.py
tests/unit/test_p7_remainder_integration.py
tests/unit/test_recovery_orchestration.py
tests/unit/test_strategy_state_recovery.py
tests/unit/test_operational_postgres.py
```

## Mandatory Counterexamples

At minimum prove all 16 frozen reviewer/architecture counterexamples:
same-transition progression and conflicts; C1/C2 C19 world mismatch;
TEST/SANDBOX-to-PRODUCTION C20 rejection; wrong C20 consumer/scope/world;
missing/stale transition resolution; authoritative cohort shrink prevention;
stale policy/membership/currentness; and provider unavailable.

## Verification / Effectivity

Run relevant C17/C19/C20/C18 targeted tests, P7 remainder integration,
then ONE final full repository regression.

Initial implementation attempt + maximum 2 scope-internal correction cycles.

Runtime correction becomes effective only after this docs-only amendment commit is pushed.
The exact pushed SHA becomes `P7_RF01_EXECUTION_BASELINE`.

```text
BROKER_IO = DENIED
SHIOAJI_IO = DENIED
MIGRATION_EXECUTION = DENIED
ACTUAL_POSTGRESQL = DENIED
PRODUCTION_ACTIVATION = NOT_AUTHORIZED
LIVE = NOT_AUTHORIZED
P8 = OUT_OF_SCOPE
P9/V07 = OUT_OF_SCOPE
NEXT_MAINLINE_GAP = NOT_AUTHORIZED
```

After RF01 correction: STOP and return to `INDEPENDENT P7 REMAINDER SEMANTIC RE-REVIEW`.
No self-credit; accepted correction core remains 98/113 until independent PASS.
