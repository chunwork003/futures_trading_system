# GAP-08 Wave-3 — Bounded Runtime Source-Modification Authorization

## 1. Authorization Decision

Wave：

`GAP08-W3-BROKER-RECOVERY-EVIDENCE`

Authorization Decision Baseline：

`09fcfa771ddf3991d52974028b3cc465e9f13f5a`

Execution package：

`docs/work/GAP08_WAVE3_EXECUTION_PACKAGE.md`

Authorized leaves：

    C07
        -> C09
        -> C10

Candidate weight：

15。

Runtime Source Modification Authorization：

`BOUNDED_AUTHORIZED_FOR_GAP08_W3`

Canonical Runtime Authorization：

`NOT_AUTHORIZED`

Production Activation：

`NOT_AUTHORIZED`

This authorization becomes effective only after this authorization document and CURRENT projections are committed and successfully pushed to `origin/master`。

The resulting authorization commit becomes the exact：

`W3 Execution Baseline`

Source modification authority is NOT Runtime Authorization and is NOT Production Activation。

---

## 2. Automatic Progression Boundary

CODEX may progress automatically only：

    C07
        -> C09
        -> C10

and only when the completed leaf passes：

- required targeted tests。
- full regression。
- `git diff --check`。
- exact leaf/cumulative scope validation。
- local leaf commit。
- Working HEAD refresh。
- dependency recheck。
- side-effect envelope unchanged。
- no new architecture/business decision。

No dynamic leaf insertion。

No W4。

No V01～V05 execution。

No C12/C13/C14/C15 implementation。

---

## 3. Authorized Existing Runtime Write Scope

Only：

- `trading/execution.py`
- `persistence/execution.py`
- `persistence/postgres/execution.py`

These are C10 compatibility surfaces only。

C07/C09 must not modify them unless the package explicitly requires the C10 stage。

---

## 4. Authorized New Runtime Files

Only：

- `trading/broker_recovery.py`
- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/postgres/migrations/0007_broker_recovery_evidence.sql`

No additional runtime file may be created。

---

## 5. Authorized Existing Test Write Scope

Only：

- `tests/unit/test_operational_execution.py`
- `tests/unit/test_operational_postgres.py`

These may be modified only for W3 compatibility/repository/migration verification。

---

## 6. Authorized New Test Files

Only：

- `tests/unit/test_c07_broker_discovery.py`
- `tests/unit/test_c09_broker_recovery_fence.py`
- `tests/unit/test_c10_broker_reconstruction.py`

No additional test file may be created。

---

## 7. Read-Only Regression Evidence Tests

These tests may be executed but MUST NOT be modified：

- `tests/unit/test_c04_account_authority_commit.py`
- `tests/unit/test_c06_broker_action_safety.py`
- `tests/unit/test_c08_broker_client_order_ref.py`
- `tests/unit/test_broker_capabilities.py`
- `tests/unit/test_shioaji_mapping.py`
- `tests/unit/test_shioaji_submitted_status.py`

C11 exact regression evidence is：

- `tests/unit/test_shioaji_mapping.py`
- `tests/unit/test_shioaji_submitted_status.py`

The planning-package placeholder `tests/unit/test_c11_shioaji_status_mapping.py` is NOT a file to create。

---

## 8. Leaf-Local Write Envelopes

### C07

May write only：

- `trading/broker_recovery.py`
- `tests/unit/test_c07_broker_discovery.py`

C07 must remain broker-neutral and persistence/network free。

### C09

May write only：

- `trading/broker_recovery.py`
- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/postgres/migrations/0007_broker_recovery_evidence.sql`
- `tests/unit/test_c09_broker_recovery_fence.py`
- `tests/unit/test_operational_postgres.py`

C09 may extend C07 broker-neutral types only where required by the frozen continuity/fence contract。

### C10

May write any file in the total authorized W3 runtime/test set because C10 composes the C07/C09 evidence primitives with accepted execution/account authority。

No file outside the total authorized W3 set may change。

---

## 9. Protected Runtime Surfaces

READ-ONLY：

### Accepted authority

- `persistence/account_authority.py`
- `persistence/postgres/account_authority.py`
- `persistence/broker_action.py`
- `persistence/postgres/broker_action.py`
- `trading/authorization.py`

W3 must consume these semantics as-is。

If existing `BrokerActionResolutionParticipant` or equivalent cannot be safely composed without changing W2 authority：

STOP / REAUTHORIZATION。

