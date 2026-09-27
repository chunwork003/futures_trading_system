# GAP-08 Wave-4 / P6 — Execution Package + Coherence

## 1. Identity

Wave：

`GAP08-W4-LOCAL-RECOVERY-RECONCILIATION`

Package：

`P6 — Local Recovery / Reconciliation`

Parent / W3 Closure Baseline：

`4a340eb966ed9930a506a5c1d1a10941f3a18c06`

Leaf order：

`C13 -> C12 -> C14 -> C15`

Candidate weight：

18 / NOT CREDITED。

Accepted correction-core before W4：

75 / 113。

Remaining before W4：

38。

If W4 is later reviewer-accepted：

93 / 113 complete / verified；20 remaining。

Execution coherence：

`VERIFIED`

Runtime Source Modification Authorization：

`NOT_AUTHORIZED`

Canonical Runtime Authorization：

`NOT_AUTHORIZED`

Production Activation：

`NOT_AUTHORIZED`

This package is planning/coherence only。

---

## 2. Efficiency Contract

This package uses the repository workflow optimization already accepted in W3：

- delta-first。
- reference-first。
- PASS/frozen-surface guard。
- changed-symbol / high-risk-function review。
- evidence-only reports。
- feedback -> concrete process/template/check improvement。

Do not copy the full frozen architecture into future CODEX prompts。

Future source handoff should reference this package + exact authorization and include leaf delta only。

---

## 3. Why The Order Is Coherent

### C13 first

Current `ReconciliationCase` / `ReconciliationCaseRepository.unresolved()` has no primary BrokerAccount scope and current recovery orchestration can gate on unresolved cases globally。

C13 must remove that cross-account authority ambiguity before RecoveryCut consumes reconciliation evidence。

### C12 second

Current `ExecutionStateLoader.load()` returns no explicit immutable restore result and current recovery flow is assembled from independent reads。

C12 must establish one BrokerAccount-local coherent RecoveryCut / explicit restore result before formal reconciliation can claim an exact evaluated world。

### C14 third

A formal ReconciliationRun must bind the exact evaluated RecoveryCut/evidence and produce crash-consistent audit evidence。

It therefore depends on C12 + C13。

### C15 fourth

BrokerAccount READY / REVIEW / HALT is the final account-level recovery gate and consumes C07/C09/C10 + C12 + C14 evidence。

It must not use `position MATCH + restored strategy` as a shortcut。

---

## 4. Frozen Architecture References

Use pointers, not copied prose：

- ADR-002 R-05A～R-05F：ExecutionStateLoader / coherent RecoveryCut。
- ADR-002 R-12A～R-12H：ReconciliationRun audit。
- ADR-002 R-04H：BrokerAccount READY / REVIEW / HALT。
- Correction Freeze C12 / C13 / C14 / C15 acceptance boundaries。
- W3 closure for C07/C09/C10 accepted evidence。

No architecture redesign is authorized。

---

## 5. Proposed Runtime Write Scope

Existing runtime files：

- `trading/reconciliation.py`
- `persistence/reconciliation.py`
- `persistence/postgres/reconciliation.py`
- `persistence/recovery.py`

New runtime file：

- `persistence/postgres/recovery.py`

New migration source：

- `persistence/postgres/migrations/0008_local_recovery_reconciliation.sql`

Existing writable tests：

- `tests/unit/test_reconciliation.py`
- `tests/unit/test_recovery_orchestration.py`
- `tests/unit/test_operational_account.py`
- `tests/unit/test_operational_postgres.py`

New tests：

- `tests/unit/test_c13_reconciliation_case_scope.py`
- `tests/unit/test_c12_recovery_cut.py`
- `tests/unit/test_c14_reconciliation_run.py`
- `tests/unit/test_c15_account_recovery_readiness.py`

This is the proposed source scope only。

It becomes writable only after a separate explicit W4 source-modification authorization。

---

## 6. Protected / READ-ONLY Runtime

Unless a later authorization explicitly amends scope：

