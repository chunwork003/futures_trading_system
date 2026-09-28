# GAP-08 W4R-B1 Authorization Amendment 01

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_B1_RF01_ONLY`

Correction base:

`43acdd3e67470a8dda3ef9f3c8dd706d0a78a67c`

Parent authorization:

`docs/work/GAP08_W4R_B1_AUTHORIZATION.md`

Independent review:

`docs/work/GAP08_W4R_B1_REVIEW_RF01.md`

## Goal

Correct only the three B1 authority-integrity defects found by independent review:

1. exact-ID reads verify decoded canonical identity/account;
2. immutable receipt historical retry is idempotent before current-generation fencing;
3. reconstruction receipt derived fields come from canonical C10 material rather than arbitrary caller strings.

No W4R-B2/C/D implementation is authorized.

## Exact writable files

Production:

- `persistence/account.py`
- `persistence/postgres/account.py`
- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/postgres/migrations/0009_trusted_readiness_authority.sql`

Tests:

- `tests/unit/test_c07_broker_discovery.py`
- `tests/unit/test_c10_broker_reconstruction.py`
- `tests/unit/test_operational_postgres.py`

Exactly these eight files. No new files.

## RF01-1 Exact decoded identity integrity

Expected snapshot `get_exact` must verify decoded snapshot ID, broker, and account_ref against the requested exact key. Mismatch/corrupt material => `ExpectedSnapshotIntegrityError`.

Broker observation `get_exact` must verify decoded observation ID, broker, and account_ref against the requested exact key. Add/use a broker-observation-specific durable integrity error.

No latest/as-of fallback.

## RF01-2 Historical receipt replay before active-generation gate

For both discovery and reconstruction receipts:

- first query exact stable receipt identity before requiring active recovery;
- exact canonical material => `DUPLICATE`;
- different material => `BrokerReportConflictError`;
- historical duplicate does not inspect/mutate current recovery control and does not advance readiness;
- only when identity is absent may repository lock recovery control and require matching active generation;
- after locking, re-read identity to close concurrent duplicate race;
- exact concurrent receipt => `DUPLICATE`;
- conflict => fail closed;
- only genuinely new receipt inserts and advances readiness once.

## RF01-3 Canonical reconstruction material

`BrokerReconstructionReceipt` must carry canonical material sufficient to recompute its authority summary.

Bind at least:

- exact broker Deal evidence used by the COMPLETE DealSet;
- exact pre-existing local Fill identities used by the reconstruction input world;
- lifecycle evidence when present;
- canonical `BrokerReconstructionPlan`.

Canonicalization:

- broker Deal evidence ordered by exact broker Deal identity;
- local Fill IDs sorted unique;
- accepted Fill IDs derived from canonical plan accepted Fills and sorted unique;
- no wall-clock ordering is authority.

Derive deterministically:

- `input_coverage_fingerprint`;
- `accepted_fill_ids`;
- `output_fingerprint`.

If supplied derived values disagree with canonical derivation, validation fails.

`deal_set_completeness` remains `COMPLETE`.

Input fingerprint covers receipt-owned C10 material: broker Deal evidence, local Fill identity set, lifecycle evidence, deal-set completeness, and order/discovery binding relevant to the receipt.

Output fingerprint covers canonical `BrokerReconstructionPlan` material: status, accepted Fill material, filled quantity, average fill price, and material_change.

B2/D may later re-read durable Order/Fill/RecoveryCut currentness.

## RF01-4 Persistence remains canonical

Migration 0009 receipt JSON remains canonical durable material.

Generated/index columns may expose derived fields but must not become independently writable authority.

Do not replace W4R-A DDL. No backfill.

## Required counterexamples first

1. snapshot JSON identity mismatch;
2. snapshot JSON BrokerAccount mismatch;
3. observation JSON identity mismatch;
4. observation JSON BrokerAccount mismatch;
5. discovery exact replay after inactive recovery;
6. reconstruction exact replay after newer recovery generation;
7. historical same identity/different material conflict;
8. concurrent exact receipt retry advances readiness once;
9. arbitrary reconstruction input fingerprint rejected;
10. arbitrary accepted Fill IDs rejected;
11. arbitrary output fingerprint rejected;
12. canonical material tuple reordering yields same deterministic receipt;
13. incomplete DealSet positive receipt rejected;
14. 0009 preserves W4R-A DDL and has no backfill.

## Protected / read only

- `trading/broker_recovery.py`
- `persistence/recovery.py`
- `persistence/postgres/recovery.py`
- `persistence/reconciliation.py`
- `persistence/postgres/reconciliation.py`
- `persistence/account_authority.py`
- `persistence/postgres/account_authority.py`
- `persistence/broker_action.py`
- `persistence/postgres/broker_action.py`
- `adapters/capabilities.py`
- `adapters/sinopac/capabilities.py`
- migrations 0001-0008
- strategy/broker-network code
- docs
- `data/`

Need outside scope => `STOP / REAUTHORIZATION`.

## Test gates

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c07_broker_discovery.py tests/unit/test_c10_broker_reconstruction.py tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-b1-rf01-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c12_recovery_cut.py tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-b1-rf01-compat
```

Full regression once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-b1-rf01-full
```

## Tooling policy

Migration 0009 is `EXISTING_UNEXECUTED_EXTENSION`.

Retain prior DDL, patch only exact B1 RF01 section, use known-working direct/controlled patch interface immediately, and do not retry the known failing patch route.

## Git

Exactly one correction commit:

`fix(recovery): complete W4R-B1 trusted evidence authority`

Push once after origin ancestry guard, then STOP reviewer.

## Denied

- W4R-B2/C/D
- W4 closure/credit
- migration execution
- actual PostgreSQL/V07
- A08
- broker/paper/Shioaji I/O
- production
- credentials
- P7
- migrations 0001-0008
- files outside exact writable set
