# GAP-08 W4R-A Closure

Final runtime candidate:

`3e87fa28c93c0c0298f7dd065688c23d69cf9d80`

Disposition:

`W4R-A ACCEPTED / FROZEN / READ_ONLY`

Parent W4 remains:

`HOLD`

Official correction-core progress remains:

`75 / 113`

W4 weight:

`18 / NOT_CREDITED`

W4R-A internal package weight:

`5 / ACCEPTED_INTERNAL_ONLY`

No official correction-core credit is added until the final W4 reviewer accepts W4 as a whole.

## Accepted authority foundation

W4R-A establishes:

- `AccountRecoveryControl.readiness_revision` as recovery-currentness/CAS fence;
- `ingress_version` remains broker-ingress-only;
- BrokerAccount-scoped `ExecutionContinuityHead`;
- append-only `ContinuityTransitionReceipt`;
- current head binds exact transition receipt;
- exact scope/revision DB constraints;
- immutable epoch exact replay/reuse checks;
- locally verifiable recovery-control provenance binding;
- migration 0009 foundation without history inference/backfill;
- C09-owned readiness writers advance the readiness fence only under active recovery.

It does not make C15 READY and does not authorize production.

## Reviewer counterexamples closed

Closed:

1. stale historical trusted epoch cannot replace newer current epoch;
2. EPOCH-1 cannot match EPOCH-10 by substring;
3. current head CAS conflicts fail closed;
4. same transition identity / different material conflicts;
5. exact historical transition replay is idempotent;
6. historical replay does not overwrite a newer head;
7. exact receipt replay verifies immutable epoch material;
8. pre-existing exact epoch may be reused;
9. pre-existing same epoch ID / different material conflicts;
10. epoch/head/receipt account/generation/identity/revision coherence is enforced;
11. head binds exact transition receipt including head/readiness revisions at DB level;
12. receipt locally binds locked control generation/cut/ingress/readiness/active;
13. fresh recovery requires readiness revision zero;
14. no migration-time continuity-head inference;
15. SequenceGap remains append-only.

## Verification history

Initial W4R-A:
- 5HR consumption: 28%
- targeted: 36 passed
- compatibility: 36 passed
- full: 1259 passed / 4 skipped
- result: HOLD / RF01_REQUIRED

RF01:
- 5HR consumption: 26%
- targeted: 46 passed
- compatibility: 36 passed
- full: 1269 passed / 4 skipped
- result: HOLD / RF02_REQUIRED

RF02:
- 5HR consumption: 17%
- targeted: 48 passed
- compatibility: 36 passed
- full: 1271 passed / 4 skipped
- Result Intake V1: PASS
- result: ACCEPTED

Known warning:
- one existing `PytestCacheWarning`.

## Side-effect status

- migration 0009 source: CREATED / NOT_EXECUTED
- migrations 0001-0008: unchanged
- actual PostgreSQL/V07: NOT_RUN
- A08: NOT_RUN
- broker/paper/Shioaji I/O: NO
- production activation: NOT_AUTHORIZED
- P7: DO NOT START

## Workflow learning

Repository-native automation successfully completed:

`machine preflight -> dispatch packet -> CODEX -> result intake -> semantic review`

Observed executor consumption improved:

`28% -> 26% -> 17%`

The known reparse-point patch retry class is now treated as tooling and should use the known-working direct/controlled patch route immediately.

W4R-A is frozen. Any later semantic modification requires explicit reauthorization.
