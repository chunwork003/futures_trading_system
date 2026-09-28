# GAP-08 W4R-A Authorization Amendment 02

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_A_RF02_ONLY`

Correction base:

`ea1a371f3408ef881703907384e518471abedeb4`

Parent authorization:

`docs/work/GAP08_W4R_A_AUTHORIZATION_AMENDMENT_01.md`

Review:

`docs/work/GAP08_W4R_A_REVIEW_RF02.md`

## Goal

Seal the remaining W4R-A continuity integrity boundary only.

This is the final reviewer correction under the current W4R-A package contract.

No W4R-B/C/D implementation is authorized.

## Exact writable files

- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/postgres/migrations/0009_trusted_readiness_authority.sql`
- `tests/unit/test_c09_broker_recovery_fence.py`
- `tests/unit/test_operational_postgres.py`

No other production/test/migration files.

## Required corrections

### RF02-1 Exact replay verifies immutable epoch material

For an existing identical transition receipt:

- load the durable referenced epoch;
- compare full canonical `ExecutionContinuityEpoch` material;
- exact epoch => idempotent historical replay;
- same epoch ID / different material => `ContinuityAuthorityConflictError`;
- do not overwrite a newer current head;
- do not advance readiness twice.

### RF02-2 Exact existing epoch reuse for a new transition

When the epoch insert conflicts because the epoch ID already exists:

- load the durable epoch;
- exact same epoch material => reuse and continue;
- different material => integrity conflict.

This must not weaken transition receipt/head CAS.

### RF02-3 Head/receipt revision FK

Migration 0009 must make the current head reference the exact receipt projection including:

- transition receipt ID;
- broker;
- account_ref;
- generation;
- current_epoch_id;
- head_revision;
- readiness_revision.

Repository values must remain coherent with that DB contract.

### RF02-4 Bind locally-owned recovery-control provenance

Add explicit `recovery_cut_revision` to `ContinuityTransitionReceipt`.

Under the account recovery control `FOR UPDATE` lock, require exact equality:

- control.generation == receipt/head/epoch generation;
- control.recovery_cut_revision == receipt.recovery_cut_revision;
- control.ingress_version == receipt.ingress_version;
- control.readiness_revision == receipt.previous_readiness_revision == expected_readiness_revision;
- control.active is TRUE.

Mismatch => fail closed.

Do not repurpose `ingress_version`.

### RF02-5 Deterministic head projection

Before persistence require:

- `head.recorded_at == receipt.recorded_at`;
- head identity/revisions remain exactly derived from the receipt.

This allows historical replay validation without requiring the mutable current-head row still equal the historical head.

## Required counterexamples first

1. exact receipt + conflicting epoch `trusted_current` => conflict;
2. exact receipt + conflicting epoch evidence => conflict;
3. exact historical receipt + exact epoch after newer head => idempotent/no overwrite/no revision advance;
4. pre-existing exact epoch + new valid receipt/head => transition succeeds;
5. pre-existing same epoch ID + conflicting epoch material => conflict;
6. receipt ingress_version != locked control ingress_version => conflict;
7. receipt recovery_cut_revision != locked control recovery_cut_revision => conflict;
8. head recorded_at != receipt recorded_at => coherence conflict;
9. migration head->receipt FK includes head/readiness revisions;
10. no 0001-0008 migration changes/backfill.

## Trust boundary

Do not expand into W4R-B/D.

Specifically do not re-resolve in RF02:

- full C12 RecoveryCut fingerprint;
- AccountStateHead;
- expected snapshot;
- authority commit;
- capability registry;
- C07/C10;
- C13/C14;
- C15 READY.

Those remain later trusted resolver/final gate work.

## Test gate

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-a-rf02-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c12_recovery_cut.py tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-a-rf02-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-a-rf02-full
```

Post gates:

- `git diff --check`;
- exact five-file scope;
- migrations 0001-0008 unchanged;
- migration 0009 source only / not executed;
- actual PostgreSQL/V07 = NO;
- A08 = NOT_RUN;
- broker/paper/Shioaji I/O = NO;
- final tree only known `data/` / `.tmp`.

## Tooling

Known reparse-point patch failure is already classified.

Use the known-working direct/controlled patch interface immediately.

Do not spend retries on the known-failing path.

## Git

Exactly one correction commit:

`fix(recovery): seal W4R-A continuity integrity`

Push once after origin ancestry guard.

Then STOP reviewer.

## Correction boundary

If any material defect remains after RF02:

`STOP / VIBE W4R-A PACKAGE REASSESSMENT`

Do not auto-open RF03.

## Denied

- W4R-B/C/D
- W4 closure/credit
- migration execution
- actual PostgreSQL/V07
- A08
- broker/paper/Shioaji I/O
- credentials
- production
- P7
- migrations 0001-0008
- any file outside exact writable set
