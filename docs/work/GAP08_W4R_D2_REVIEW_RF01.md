# GAP-08 W4R-D2 Independent Review RF01

Reviewed runtime:

`26c1d7028c1c3451e46da3fe1f346d966feb42b5`

Disposition:

`W4R-D2 HOLD / RF01_REQUIRED`

The runtime candidate is otherwise retained.

## Accepted candidate material

The candidate correctly establishes most D2 structure:

- immutable `TrustedReadinessEvidenceBundle`;
- canonical derived bundle fingerprint;
- caller-supplied fingerprint cannot override derivation;
- account authority closure validation;
- B2 trusted core binding;
- C13 resolver reuse;
- exact C14 boundary/outcome reads;
- C2 root/closure reuse;
- continuity head-selected epoch/transition reads;
- BrokerAction account scoping;
- no READY/finalize/handoff/activate surface;
- no commit/rollback;
- no migration / broker I/O;
- exact runtime scope;
- targeted / compatibility / full regression all pass.

Two authority seams remain before D2 can be accepted.

## RF01-1 — D2 resolver must be composable inside D3 caller-owned writable UoW

Current candidate:

`PostgresTrustedReadinessEvidenceResolver.resolve(...)`

calls:

`PostgresExecutionStateLoader(...).load(account)`

The loader executes:

`SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY`

That behavior is valid for the standalone C12 loader, but it is not valid as a hidden side effect of the D2 resolver because frozen D3 requires:

1. caller starts writable PostgreSQL UoW;
2. caller locks active `AccountRecoveryControl` (`FOR UPDATE`);
3. caller re-runs the accepted D2 resolver under that lock;
4. caller may finalize handoff in the same transaction.

After a transaction has already performed the control lock, the D2 resolver must not attempt to reset transaction characteristics. It also must not convert the final D3 UoW to READ ONLY.

### Required correction

Factor the existing execution-state read body into a pure current-transaction helper in:

`persistence/postgres/recovery.py`

Semantics:

- helper performs only the existing durable reads/validation;
- helper does not issue `SET TRANSACTION`;
- helper does not commit/rollback;
- `PostgresExecutionStateLoader.load()` keeps its existing public standalone behavior:
  - first establishes `REPEATABLE READ READ ONLY`;
  - then delegates to the pure helper;
- `PostgresTrustedReadinessEvidenceResolver.resolve()` delegates directly to the pure helper and therefore does not alter caller transaction characteristics.

Do not change C12 recovery-cut semantics.

Do not add D3 locking/handoff in RF01.

## RF01-2 — durable gap set must bind the continuity transition receipt

Current candidate derives:

`gap_semantic_fingerprint`

from the exact durable `SequenceGap` set.

But the bundle does not require that derived value equal:

`continuity_transition.gap_set_fingerprint`

Therefore a transition receipt can claim one gap world while the current durable gap set describes another world, and the typed bundle still constructs.

This violates the same-world continuity/gap binding required by D2.

### Required correction

Use one deterministic canonical gap semantic fingerprint algorithm for the bundle.

After canonicalizing/sorting the exact gap set:

- derive current gap semantic fingerprint;
- require exact equality with `continuity_transition.gap_set_fingerprint`;
- mismatch => `TrustedRecoveryEvidenceError`;
- caller-provided `gap_semantic_fingerprint` remains non-authoritative and is overwritten by canonical derivation.

This intentionally makes a newly appended readiness-relevant gap invalidate a transition whose receipt has not been re-anchored/re-bound to that gap world.

## No other D2 changes authorized

Do not:

- add READY evaluation;
- add D3 control locking;
- add handoff/finalize;
- change C13/C14/B/C accepted semantics;
- modify migrations;
- expand production ownership;
- change broker behavior.

## Efficiency record

Initial D2 semantic execution:

- user-observed 5HR: `11%`
- changed files: `3`
- diff: approximately `+164 / -5`
- targeted: `72 passed`
- compatibility: `105 passed`
- full regression: `1357 passed / 4 skipped`
- semantic correction cycles: `0`
- tooling route switches/retries: `1`
- runtime commit: `26c1d7028c1c3451e46da3fe1f346d966feb42b5`

The controlled route set worked as intended and must remain available for RF01.