- `persistence/postgres/uow.py`
- `persistence/account.py`
- `persistence/postgres/account.py`
- `persistence/account_authority.py`
- `persistence/postgres/account_authority.py`
- `persistence/broker_action.py`
- `persistence/postgres/broker_action.py`
- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `trading/broker_recovery.py`
- `trading/execution.py`
- `persistence/execution.py`
- `persistence/postgres/execution.py`
- strategy state / market observation modules
- all Shioaji / Sinopac adapters
- capability registry
- migrations `0001`～`0007`
- `data/`

W1/W2/W3 accepted authority paths are consumed，not rewritten。

If C12 cannot prove a coherent PostgreSQL cut without changing `persistence/postgres/uow.py`：

STOP / REAUTHORIZATION。

Do not silently widen scope。

---

## 7. C13 — ReconciliationCase BrokerAccount Scope

Weight：

3。

Primary owners：

- `trading/reconciliation.py`
- `persistence/reconciliation.py`
- `persistence/postgres/reconciliation.py`
- migration 0008

Required semantics：

1. every ReconciliationCase has exactly one primary BrokerAccount scope。
2. scope is explicit even when result side is absent / UNKNOWN_EXTERNAL_STATE。
3. all versions of one case_id remain in the same BrokerAccount scope。
4. changing case scope across versions fails closed。
5. repository unresolved query is exact-account scoped。
6. unresolved cases from Account A must not block Account B。
7. append-only version history remains intact。
8. case state is discrepancy/control evidence，not economic authority。
9. case `open` / unresolved alone is not final readiness authority。
10. legacy unscoped persisted history may not be silently ignored or guessed。

Migration rule：

- 0002 remains immutable。
- 0008 may add account-scope support to existing reconciliation history。
- any legacy scope derivation must be deterministic from immutable persisted evidence。
- ambiguous legacy scope must fail closed；no guessed backfill。

C13 does not establish ReconciliationRun or READY。

---

## 8. C12 — Coherent RecoveryCut + ExecutionStateLoader

Weight：

5。

Primary owners：

- `persistence/recovery.py`
- new `persistence/postgres/recovery.py`

Required semantics：

1. ExecutionStateLoader = Read + Validate + Explicit immutable Result。
2. outcomes distinguish at least VALID / BASELINE_NOT_ESTABLISHED / RESTORE_FAILURE categories required by R-05D。
3. `BASELINE_NOT_ESTABLISHED` requires positive lifecycle authority proof；row absence alone is insufficient。
4. one VALID result contains exactly one BrokerAccount-local coherent RecoveryCut。
5. AccountStateHead revision is the economic frontier but is not the entire RecoveryCut identity。
6. RecoveryCut covers currentness evidence for dependencies that can change without account revision，at minimum W3 inbox/application frontier + recovery control generation/frontier where applicable。
7. required closure includes exact checkpoint / expected snapshot / authority receipt and applicable current non-terminal execution / unresolved broker-action dependencies。
8. no independent `latest` reads may be presented as one coherent cut。
9. PostgreSQL implementation uses one caller-owned transaction / verified snapshot consistency boundary。
10. if transaction isolation/currentness cannot be proven，do not return VALID。
11. new PostgreSQL recovery adapter may establish the required read-only repeatable snapshot as its first operation；existing PostgresUnitOfWork remains READ-ONLY。
12. projection-only trust is forbidden；required canonical anchors must resolve。
13. partial diagnostics may exist but cannot be exposed as VALID。
14. loader performs no broker I/O。
15. loader performs no repair / re-anchor。
16. loader performs no economic mutation / AccountStateHead advancement。
17. VALID may hydrate RecoveryExecutionContext only。
18. VALID != BrokerAccount READY。
19. VALID != Strategy READY。
20. RecoveryCut currentness after load is C15/R-04H responsibility。

No second high-water authority may be invented。

---

## 9. C14 — ReconciliationRun Audit

Weight：

5。

Primary owners：

- `persistence/reconciliation.py`
- `persistence/postgres/reconciliation.py`
- migration 0008