### Deferred recovery/reconciliation

- `persistence/recovery.py`
- `persistence/reconciliation.py`
- `persistence/postgres/reconciliation.py`
- `trading/reconciliation.py`

W3 does not implement C12/C13/C14/C15。

C09 may persist recovery control/evidence but MUST NOT claim a complete C12 RecoveryCut or final C15 BrokerAccount READY/REVIEW/HALT authority。

### Account authority/projection

- `persistence/account.py`
- `persistence/postgres/account.py`
- `trading/account.py`

C10 must reuse these existing models/contracts。

If modification is required：

STOP / REAUTHORIZATION。

### Strategy / market observation

- `persistence/strategy_state.py`
- `persistence/postgres/strategy_state.py`
- `persistence/market_observation.py`
- `persistence/postgres/market_observation.py`
- `persistence/market_observation_delivery.py`

### Broker-specific adapters/capability registry

READ-ONLY：

- all `backtest/shioaji_*`
- all `adapters/sinopac/*`
- `adapters/capabilities.py`

No Shioaji/Sinopac runtime capability may be inferred or added in W3。

### Other

- unrelated backtest/strategy/risk/domain modules。
- `data/`。

---

## 10. Migration Authority

Historical migrations：

`0001` through `0006`

READ-ONLY。

Authorized new migration source：

`0007_broker_recovery_evidence.sql`

Creation：

ALLOW。

Amendment within W3 before any execution：

ALLOW under exact W3 scope。

Migration execution：

DENY。

Backfill：

DENY。

Destructive migration：

DENY。

Actual PostgreSQL：

DENY。

V07：

DENY。

No migration can be executed by CODEX in this Wave。

---

## 11. Side-Effect Envelope

ALLOW：

- exact W3 source modification。
- unit test execution。
- full regression execution。
- creation/amendment of unexecuted 0007。
- fake/mock broker-neutral provider evidence in tests。
- fake/in-memory repository/unit-of-work evidence in tests。

DENY：

- migration execution。
- actual PostgreSQL access。
- V07。
- broker network I/O。
- paper broker I/O。
- Shioaji simulation I/O。
- Shioaji production I/O。
- callback registration against a real broker。
- credential/API-key/certificate access。
- production capability verification。
- production activation。
- real order submission/cancel/query。
- real `list_trades` / refresh。
- real subscription repair。
- manual unresolved-attempt release/override。

---

## 12. C07 Required Semantics

C07 must implement the frozen broker-neutral discovery contract。

At minimum：

1. BrokerAccount scope is explicit on request/result/evidence。
2. wrong-account evidence fails closed。
3. discovery has stable immutable `discovery_run_id`。
4. required scope/horizon/currentness/refresh evidence is explicit。
5. discovery completeness is separate from exact-match cardinality。
6. exact-match cardinality distinguishes ZERO / ONE / MULTIPLE or exact equivalent。
7. incomplete zero is not absence authority。
8. complete zero is only absence inside the verified required scope/horizon。
9. complete zero never overrides an unresolved BrokerActionAttempt。
10. multiple exact correlation matches produce ambiguity/integrity classification。
11. positive evidence can be retained under incomplete discovery。
12. provider is read-only and broker-neutral。
13. no process-memory Trade/native cache is restart authority。
14. no attribute/time heuristic becomes identity authority。
15. query/external-state failure is typed/account-scoped。
16. no Shioaji object/import in broker-neutral core。

C07 does not prove V01/V02/V03/V04/V05。

---

## 13. C09 Required Semantics

C09 must implement durable recovery evidence/control without becoming economic account authority。

At minimum：

1. immutable BrokerReportInboxEntry or equivalent durable ingress evidence。
2. exact duplicate ingress is idempotent/corroborating。
3. same ingress identity + conflicting material content fails closed。
4. inbox capture does not advance AccountStateHead。
5. immutable BrokerReportApplication history supports:
   - APPLIED
   - DUPLICATE
   - CORROBORATED
   - DEFERRED
   - CONFLICT
6. post-cut broker evidence is durably captured and deferred, never dropped。
7. post-cut evidence does not directly bypass the active recovery fence。
8. durable AccountRecoveryControl/generation is distinct from AccountStateHead。
9. `recovery_cut_revision` is an AccountStateHead revision reference used by the short fence; W3 MUST NOT claim that revision alone is the complete C12 RecoveryCut。
10. stale generation/cut cannot finalize handoff。
11. ExecutionContinuityEpoch/current-trust evidence is durable。
12. historical degradation remains durable after re-anchor。
13. re-anchor never rewrites SequenceGap history。
14. PendingReport/unapplied material evidence prevents applicable continuity/completeness trust。
15. final handoff repository/transaction primitive is race-safe with concurrent durable ingress。
16. no actual broker callback registration/network I/O。

