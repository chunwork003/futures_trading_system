# GAP-08 W4R-A Independent Review — RF01 Required

Reviewed runtime candidate:

`6628d5e1bb7fe12eae8323de11be5f3db46fcb97`

Authorization baseline:

`8e381f72d2130e27dbe8f46030df3c378d0bb273`

Disposition:

`HOLD / W4R_A_RF01_REQUIRED`

Official correction-core acceptance remains:

`75 / 113`

W4 weight 18 remains:

`NOT_CREDITED`

## Mechanical result

PASS:

- exactly one runtime commit;
- master == runtime candidate;
- exactly five authorized files changed;
- migrations 0001-0008 unchanged;
- migration 0009 source added but not executed;
- no broker / actual PostgreSQL / V07 / A08 side effects claimed;
- executor stopped at reviewer barrier.

Executor evidence:

- targeted 36 passed;
- compatibility 36 passed;
- full regression 1259 passed / 4 skipped;
- semantic correction cycles 1;
- tooling retries 3;
- observed 5HR consumption 28%.

## Material blocker A — PostgreSQL exact retry is not idempotent

The in-memory test repository checks an existing `transition_id` before CAS and returns for identical replay.

The PostgreSQL repository checks active control readiness/head CAS before checking the durable transition receipt.

After the first successful transition the readiness/head revisions have advanced, therefore an exact retry using the original expected revisions fails before the existing identical receipt can be recognized.

Required:

- same `transition_id` + exact same canonical transition material => idempotent no-op/return;
- same `transition_id` + different material => integrity conflict;
- historical retry must not mutate current head or imply that the historical transition is still current.

## Material blocker B — Cross-object transition invariants are incomplete

The repository does not positively prove all three supplied objects describe the same transition.

Required before write:

- epoch/head/receipt BrokerAccount identical;
- epoch/head/receipt generation identical;
- head.current_epoch_id == epoch.epoch_id == receipt.current_epoch_id;
- receipt.previous_epoch_id == actual current head epoch;
- head.head_revision == receipt.head_revision == expected_head_revision + 1;
- head.readiness_revision == receipt.readiness_revision == expected_readiness_revision + 1;
- receipt previous revisions equal expected revisions.

Any mismatch => fail closed.

Database constraints must also prevent a head/receipt for one BrokerAccount/generation from referencing an epoch of another scope.

## Material blocker C — Current head does not bind transition receipt

AD-01 requires the current continuity head to point to the transition/re-anchor provenance that established it.

Current `ExecutionContinuityHead` / table has no `transition_receipt_id`.

Required:

- add `transition_receipt_id`;
- exact head row binds the receipt that established the current epoch/revision;
- DB FK / scope constraints preserve identity.

## Material blocker D — Transition receipt provenance is incomplete

AD-01 / W4 Replan V2 require durable provenance beyond free-form evidence strings.

Add explicit material fields for at least:

- recovery_cut_fingerprint;
- anchor_fingerprint;
- ingress_version / ingress frontier;
- account_revision;
- expected_snapshot_id;
- authority_commit_id;
- gap_set_fingerprint;
- producer_id;
- contract_version;
- evidence_id.

These are material receipt identity/provenance and must participate in exact duplicate comparison.

Do not infer these fields from timestamps or strings.

## Additional bounded correction

`begin_recovery` must establish a fresh recovery generation with `readiness_revision = 0`; caller-provided non-zero initial readiness revision must fail closed.

## Tooling finding

The executor hit the same workspace/reparse-point apply-patch class three times.

This is TOOLING, not semantic correction.

For RF01:

- detect the known environment once during preflight;
- select the previously working direct/controlled patch interface immediately;
- do not retry the known-failing patch route three times.

## Reviewer state

W4R-A is not accepted.

No W4R-B/C/D.

No W4 credit.

No architecture escalation required.

All required changes remain inside W4R-A's original five-file boundary.
