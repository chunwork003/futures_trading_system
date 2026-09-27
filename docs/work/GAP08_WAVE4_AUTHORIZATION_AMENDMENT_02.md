# GAP-08 Wave-4 — Reviewer Correction Authorization RF02

## Current Decision

runtime_candidate = `efd74325c4a4d31c63e8e4790689c00388eadaf3`
reviewer = `HOLD / RF02_REQUIRED`

C13 = `PASS / FROZEN / READ_ONLY`
C14 = `PASS / FROZEN / READ_ONLY`
C12 = `RF02_REQUIRED`
C15 = `RF02_REQUIRED`

W4_weight = `18 / NOT_CREDITED`
accepted_correction_core = `75 / 113`
canonical_runtime_authorization = `NOT_AUTHORIZED`

RF01 execution evidence reported：

- C12 targeted：111 passed
- C15 targeted：117 passed
- W4 targeted：218 passed
- final full regression：1250 passed / 4 skipped
- one Windows pytest temp-path tooling retry
- A08 PostgreSQL crash/concurrency：NOT_RUN

This amendment is reviewer delta only。
Original W4 package、original authorization and Amendment 01 remain frozen authority。

## RF02-A — Exact Fill/Event Witness

Current Order witness includes exact Order material but Fill/Event validation is still reduced to counts。

Required：

- Fill witness includes deterministic exact immutable identity + material fields required for current Order economics/state validation。
- Event witness includes deterministic exact identity / sequence / provenance / material fields required for lifecycle validation。
- same-count but materially different Fill/Event worlds change the RecoveryCut witness。
- unrelated-account Fill/Event material does not affect this account witness。
- final revalidation reads the same exact witness。
- no global Order scan。
- no second economic authority。

Required negative cases：

1. same Fill count but different identity / quantity / price / material => witness changes。
2. same Event count but different identity / sequence / provenance / material => witness changes。
3. unrelated-account Fill/Event => no effect。

## RF02-B — READY Positive Evidence Must Be Bound

Mandatory READY predicates may not be authorized by free booleans or arbitrary nonblank strings alone。

Required：

- positive predicates derive from typed evidence and/or exact immutable provenance refs。
- evidence binds BrokerAccount + current RecoveryCut fingerprint and applicable run/discovery identity。
- C07 discovery evidence validates exact account/run identity、completeness/current scope and integrity。
- C09 continuity evidence validates exact account/generation/current trust；bare boolean is insufficient。
- pending/unapplied broker report state derives from exact current report witness/disposition。
- C10 reconstruction completeness/conflict requires exact provenance tied to the evaluated world。
- empty-result completeness requires structured positive evidence tied to the formal run/evaluated scope。
- mandatory capability evidence has positive provenance if used as READY predicate。
- cross-field mismatch => HALT or REVIEW according to frozen semantics；never READY。

Required negative cases：

1. all convenience booleans positive but typed/provenance evidence absent => cannot READY。
2. discovery evidence wrong account/run/incomplete/ambiguous => cannot READY。
3. continuity evidence wrong account/generation or degraded/currentness mismatch => cannot READY。
4. arbitrary completeness string with empty results => cannot READY。
5. reconstruction boolean without matching provenance => cannot READY。
6. evidence bundle from another cut => cannot READY。

## RF02-C — Non-Revision Currentness Coverage

Currentness witness/revalidation must include readiness-affecting account-scoped evidence where applicable：

- current ExecutionContinuityEpoch identity/state。
- relevant SequenceGap / continuity degradation witness。
- readiness-relevant reconciliation case/run identity/version that can change without AccountStateHead revision。
- current report application disposition。
- current non-terminal execution witness。
- unresolved BrokerAction head。

Do not make every historical/open case an automatic blocker。
Use existing blocking/policy semantics。

Any relevant witness change after evaluation => stale evaluation / reevaluate。

Formal ReconciliationRun may remain outside the RecoveryCut fingerprint if including it creates circularity，but final readiness must bind/revalidate its applicability to the same cut。

## RF02-D — Narrow Structured Restore Failure

Current loader catches ValidationError / TypeError / ValueError / IndexError across the whole workflow。

Required：

- corrupted persisted authority evidence / Pydantic validation failure => structured RESTORE_FAILURE。
- DB operational errors propagate。
- programming errors propagate。
- exception handling is narrow around evidence decode/validation/construction boundaries。

Required negative cases：

1. malformed persisted checkpoint/receipt => RESTORE_FAILURE。
2. injected/helper TypeError => propagates。
3. DB operational exception => propagates。
4. no broad catch around the full snapshot workflow。

## Exact RF02 Writable Scope

Runtime：

- `persistence/recovery.py`
- `persistence/postgres/recovery.py`

Tests：

- `tests/unit/test_c12_recovery_cut.py`
- `tests/unit/test_c15_account_recovery_readiness.py`
- `tests/unit/test_recovery_orchestration.py`
- `tests/unit/test_operational_postgres.py`

No new files。

Everything else READ_ONLY，especially：

- C13/C14 files。
- migration 0008。
- migrations 0001～0007。
- W1/W2/W3 modules。
- `persistence/postgres/uow.py`。
- execution/broker-recovery source modules。
- strategy/market-observation modules。
- governance docs after this amendment。
- `data/`。

If exact typed evidence cannot be completed in this six-file scope：

`STOP / REAUTHORIZATION`

## Test Gate

1. RF02 negative cases first。
2. C12 targeted from Amendment 01。
3. C15 targeted from Amendment 01。
4. final W4 targeted suite from execution package。
5. exactly one final full offline regression。
6. `git diff --check`。
7. exact RF02 scope/protected/migration guards。

A08 isolated PostgreSQL crash/concurrency remains：

`NOT_RUN / NOT_CLAIMED`

Known Windows pytest temp issue：

use a task-local writable `--basetemp` from the first full-regression invocation。

## Semantic Budget

RF02 is one combined final semantic correction cycle for C12/C15。

If independent review finds another material C12/C15 semantic defect after RF02：

`STOP / ARCHITECT DECISION`

Do not open RF03 automatically。

## Side Effects

DENY：

- migration source modification/execution。
- actual PostgreSQL / V07。
- broker/paper/Shioaji I/O。
- credential access。
- V01～V05。
- production activation。
- R-13。
- C16～C20。
- P7。
- governance modification during runtime correction。

## Git

Preserve all existing W4/RF01 commits。

RF02 creates exactly one additional correction commit after all gates pass。

Suggested message：

`fix(recovery): bind W4 readiness evidence authority`

Before push：

origin/master must equal the RF02 authorization commit created from this document。

After push：

STOP for independent reviewer。

Do not close W4 or credit weight 18。