---

## 14. C10 Required Semantics

C10 must implement broker-neutral reconstruction and atomic authority application。

At minimum：

1. reconstruction consumes only broker-neutral discovery/inbox/deal evidence。
2. canonical OrderEvent provenance can distinguish LOCAL_OMS / BROKER_CALLBACK / BROKER_DISCOVERY or exact equivalent。
3. recovery never fabricates unsupported intermediate lifecycle history。
4. evidence-backed PENDING -> PARTIALLY_FILLED is legal。
5. evidence-backed PENDING -> FILLED is legal。
6. PARTIALLY_FILLED -> PARTIALLY_FILLED with newly accepted Fill evidence is material。
7. exact BrokerDealIdentity is required to create canonical recovery Fill。
8. no timestamp/price/quantity heuristic identity fallback。
9. no broker aggregate synthetic Fill。
10. same DealIdentity + same material content deduplicates/corroborates。
11. same DealIdentity + conflicting material content is integrity conflict。
12. complete LocalFillSet is read before projecting economics。
13. filled_quantity derives from canonical Fill-set quantity sum。
14. average_fill_price derives from exact quantity-weighted canonical Fill set。
15. broker aggregate quantity/average is validation evidence only。
16. terminal accepted lifecycle/economics is sealed。
17. no Fill/economic enrichment after terminal acceptance。
18. incomplete/conflicting/capability-unverified reconstruction commits no partial authority mutation。
19. existing AccountAuthorityCommit is the only BrokerAccount revision authority。
20. recovery-cut account revision maps to expected_head_revision and stale mismatch aborts。
21. position-changing Fill requires complete AccountPositionSnapshot in same authority transaction。
22. status-only transition carries forward exact prior expected_snapshot_id。
23. execution participant and BrokerActionResolution participant share one AccountAuthorityCommit when the same evidence set requires both。
24. no broker network I/O while AccountAuthorityCommit UoW/lock is active。
25. no second recovery economic persistence authority is created。

---

## 15. Capability Default-Deny

W3 MUST NOT claim：

- Shioaji discovery scope/horizon is production verified。
- `custom_field` round-trip is production verified。
- `Deal.seq` is restart-stable production BrokerDealIdentity。
- pinned event tracking/continuity is production verified。
- PreSubmitted / Inactive / Failed production semantics are verified。
- quantity-modification recovery is supported。
- broker callback delivery is exactly once。
- broker server-side idempotent resubmission exists。
- process-memory Trade cache is recovery authority。

V01～V05 remain separate and NOT_AUTHORIZED。

Tests may use explicit fake broker-neutral “verified identity/currentness” evidence solely to verify core behavior；that test fixture must not be labelled Sinopac/Shioaji production verification。

---

## 16. C07 Required Tests

Run：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c07_broker_discovery.py `
        tests/unit/test_c08_broker_client_order_ref.py `
        tests/unit/test_c06_broker_action_safety.py `
        tests/unit/test_broker_capabilities.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Then：

    git diff --check

Then exact C07 scope validation。

Only after PASS：

commit C07 locally。

Do not push。

Refresh Working HEAD before C09。

---

## 17. C09 Required Tests

Run：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c09_broker_recovery_fence.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_c06_broker_action_safety.py `
        tests/unit/test_operational_postgres.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Then：

    git diff --check

Then exact C09 cumulative scope validation。

Only after PASS：

commit C09 locally。

Do not push。

Refresh Working HEAD before C10。

---

## 18. C10 Required Tests

C11 read-only regression evidence is the actual existing pair：

- `tests/unit/test_shioaji_mapping.py`
- `tests/unit/test_shioaji_submitted_status.py`

Run：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c10_broker_reconstruction.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_c06_broker_action_safety.py `
        tests/unit/test_shioaji_mapping.py `
        tests/unit/test_shioaji_submitted_status.py `
        tests/unit/test_operational_execution.py `
        tests/unit/test_operational_postgres.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Then：

    git diff --check

Then exact C10 cumulative scope validation。

Only after PASS：

commit C10 locally。

---

## 19. Wave Final Verification

