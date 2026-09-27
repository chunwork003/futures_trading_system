# GAP-08 Wave-4 / P6 — Runtime Source Modification Authorization

## 1. Authority

Wave：

`GAP08-W4-LOCAL-RECOVERY-RECONCILIATION`

Planning Baseline：

`a936a4827b53609bcd15383d62bcc515d26140b6`

Execution package：

`docs/work/GAP08_WAVE4_EXECUTION_PACKAGE.md`

Authorized leaves：

`C13 -> C12 -> C14 -> C15`

Candidate weight：

18 / NOT CREDITED until reviewer closure。

Execution coherence：

`VERIFIED`

Runtime Source Modification Authorization：

`BOUNDED_AUTHORIZED_FOR_GAP08_W4`

Canonical Runtime Authorization：

`NOT_AUTHORIZED`

Production Activation：

`NOT_AUTHORIZED`

Architecture Acceptance：

`HOLD`

This authorization permits bounded source/test/migration-source modification only。

It does not authorize runtime activation or external side effects。

---

## 2. Efficient Execution Rule

Use：

`Wave Shared Context + Leaf Delta Context`

Shared context is resolved once from：

- this authorization。
- `docs/work/GAP08_WAVE4_EXECUTION_PACKAGE.md`。
- `docs/CURRENT_STATE.md`。
- `AGENTS.md`。

Do not reread or restate full ADR / correction-freeze prose unless a concrete contradiction requires it。

After each leaf：

- refresh HEAD。
- retain unaffected shared context。
- invalidate only changed read-set。
- load only the next leaf delta。

Final reports return new evidence only。

---

## 3. Exact Wave Write Scope

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

No other file is writable。

No additional new file is authorized。

---

## 4. Protected / Read-Only

Read-only unless separate reauthorization：

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
- governance docs after this authorization commit
- `data/`

If a leaf requires changing a protected file：

`STOP / REAUTHORIZATION`

---

## 5. Leaf Locality

### C13 writable subset

- `trading/reconciliation.py`
- `persistence/reconciliation.py`
- `persistence/postgres/reconciliation.py`
- `persistence/postgres/migrations/0008_local_recovery_reconciliation.sql`
- `tests/unit/test_reconciliation.py`
- `tests/unit/test_operational_account.py`
- `tests/unit/test_operational_postgres.py`
- new `tests/unit/test_c13_reconciliation_case_scope.py`

### C12 writable subset

- `persistence/recovery.py`
- new `persistence/postgres/recovery.py`
- `tests/unit/test_recovery_orchestration.py`
- `tests/unit/test_operational_postgres.py`
- new `tests/unit/test_c12_recovery_cut.py`

### C14 writable subset

- `persistence/reconciliation.py`
- `persistence/postgres/reconciliation.py`
- `persistence/postgres/migrations/0008_local_recovery_reconciliation.sql`
- `tests/unit/test_reconciliation.py`
- `tests/unit/test_operational_postgres.py`
- new `tests/unit/test_c14_reconciliation_run.py`

### C15 writable subset

- `persistence/recovery.py`
- `persistence/postgres/recovery.py`
- `tests/unit/test_recovery_orchestration.py`
- `tests/unit/test_operational_postgres.py`
- new `tests/unit/test_c15_account_recovery_readiness.py`

A leaf may not opportunistically edit another leaf's files merely because they are in the Wave scope。

Cross-leaf change required before its dependency turn：

STOP / REVIEW。

---

## 6. C13 Contract

Reference：

Execution Package section 7 + frozen C13 acceptance boundary。

Must establish：

- exact one-primary-BrokerAccount scope on every ReconciliationCase。
- same case_id cannot drift account scope across versions。
- unresolved repository query becomes exact-account scoped。
- Account A unresolved case cannot gate Account B。
- append-only history remains。
- ambiguous legacy unscoped history fails closed；no guessed backfill。
- case state is not economic/readiness truth authority。

C13 does not implement ReconciliationRun or final READY。

---

## 7. C12 Contract

Reference：

Execution Package section 8 + ADR-002 R-05A～R-05F。

Must establish：

