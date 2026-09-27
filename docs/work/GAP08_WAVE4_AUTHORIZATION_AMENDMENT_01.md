# GAP-08 Wave-4 — Reviewer Correction Authorization RF01

## Current Decision

runtime_candidate = `060dfdc2ac4539fa31b95c26c0a0bd0b3dcb7021`
reviewer = `HOLD / RF01_REQUIRED`
C13 = `PASS / FROZEN / READ_ONLY`
C12 = `RF01_REQUIRED`
C14 = `PASS / FROZEN / READ_ONLY`
C15 = `RF01_REQUIRED`
W4_weight = `18 / NOT_CREDITED`
accepted_correction_core = `75 / 113`
canonical_runtime_authorization = `NOT_AUTHORIZED`

Original authority:
- `docs/work/GAP08_WAVE4_EXECUTION_PACKAGE.md`
- `docs/work/GAP08_WAVE4_AUTHORIZATION.md`

This file is RF01 delta only. Original frozen contracts remain authoritative.

## C12 RF01 Delta

VALID RecoveryCut must prove the applicable BrokerAccount-local current execution closure, including:

- exact account-relevant current non-terminal canonical Order set;
- deterministic canonical Fill/event validation anchors where applicable;
- BrokerAccount-scoped durable authority selecting those Orders;
- AccountRecoveryControl active + generation + ingress frontier;
- broker-report current disposition/frontier evidence that equal aggregate counts cannot hide;
- unresolved BrokerAction head witness;
- deterministic non-revision witness/fingerprint changed by any required current-world change.

Missing/unverifiable closure => `RESTORE_FAILURE`.

Projection-only trust, global Order scan and heuristic account attribution are forbidden.

## C15 RF01 Delta

READY must bind formal ReconciliationRun to the exact current RecoveryCut:

- boundary/outcome run_id match;
- exact BrokerAccount match;
- exact account_revision match;
- exact expected_snapshot_id match;
- exact authority_commit_id match;
- exact recovery generation/frontier match;
- exact recovery-cut fingerprint/witness match;
- required discovery/observation references remain the evidence used by readiness.

Historical MATCH from another/stale cut must never READY.
Caller booleans alone must not constitute mandatory positive READY evidence.
Final local revalidation must cover the complete C12 non-revision witness.
Mismatch => stale evaluation / reevaluate.

## Exact Writable Scope

Runtime:
- `persistence/recovery.py`
- `persistence/postgres/recovery.py`

Tests:
- `tests/unit/test_c12_recovery_cut.py`
- `tests/unit/test_c15_account_recovery_readiness.py`
- `tests/unit/test_recovery_orchestration.py`
- `tests/unit/test_operational_postgres.py`

No new files. Everything else READ_ONLY, including C13/C14 files and migration 0008.

## Test / Correction Gate

C12 targeted:
`.\.venv\Scripts\python.exe -m pytest tests/unit/test_c12_recovery_cut.py tests/unit/test_recovery_orchestration.py tests/unit/test_c04_account_authority_commit.py tests/unit/test_c06_broker_action_safety.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c10_broker_reconstruction.py tests/unit/test_operational_postgres.py -q`

C15 targeted:
`.\.venv\Scripts\python.exe -m pytest tests/unit/test_c15_account_recovery_readiness.py tests/unit/test_recovery_orchestration.py tests/unit/test_c07_broker_discovery.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c10_broker_reconstruction.py tests/unit/test_c12_recovery_cut.py tests/unit/test_c14_reconciliation_run.py tests/unit/test_operational_postgres.py -q`

Then:
1. final W4 targeted suite from execution package;
2. one mandatory final full regression;
3. `git diff --check`;
4. exact RF01 scope/protected/migration/side-effect guards.

No intermediate full regression is required between C12 and C15 RF01.

Semantic budget:
- C12 RF01 max 2 scope-internal semantic corrections;
- C15 RF01 max 2;
- third => STOP / REAUTHORIZATION.

## Side Effects / Git

DENY migration source modification/execution, actual PostgreSQL/V07, broker/paper/Shioaji I/O, V01-V05, credentials, production activation, R-13, C16-C20, P7.

Preserve existing four W4 commits. RF01 creates one new correction commit only:
`fix(recovery): complete W4 recovery authority closure`

Before push, origin/master must equal the RF01 authorization commit.
After correction push: STOP for reviewer.

## Execution Context

Next CODEX handoff is a transient Task Context Packet:

`TRANSIENT / DERIVED / NON-AUTHORITATIVE / REVISION-BOUND`

It must bind:
- RF01 authorization commit;
- working HEAD;
- authority pointers;
- six-file write scope;
- tests / side-effect envelope / STOP rules.

Pointer > duplicated prose.
The packet is not committed to the repository.