Required semantics：

1. one run_id belongs to exactly one BrokerAccount。
2. stable opaque run identity for one formal evaluation attempt。
3. durable RUN_BOUNDARY_ESTABLISHED exists before result-bearing formal evaluation。
4. crash after run boundary leaves detectable non-finalized attempt。
5. exact declared scope + policy identity + recovery/session context are durable。
6. evaluated input world binds exact immutable/versioned references。
7. exact RecoveryCut/currentness witness is bound。
8. exact expected-state/account authority refs are bound。
9. broker/discovery/observation qualification refs are exact where applicable。
10. technical outcome、input qualification、domain result are separate axes。
11. incomplete/unqualified evidence cannot become MATCH。
12. UNKNOWN_EXTERNAL_STATE requires qualified evidence，not generic failure。
13. run lifecycle != case lifecycle。
14. MATCH may create zero case。
15. case resolution never rewrites historical run。
16. one run has at most one authoritative terminal audit outcome。
17. identical terminal retry may deduplicate。
18. conflicting terminal finalization fails closed。
19. terminal outcome + required result/provenance evidence finalize crash-consistently。
20. finalized run must never expose partial required result evidence。
21. ReconciliationRun does not advance AccountStateHead。
22. historical finalized MATCH is not current READY authority。
23. no `SELECT latest MATCH -> READY` path。

0008 may add formal reconciliation-run audit tables/indexes/constraints。

Migration execution remains DENY。

---

## 10. C15 — BrokerAccount READY / REVIEW / HALT Aggregator

Weight：

5。

Primary owner：

- `persistence/recovery.py`
- new `persistence/postgres/recovery.py` only where final currentness reads/handoff support are needed

Required semantics：

1. precedence = HALT > REVIEW > READY。
2. READY requires positive proof for every mandatory predicate。
3. UNKNOWN / DEGRADED / NO_ERROR_OBSERVED never imply READY。
4. coherent C12 RecoveryCut VALID is required but not sufficient。
5. required C14 formal run/audit evidence must be eligible for activation use。
6. C07 discovery completeness / exact-correlation integrity must satisfy required scope。
7. C09 continuity/current evidence must be READY/current and no unapplied material inbox evidence may remain。
8. C10 canonical reconstruction / Fill economics must be complete and conflict-free where applicable。
9. unresolved BrokerActionAttempt requiring disposition prevents READY。
10. out-of-horizon unresolved action requiring authorized external evidence maps REVIEW，not READY。
11. integrity conflict / ambiguous exact match / invalid expected authority / mandatory unavailable capability maps HALT。
12. a reconciled active non-terminal broker order alone does not prevent READY。
13. position MATCH alone never grants READY。
14. restored strategy alone never grants BrokerAccount READY。
15. strategy readiness remains later C16/C17/C18 scope。
16. final handoff revalidates exact AccountStateHead revision + RecoveryCut non-revision currentness witness + recovery generation/frontier。
17. changed cut/currentness returns stale evaluation / reevaluate；never silently activates。
18. readiness does not advance economic AccountStateHead。
19. readiness cannot bypass C06 no-blind-retry or R-13 production authorization。
20. no broker network I/O inside final local currentness/handoff transaction。

The existing legacy `recover_runtime()` compatibility path must not retain a bypass where `position MATCH + strategy restored` independently creates BrokerAccount READY。

Do not implement C16～C20 strategy authority in C15。

---

## 11. Migration 0008 Boundary

Candidate：

`0008_local_recovery_reconciliation.sql`

Source creation/amendment may be authorized later。

Execution：

`DENY`

Actual PostgreSQL / V07：

`DENY`

0001～0007：

READ-ONLY。

No 0009。

0008 expected scope：

- ReconciliationCase account-scope persistence support。
- formal ReconciliationRun audit persistence。
- indexes / constraints required for exact account/run identity and append-only audit semantics。

RecoveryCut itself need not become a second persistence authority/table merely to satisfy C12。

---

## 12. Planned Leaf Gates

C13 targeted：