Run：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c07_broker_discovery.py `
        tests/unit/test_c09_broker_recovery_fence.py `
        tests/unit/test_c10_broker_reconstruction.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_c06_broker_action_safety.py `
        tests/unit/test_c08_broker_client_order_ref.py `
        tests/unit/test_broker_capabilities.py `
        tests/unit/test_shioaji_mapping.py `
        tests/unit/test_shioaji_submitted_status.py `
        tests/unit/test_operational_execution.py `
        tests/unit/test_operational_postgres.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Then：

    git diff --check

Then exact cumulative W3 scope validation。

No actual PostgreSQL or broker capability test is part of W3。

---

## 20. Git Policy

Per-leaf local commits：

ALLOW。

Expected sequence：

    C07
        -> C09
        -> C10

Intermediate push：

DENY by default。

Wave-end push：

ALLOW only after final Wave verification。

Force push：

DENY。

Before wave-end push：

    git fetch origin master

`origin/master` must still equal the exact W3 Execution Baseline created by this authorization commit。

If remote diverged：

STOP。

No rebase / merge / force push / history rewrite。

`data/` must never be staged。

---

## 21. Semantic Correction Budget

Maximum：

2 scope-internal semantic correction cycles per leaf。

Tooling retries do not consume semantic correction budget but must remain finite。

Repeated same-class tooling failure requires root-cause correction before retry。

Authority / revision contradiction：

STOP。

Architecture contradiction：

STOP。

---

## 22. Documentation / Comment Rule

Important new module/class/public function/public contract comments/docstrings must be Traditional Chinese and describe applicable：

- 用途。
- 責任。
- upstream / 資料來源。
- downstream consumer。
- invariant。
- non-obvious broker/recovery rule。
- explicit non-responsibility。

Important PostgreSQL TABLE / COLUMN / FUNCTION comments must follow existing Traditional Chinese documentation requirements。

Do not add low-value translation-only comments。

---

## 23. Mandatory STOP / Reauthorization

STOP if any of the following is required：

- file outside exact W3 write set。
- additional new runtime/test/migration file。
- modification of `persistence/recovery.py`。
- modification of reconciliation modules。
- modification of W1/W2 authority modules。
- modification of account projection modules。
- modification of any Shioaji/Sinopac adapter/capability registry。
- migration execution。
- actual PostgreSQL / V07。
- broker network/paper/simulation/production I/O。
- real callback registration。
- credential access。
- production capability verification。
- V01～V05 execution。
- C12/C13/C14/C15 implementation。
- quantity-modification recovery。
- manual unresolved-attempt release/override。
- new architecture/business decision。
- destructive migration。
- unrelated regression。
- semantic correction budget exceeded。
- remote divergence。

---

## 24. Completion Boundary

After C10 + Wave final verification + wave-end push：

STOP。

CODEX MUST NOT：

- update reviewer acceptance/closure docs。
- mark W3 accepted/closed。
- credit W3 weight 15。
- mark GAP-08 closed。
- start another Wave。
- execute migration 0007。
- access actual PostgreSQL。
- perform any real broker I/O。
- run V01～V05 capability verification。
- activate runtime/production。

Return the final W3 execution report to reviewer。

---

## 25. CODEX Start Gate

CODEX may start only when：

- local HEAD == origin/master == W3 authorization commit。
- tree is clean except known `data/`。
- exact W3 authorization file is readable。
- no remote divergence。
- no source changes occurred between planning and authorization。

Read before execution：

1. `docs/CURRENT_STATE.md`
2. `docs/work/GAP08_WAVE3_AUTHORIZATION.md`
3. `docs/work/GAP08_WAVE3_EXECUTION_PACKAGE.md`
4. `docs/work/GAP08_CORRECTION_FREEZE.md`
5. `docs/adr/ADR-002-RECOVERY-CONSISTENCY-MARKET-OBSERVATION.md`
6. `docs/CODEX_EXECUTION_WORKFLOW.md`
7. `AGENTS.md`

First executable leaf：

C07。

Execution mode：

LEVEL_3A_BOUNDED。

Automatic progression only through C07 -> C09 -> C10。

---

## 26. Current Progress

Accepted correction-core progress：

60 / 113。

Remaining：

53。

W3 candidate weight：

15 / NOT CREDITED until reviewer closure。

Canonical Runtime Authorization：

NOT_AUTHORIZED。

Production Activation：

NOT_AUTHORIZED。