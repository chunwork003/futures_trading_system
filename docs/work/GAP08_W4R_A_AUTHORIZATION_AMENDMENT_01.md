# GAP-08 W4R-A Authorization Amendment 01

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_A_RF01_ONLY`

Correction base:

`6628d5e1bb7fe12eae8323de11be5f3db46fcb97`

Parent authorization:

`docs/work/GAP08_W4R_A_AUTHORIZATION.md`

Review:

`docs/work/GAP08_W4R_A_REVIEW_RF01.md`

## Goal

Correct only the independent-review defects in W4R-A continuity authority.

No W4R-B/C/D implementation is authorized.

## Exact writable files

- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/postgres/migrations/0009_trusted_readiness_authority.sql`
- `tests/unit/test_c09_broker_recovery_fence.py`
- `tests/unit/test_operational_postgres.py`

No other production/test/migration files.

## Required corrections

### RF01-1 Exact transition replay

PostgreSQL behavior must match the frozen idempotency contract:

- exact same transition identity + exact same material => idempotent;
- same identity + different material => conflict;
- retry must not re-advance head/readiness;
- retry after head later advances remains a historical idempotent replay and must not overwrite current head.

### RF01-2 Cross-object coherence

Fail closed unless:

- epoch/head/receipt account scope identical;
- generation identical;
- exact current epoch identity identical;
- previous epoch equals durable current head;
- head/receipt revisions exactly match expected+1;
- readiness revisions exactly match expected+1.

### RF01-3 Head binds receipt

Add `transition_receipt_id` to domain head and migration 0009 head table.

The current head must durably reference the exact receipt that established it.

### RF01-4 Full transition provenance

Add explicit material receipt fields:

- `recovery_cut_fingerprint`
- `anchor_fingerprint`
- `ingress_version`
- `account_revision`
- `expected_snapshot_id`
- `authority_commit_id`
- `gap_set_fingerprint`
- `producer_id`
- `contract_version`
- `evidence_id`

Normalize stable IDs; revisions/frontiers are non-negative/positive as appropriate.

Duplicate equality must include these fields.

### RF01-5 DB scope integrity

Migration 0009 must enforce that continuity head/receipt epoch references match the same:

- broker
- account_ref
- generation

Do not modify migration 0007.

A composite UNIQUE/FOREIGN KEY added by migration 0009 is allowed.

### RF01-6 Fresh recovery fence

`begin_recovery` must reject a fresh recovery control whose `readiness_revision != 0`.

Do not repurpose `ingress_version`.

## Required counterexamples first

1. exact successful transition retry is idempotent and does not advance revisions twice;
2. exact old transition retry after a newer head exists does not overwrite the newer head;
3. same transition ID with changed provenance conflicts;
4. head current_epoch != epoch ID fails;
5. receipt current_epoch != epoch ID fails;
6. cross-account or cross-generation epoch/head/receipt fails;
7. head/receipt revision mismatch fails;
8. head transition_receipt_id mismatch fails;
9. non-zero readiness revision at begin_recovery fails;
10. migration 0009 has composite scope constraints and no history backfill.

## Tests

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-a-rf01-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c12_recovery_cut.py tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-a-rf01-compat
```

Full regression once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-a-rf01-full
```

## Tooling policy

Known reparse-point patch behavior has already been observed.

At preflight select the known-working direct/controlled patch interface.

Do not repeatedly retry the known-failing patch method.

## Git

Exactly one correction commit:

`fix(recovery): complete W4R-A continuity authority`

Push once after remote ancestry guard.

Then STOP reviewer.

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
- protected files outside exact writable set
