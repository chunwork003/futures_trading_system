# GAP-08 W4R-A Independent Review — RF02 Required

Reviewed runtime candidate:

`ea1a371f3408ef881703907384e518471abedeb4`

RF01 authorization baseline:

`cee69ad0aa2eef586a721a148b0f13f03ef5718c`

Disposition:

`HOLD / W4R_A_RF02_REQUIRED`

Official correction-core acceptance remains:

`75 / 113`

W4 weight 18 remains:

`NOT_CREDITED`

## Mechanical result

PASS:

- exactly one RF01 runtime commit;
- master == runtime candidate;
- exactly five authorized files changed;
- migrations 0001-0008 unchanged;
- Result Intake V1 passed;
- migration 0009 not executed;
- no actual PostgreSQL/V07/A08/broker I/O claimed.

Executor evidence:

- targeted = 46 passed;
- compatibility = 36 passed;
- full regression = 1269 passed / 4 skipped;
- observed 5HR = 26%;
- semantic correction cycles = 1.

## RF01 blockers successfully closed

Closed:

1. exact historical transition receipt replay can bypass stale current CAS;
2. `ExecutionContinuityHead` now binds `transition_receipt_id`;
3. epoch/head/receipt account/generation/identity/revision coherence is checked;
4. transition receipt now carries explicit provenance fields;
5. fresh recovery rejects non-zero initial `readiness_revision`;
6. migration 0009 adds composite account/generation epoch scope constraints.

## Material blocker A — Exact replay still ignores immutable epoch material

Current exact replay returns after comparing only `receipt_json`.

A caller can replay the same exact receipt while supplying the same `epoch_id` with different immutable epoch material such as:

- `trusted_current`;
- `historical_degradation`;
- `anchored_at`;
- `evidence`.

Because the existing-receipt path returns before checking the durable epoch row, this conflicting material is silently accepted as an idempotent replay.

Required:

- exact replay must verify the durable referenced `ExecutionContinuityEpoch` equals the supplied epoch;
- same transition receipt + different epoch material => integrity conflict;
- historical replay after a newer head exists remains idempotent only when receipt + immutable epoch material are exact.

The historical mutable current head must not be overwritten.

## Material blocker B — Head/receipt DB revision linkage is incomplete

The current head FK binds:

- transition receipt ID;
- broker/account;
- generation;
- current epoch ID.

It does not bind the head's:

- `head_revision`;
- `readiness_revision`

to the same fields on the receipt.

Repository code sets them coherently, but the database contract still permits a row that references the correct receipt identity while carrying mismatched revisions.

Required:

- receipt exposes a unique referenced key including `head_revision` and `readiness_revision`;
- current head FK includes those revisions;
- DB therefore enforces that the current row is the exact projection established by that receipt.

## Material blocker C — Locally verifiable receipt provenance is not bound to locked control

`ContinuityTransitionReceipt.ingress_version` is currently caller-supplied but is not compared with the locked `AccountRecoveryControl.ingress_version`.

The receipt also does not carry the exact `recovery_cut_revision` owned by `AccountRecoveryControl`, so the transition cannot positively bind the local recovery control it observed.

Required W4R-A local provenance binding:

- add `recovery_cut_revision` to the receipt;
- lock/read control:
  - generation;
  - recovery_cut_revision;
  - ingress_version;
  - readiness_revision;
  - active;
- require receipt values equal the locked control values for:
  - generation;
  - recovery_cut_revision;
  - ingress_version;
  - previous readiness revision;
- mismatch => fail closed.

Boundary:

W4R-A does **not** re-resolve the full C12 RecoveryCut fingerprint, AccountStateHead, expected snapshot, or authority commit. Those are W4R-B/D trusted resolver responsibilities.

Therefore:

- W4R-A seals locally-owned continuity/currentness authority;
- receipt fields for full RecoveryCut/account/snapshot/commit remain durable provenance claims until B/D re-resolve them;
- no C15 READY authority is granted by W4R-A.

## Additional integrity requirement — Existing epoch exact reuse

If the referenced immutable epoch row already exists before a new transition receipt:

- exact same epoch material may be reused;
- same epoch ID + different material => conflict.

Do not require a new epoch insert merely because the current transition receipt is new.

## Reviewer state

W4R-A remains unaccepted.

W4R-B/C/D remain NOT_AUTHORIZED.

No architecture escalation is required.

RF02 is the final reviewer correction for W4R-A under the current package contract.

If another material defect remains after RF02:

`STOP / VIBE W4R-A PACKAGE REASSESSMENT`

Do not auto-open RF03.
