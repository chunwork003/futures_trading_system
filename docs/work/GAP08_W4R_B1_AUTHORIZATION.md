# GAP-08 W4R-B1 Authorization

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_B1_ONLY`

Planning baseline:

`3e87fa28c93c0c0298f7dd065688c23d69cf9d80`

Dependencies:

- W4 architect replan decision
- W4R package freeze
- W4R-A closure

Execution plan:

`docs/work/GAP08_W4R_B_EXECUTION_PLAN.md`

## Goal

Implement only W4R-B1:

- durable C07 discovery receipt;
- durable positive C10 reconstruction receipt;
- active-recovery readiness fence participation;
- exact expected snapshot lookup;
- exact broker observation lookup;
- migration 0009 B1 schema extension.

Do not implement B2, C, D, or final C15 READY.

## Frozen existing semantics

### C07

Reuse existing:

- `BrokerDiscoveryRequest`
- `BrokerDiscoveryResult`
- `DiscoveryCompleteness`
- `BrokerDiscoveryIntegrity`
- exact client-correlation cardinality rules

Do not change C07 classification behavior.

### C10

Reuse existing:

- `BrokerReconstructionPlan`
- `BrokerDealSetCompleteness`
- exact broker deal identity rules
- existing reconstruction economics

Do not change C10 economics.

## B1 durable contracts

### BrokerDiscoveryReceipt

Must positively bind at least:

- discovery_run_id
- BrokerAccount
- recovery generation
- canonical `BrokerDiscoveryResult`
- producer_id
- contract_version
- recorded_at

The canonical result fingerprint must be derived deterministically from the result; caller strings/counts cannot substitute for exact material.

Identity:

`discovery_run_id`

Rules:

- same identity + exact same canonical material = idempotent;
- same identity + different material = conflict;
- append requires matching active recovery generation;
- new append advances `readiness_revision` exactly once;
- exact duplicate does not advance readiness again.

No "latest discovery" fallback.

### BrokerReconstructionReceipt

Positive receipt only. Absence means no positive reconstruction authority.

Must bind at least:

- reconstruction_receipt_id
- BrokerAccount
- recovery generation
- recovery_cut_fingerprint
- discovery_run_id
- order_id
- deterministic input coverage fingerprint
- exact accepted Fill IDs
- deterministic output/economic fingerprint
- `BrokerDealSetCompleteness.COMPLETE`
- optional authority_commit_id
- producer_id
- contract_version
- recorded_at

Rules:

- positive receipt requires COMPLETE DealSet;
- same identity + exact material = idempotent;
- same identity + different material = conflict;
- account/generation must match active recovery control;
- new append advances `readiness_revision` exactly once;
- exact duplicate does not advance again.

B1 does not infer COMPLETE from booleans or counts.

### Exact expected/actual reads

Add exact read methods to repository contracts and PostgreSQL adapters:

Expected snapshot:
- lookup by exact snapshot ID + broker + account_ref;
- no latest/as-of fallback.

Broker observation:
- lookup by exact observation ID + broker + account_ref;
- no latest fallback.

Wrong scope or missing identity returns no positive authority.

Canonical decode/integrity failure must fail closed.

## Required negative tests first

1. discovery same run ID / changed result material => conflict;
2. discovery exact duplicate => idempotent and readiness unchanged;
3. discovery wrong account/generation/inactive recovery => fail closed;
4. discovery result account differs from receipt account => fail closed;
5. reconstruction same receipt ID / changed accepted Fill IDs => conflict;
6. reconstruction same receipt ID / changed output fingerprint => conflict;
7. reconstruction `INCOMPLETE` DealSet cannot create positive receipt;
8. reconstruction wrong account/generation/inactive recovery => fail closed;
9. reconstruction exact duplicate => no second readiness advance;
10. expected snapshot exact ID with other account must not resolve;
11. broker observation exact ID with other account must not resolve;
12. invalid persisted snapshot/observation canonical JSON => integrity failure;
13. migration 0009 creates exact B1 tables without history backfill;
14. C07 and C10 existing semantics/tests remain unchanged.

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

Exactly these eight files.

No new files.

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
- all strategy/broker network code
- docs
- `data/`

If protected scope is required:

`STOP / REAUTHORIZATION`

## Test gates

Counterexamples first.

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c07_broker_discovery.py tests/unit/test_c10_broker_reconstruction.py tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-b1-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c12_recovery_cut.py tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-b1-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-b1-full
```

## Tooling policy

Known reparse-point patch issue:

use the known-working direct/controlled patch interface immediately.

Do not retry the known-failing route.

## Git

Exactly one runtime commit:

`feat(recovery): persist W4R-B1 trusted recovery evidence`

Before push:
- origin/master must still equal the B1 authorization baseline;
- no amend/rebase/force push.

Push once, then STOP reviewer.

## Side effects

ALLOW:
- exact eight-file source/test changes;
- extend migration 0009 source;
- local tests;
- one commit/push.

DENY:
- migration execution;
- actual PostgreSQL/V07;
- A08;
- broker/paper/Shioaji I/O;
- credentials;
- production;
- W4R-B2/C/D;
- P7;
- W4 closure/credit.

## Completion report

Report:

- initial HEAD
- final HEAD/origin
- commit
- exact changed files
- counterexample evidence
- targeted/compat/full results
- tooling retries
- semantic correction cycles
- 5HR consumption
- migration execution = NO
- actual PostgreSQL/V07 = NO
- A08 = NOT_RUN
- broker I/O = NO
- STOP