- explicit immutable ExecutionRestoreResult。
- coherent BrokerAccount-local RecoveryCut。
- VALID / BASELINE_NOT_ESTABLISHED / RESTORE_FAILURE contract。
- baseline-not-established requires positive lifecycle proof。
- exact head/checkpoint/snapshot/receipt validation。
- deterministic coverage of non-revision recovery evidence/currentness。
- one verified PostgreSQL consistency boundary。
- no independent latest-read composition masquerading as a coherent cut。
- no broker I/O / repair / re-anchor / economic mutation / head advance。
- VALID != READY。

`persistence/postgres/uow.py` remains read-only。

If coherent snapshot semantics cannot be proven without changing it：

STOP / REAUTHORIZATION。

---

## 8. C14 Contract

Reference：

Execution Package section 9 + ADR-002 R-12A～R-12H。

Must establish：

- durable BrokerAccount-scoped ReconciliationRun boundary。
- run boundary durable before result-bearing formal evaluation。
- crash leaves detectable non-finalized run。
- exact immutable/versioned evaluated-world binding。
- technical outcome / input qualification / domain result separated。
- run lifecycle distinct from case lifecycle。
- one authoritative terminal outcome。
- identical terminal retry idempotent。
- conflicting finalization fail closed。
- terminal outcome + required result evidence crash-consistent。
- finalized run cannot expose partial result evidence。
- historical MATCH is not current READY authority。
- no latest-run -> MATCH -> READY shortcut。
- ReconciliationRun does not advance AccountStateHead。

---

## 9. C15 Contract

Reference：

Execution Package section 10 + ADR-002 R-04H。

Must establish：

- precedence HALT > REVIEW > READY。
- READY requires positive proof of all mandatory account recovery predicates。
- UNKNOWN / DEGRADED / NO_ERROR_OBSERVED never imply READY。
- coherent C12 VALID cut required but insufficient。
- eligible C14 formal run required where applicable。
- W3 C07/C09/C10 evidence consumed read-only。
- unresolved BrokerActionAttempt requiring disposition blocks READY。
- position MATCH alone never grants READY。
- restored strategy alone never grants BrokerAccount READY。
- final handoff revalidates exact revision + non-revision cut/currentness + recovery generation/frontier。
- stale evaluation forces reevaluation。
- readiness does not advance economic AccountStateHead。
- no bypass of C06 no-blind-retry / R-13 authorization。
- no broker I/O in local final-currentness transaction。
- do not implement C16～C20 strategy authority。

Legacy `recover_runtime()` compatibility must not preserve the old READY shortcut。

---

## 10. Migration 0008

Authorized source file：

`persistence/postgres/migrations/0008_local_recovery_reconciliation.sql`

May be created during C13 and amended during C14 if required by the frozen package。

May contain only P6 schema/index/constraint support：

- ReconciliationCase BrokerAccount scope。
- formal ReconciliationRun audit。
- exact identity / append-only / terminal-finalization constraints。

Migration execution：

`DENY`

Actual PostgreSQL / V07：

`DENY`

Migrations `0001`～`0007`：

READ-ONLY。

No `0009`。

No destructive migration or guessed legacy backfill。

---

## 11. Leaf Test Gates

C13：

`.\.venv\Scripts\python.exe -m pytest tests/unit/test_c13_reconciliation_case_scope.py tests/unit/test_reconciliation.py tests/unit/test_operational_account.py tests/unit/test_operational_postgres.py -q`

C12：

`.\.venv\Scripts\python.exe -m pytest tests/unit/test_c12_recovery_cut.py tests/unit/test_recovery_orchestration.py tests/unit/test_c04_account_authority_commit.py tests/unit/test_c06_broker_action_safety.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_operational_postgres.py -q`

C14：

`.\.venv\Scripts\python.exe -m pytest tests/unit/test_c14_reconciliation_run.py tests/unit/test_reconciliation.py tests/unit/test_c12_recovery_cut.py tests/unit/test_operational_postgres.py -q`

C15：