`.\.venv\Scripts\python.exe -m pytest tests/unit/test_c13_reconciliation_case_scope.py tests/unit/test_reconciliation.py tests/unit/test_operational_account.py tests/unit/test_operational_postgres.py -q`

C12 targeted：

`.\.venv\Scripts\python.exe -m pytest tests/unit/test_c12_recovery_cut.py tests/unit/test_recovery_orchestration.py tests/unit/test_c04_account_authority_commit.py tests/unit/test_c06_broker_action_safety.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_operational_postgres.py -q`

C14 targeted：

`.\.venv\Scripts\python.exe -m pytest tests/unit/test_c14_reconciliation_run.py tests/unit/test_reconciliation.py tests/unit/test_c12_recovery_cut.py tests/unit/test_operational_postgres.py -q`

C15 targeted：

`.\.venv\Scripts\python.exe -m pytest tests/unit/test_c15_account_recovery_readiness.py tests/unit/test_recovery_orchestration.py tests/unit/test_c07_broker_discovery.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c10_broker_reconstruction.py tests/unit/test_c12_recovery_cut.py tests/unit/test_c14_reconciliation_run.py tests/unit/test_operational_postgres.py -q`

Wave final targeted：

`.\.venv\Scripts\python.exe -m pytest tests/unit/test_c13_reconciliation_case_scope.py tests/unit/test_c12_recovery_cut.py tests/unit/test_c14_reconciliation_run.py tests/unit/test_c15_account_recovery_readiness.py tests/unit/test_reconciliation.py tests/unit/test_recovery_orchestration.py tests/unit/test_operational_account.py tests/unit/test_operational_postgres.py tests/unit/test_c04_account_authority_commit.py tests/unit/test_c06_broker_action_safety.py tests/unit/test_c07_broker_discovery.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c10_broker_reconstruction.py -q`

Every authorized leaf later requires：

- targeted PASS。
- full regression PASS。
- `git diff --check` PASS。
- exact cumulative scope PASS。
- semantic correction budget within authorization。
- local commit according to future authorization。
- no intermediate push unless future authorization allows it。

---

## 13. Side-Effect Envelope

Planning / coherence stage：

source modification DENY。

Future W4 runtime execution must continue to DENY unless separately authorized：

- migration execution。
- actual PostgreSQL / V07。
- broker network / paper / Shioaji simulation / production I/O。
- credential access。
- V01～V05 broker capability verification。
- production activation。
- R-13 manual authority implementation。
- C16～C20。
- P7 / next Wave。

Tests use fake/mock/in-memory persistence evidence only。

---

## 14. Coherence Findings

Verified：

- dependencies C13 -> C12 -> C14 -> C15 match frozen DAG。
- current global unresolved-case read is a concrete C13 correction target。
- current ExecutionStateLoader is materially below frozen R-05 contract and has one clear owner。
- existing W1 account authority + W2 broker-action + W3 broker-recovery evidence provide the read-only inputs C12/C15 need。
- one new PostgreSQL recovery adapter can own coherent local cut/currentness reads without rewriting accepted W1/W2/W3 adapters。
- 0008 is the next migration number。
- formal ReconciliationRun has no current runtime implementation and has one coherent persistence owner family。
- existing pure position reconciliation can be preserved rather than rewritten。
- strategy readiness architecture remains outside P6。

Execution coherence：

`VERIFIED`

No source-modification authority is granted here。

---

## 15. STOP / Reauthorization Triggers

STOP if future implementation requires：

- modifying `PostgresUnitOfWork` to prove snapshot semantics。
- modifying accepted W1/W2/W3 authority modules。
- changing migrations 0001～0007。
- broker I/O。
- actual PostgreSQL / V07。
- V01～V05。
- C16+ strategy authority。
- new architecture semantics not already frozen。
- a file outside the exact future authorized scope。

---

## 16. Next Governance Action

Separate explicit W4 Runtime Source Modification Authorization decision。

Until then：

`NOT_AUTHORIZED`

Do not start C13 runtime。