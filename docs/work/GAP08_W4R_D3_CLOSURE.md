# GAP-08 W4R-D3 Closure

Final accepted runtime:

`38198142b5d57141c38582508a31d292e4bf246c`

Disposition:

`W4R-D3 ACCEPTED / FROZEN / READ_ONLY`

W4R-D parent:

`INTERNALLY COMPLETE`

Internal W4R package weight:

`18 / 18`

Official W4 weight:

`18 / NOT_CREDITED`

Official accepted correction core remains:

`75 / 113`

W4 is not closed by this document.

## Accepted D3 authority

D3 establishes the final trusted C15 and atomic handoff path.

### Pure trusted readiness projection

`evaluate_trusted_readiness(...)` accepts resolver-backed authority only.

It does not accept caller convenience booleans such as:

- ready;
- discovery_complete;
- continuity_current;
- pending_material_inbox;
- reconstruction_complete;
- mandatory_capabilities_available.

It binds exact durable discovery receipt, D2 trusted bundle, configured capability policy/mode, C13 blocker evidence, C14 formal run, generation-scoped broker-report disposition, BrokerAction unresolved state, and root/closure ambiguity.

Output is immutable `TrustedReadinessEvaluation` with `READY / REVIEW / HALT`.

### C14 / B2 final-world linkage

RF01 requires:

- `formal_run_boundary.discovery_run_id == trusted_core.discovery_receipt_id`;
- `formal_run_boundary.observation_id == trusted_core.broker_observation_id`;
- both boundary identities are non-null.

Missing or mismatched identity fails closed before READY.

### Atomic final transaction

Accepted order:

1. enter caller-owned PostgreSQL UoW;
2. lock exact active `AccountRecoveryControl ... FOR UPDATE`;
3. capture generation / recovery-cut / ingress / readiness fence;
4. re-run accepted D2 resolver on the same connection;
5. require D2 bundle fence == captured locked control;
6. re-read exact durable discovery receipt in the same transaction;
7. evaluate trusted readiness;
8. non-READY => explicit rollback / no handoff;
9. READY => lock/recheck active control again;
10. construct canonical inactive `AccountRecoveryControl`;
11. call existing C09 `finalize_handoff()` using exact generation / ingress / readiness;
12. commit exactly once.

No broker I/O occurs. No other durable mutation is added.

### Canonical final time

RF01 removed `model_copy(update=...)` from final completed-control construction.

The final control is reconstructed through `AccountRecoveryControl`, so naive/invalid time fails and aware non-UTC time normalizes to UTC before C09 handoff.

## Final verification

RF01 runtime:

`38198142b5d57141c38582508a31d292e4bf246c`

Commit:

`fix(recovery): seal W4R-D3 final authority guards`

Changed files:

- `persistence/recovery.py`
- `persistence/postgres/recovery.py`
- `tests/unit/test_c15_account_recovery_readiness.py`
- `tests/unit/test_operational_postgres.py`

Verification:

- counterexamples: `7 expected failures` before correction;
- targeted: `96 passed`;
- compatibility: `107 passed`;
- full regression: `1383 passed / 4 skipped`;
- `git diff --check`: PASS;
- exact scope: PASS;
- semantic correction cycles: `1`;
- tooling retries: `2`;
- user-observed 5HR: `13%`;
- migration execution: NO;
- PostgreSQL test-environment execution: NO;
- broker/paper/Shioaji I/O: NO.

Mechanical intake:

`MECHANICAL_INTAKE_PASS / SEMANTIC_REVIEW_REQUIRED`

Independent semantic review:

`PASS`

## Freeze

W4R-D3 is frozen/read-only.

W4R-D is internally complete.

This does NOT grant W4 closure, official W4 credit, P7, production activation, LIVE broker I/O, or V07 actual-environment conformance.

Before W4 closure, the separately authorized isolated PostgreSQL integration/concurrency gate is mandatory.