`.\.venv\Scripts\python.exe -m pytest tests/unit/test_c15_account_recovery_readiness.py tests/unit/test_recovery_orchestration.py tests/unit/test_c07_broker_discovery.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c10_broker_reconstruction.py tests/unit/test_c12_recovery_cut.py tests/unit/test_c14_reconciliation_run.py tests/unit/test_operational_postgres.py -q`

After each leaf targeted PASS：

`.\.venv\Scripts\python.exe -m pytest -q`

Then：

`git diff --check`

Then exact cumulative Wave scope + leaf-local scope validation。

No leaf commit if any gate fails。

---

## 12. Automatic Wave Progression

C13 -> C12 -> C14 -> C15 may advance without another human authorization only if the completed leaf has：

- exact leaf-local scope PASS。
- targeted PASS。
- full regression PASS。
- `git diff --check` PASS。
- semantic correction budget not exceeded。
- no architecture/authority contradiction。
- no protected-file requirement。
- leaf commit complete。
- next dependency still valid。

Leaf-local PASS is not reviewer acceptance。

If any condition fails：

STOP。

---

## 13. Semantic Correction Budget

Each leaf：

maximum **2 scope-internal semantic correction cycles**。

This is intentionally pre-authorized to reduce governance churn while preserving bounded execution。

A third semantic correction requirement for the same leaf：

`STOP / REAUTHORIZATION`

Tooling retries：

finite and do not consume semantic budget。

Repeated same tooling failure requires root-cause inspection；do not loop blindly。

Test-fixture correction counts as semantic correction only when it changes the asserted contract，not when it merely repairs tooling/serialization/fixture mechanics without semantic change。

---

## 14. Git Policy

Per leaf：

one bounded commit after all leaf gates pass。

Suggested messages：

- `fix(reconciliation): scope cases by broker account`
- `feat(recovery): add coherent recovery cut loader`
- `feat(reconciliation): add formal reconciliation run audit`
- `feat(recovery): add broker account readiness gate`

Intermediate push：

`DENY`

Wave-end push after C15：

`ALLOW`

Before wave-end push：

`git fetch origin master`

`origin/master` must equal the W4 authorization commit created from this document。

If remote diverges：

STOP。

No merge / rebase / amend-public-history / force push。

`data/` must never be staged。

---

## 15. Side-Effect Envelope

Allowed：

- bounded source modification in exact Wave scope。
- unit / integration / full-regression tests using fake/mock/in-memory evidence。
- Git local commits。
- one wave-end push after all four leaves pass。

Denied：

- migration execution。
- actual PostgreSQL。
- V07。
- broker network。
- paper broker。
- Shioaji simulation / production。
- callback registration。
- credential access。
- V01～V05 capability verification。
- production activation。
- R-13 manual authority implementation。
- C16～C20。
- P7 / next Wave。

---

## 16. Comments / Documentation

Important CODEX-created/modified module、class、function、non-obvious invariant comments/docstrings：

Traditional Chinese。

At minimum explain：

- responsibility。
- upstream source。
- downstream consumer。
- authority boundary。
- non-obvious fail-closed rule。

Avoid comments that merely restate code syntax。

---

## 17. Wave Completion Boundary

After C15 gates pass：

- run final Wave targeted suite from Execution Package。
- run full regression。
- validate exact cumulative scope。
- validate migrations 0001～0007 unchanged。
- validate 0008 NOT_EXECUTED。
- validate protected files unchanged。
- validate no external side effects。
- fetch/check remote ancestry。
- push Wave commits once。
- STOP and return to reviewer。

Do not：

- mark W4 accepted/closed。
- credit weight 18。
- update governance closure docs。
- begin P7。
- execute migration 0008。
- access actual PostgreSQL。
- perform broker I/O。

---

## 18. Efficient Final Report

Return only new evidence：

- authorization execution baseline。
- final HEAD。
- per-leaf commit SHAs。
- exact changed files。
- per-leaf targeted results。
- per-leaf full regression results。
- final Wave targeted/full regression。
- correction counts per leaf。
- tooling retries。
- scope/protected/migration guards。
- migration execution / PG / broker I/O = NO。
- origin/master synchronization。
- STOP status。

Do not restate unchanged architecture or frozen contract。