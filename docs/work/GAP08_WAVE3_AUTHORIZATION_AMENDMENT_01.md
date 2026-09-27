# GAP-08 Wave-3 — Reviewer Correction Authorization Amendment 01

## 1. Reviewer Status

Wave：

`GAP08-W3-BROKER-RECOVERY-EVIDENCE`

Original W3 Execution Baseline：

`723961e0059a826e7d454f6530341f0c6f1f8b2e`

First-pass W3 Runtime Candidate：

`b270932dfa04f17528c0dc0ff74aab2b95094ab8`

First-pass commits：

- C07：`ff86f8a2452269f0a80810015ac6e9bdf7c3b1af`
- C09：`26fa593286b08d0428fa705aaf387e7c1cf1fcd1`
- C10：`b270932dfa04f17528c0dc0ff74aab2b95094ab8`

Reviewer status：

`HOLD / RF01_REQUIRED`

C07：

`REVIEWER_PASS / READ_ONLY`

C09：

`HOLD / RF01_REQUIRED`

C10：

`HOLD / RF01_REQUIRED`

W3 weight：

15 / NOT CREDITED。

Accepted correction-core progress remains：

60 / 113。

Remaining：

53。

Runtime Source Modification Authorization：

`BOUNDED_AUTHORIZED_FOR_GAP08_W3_RF01`

Canonical Runtime Authorization：

`NOT_AUTHORIZED`

Production Activation：

`NOT_AUTHORIZED`

---

## 2. Reviewer Verification Already Passed

GitHub reviewer verification confirms：

- authorization baseline -> runtime candidate = exactly 3 commits。
- exact repo change scope = exactly 11 W3-authorized files。
- `master == b270932dfa04f17528c0dc0ff74aab2b95094ab8` at reviewer inspection。
- C07 implementation remains broker-neutral and within its leaf envelope。
- migration 0007 was created but not executed。
- migrations 0001～0006 remain outside the W3 runtime diff。
- protected governance/runtime files were not changed by W3 execution。
- no broker / paper / Shioaji simulation / production I/O was reported。
- no actual PostgreSQL / V07 was reported。
- V01～V05 were not executed。

First-pass executor evidence：

- C07 targeted：57 passed。
- C07 full：1161 passed / 4 skipped。
- C09 targeted：47 passed。
- C09 full：1171 passed / 4 skipped。
- C10 targeted：84 passed。
- C10 full：1181 passed / 4 skipped。
- Wave targeted：131 passed。
- Wave full：1181 passed / 4 skipped。
- `git diff --check`：PASS。
- first-pass user-reported 5HR quota observation：48%。
- C07 semantic corrections：0。
- C09 semantic corrections：1。
- C10 semantic corrections：1。

These passes do NOT override the reviewer findings below。

---

## 3. RF01-A — C09 Durable Ingress Frontier Is Not PostgreSQL-Enforced

Current in-memory C09 test repository：

- increments `ingress_version` when a new inbox entry is appended。
- updates active recovery control frontier。
- therefore stale frontier blocks final handoff。

Current PostgreSQL repository：

- inserts `broker_report_inbox`。
- does NOT update / lock / consume `account_recovery_controls.ingress_version` during ingress capture。
- final handoff checks `ingress_version` but that frontier is not advanced by PostgreSQL ingress。

Therefore the fake repository demonstrates stronger semantics than the PostgreSQL adapter。

This does NOT prove the required：

`Final handoff from RECOVERING to normal must be race-free with callback ingress.`

RF01-A is blocking。

---

## 4. RF01-A Required Semantics

For the active recovery generation of one BrokerAccount：

1. a genuinely NEW inbox capture and the active `AccountRecoveryControl` frontier update must be one caller-owned transaction。
2. the new durable ingress must advance the durable `ingress_version` exactly once。
3. exact duplicate ingress must NOT advance the frontier again。
4. ingress capture and final handoff must serialize through the same durable account recovery-control authority / row or an equivalent database-enforced primitive。
5. if capture wins the race：
   - frontier advances。
   - stale finalization fails。
6. if final handoff wins the race：
   - later capture must not be silently attached to the closed generation as if recovery were still active。
   - it remains durable evidence and must be handled under an explicit post-handoff/current-generation path rather than lost。
7. active generation mismatch must fail closed；it must not silently mutate another generation。
8. no process-memory-only frontier authority。
9. no independent repository commit / rollback。
10. inbox capture itself still does NOT advance AccountStateHead。

Physical SQL shape is not prescribed。

The result MUST be database-enforced and free of check-then-write TOCTOU authority。

---

## 5. RF01-B — C09 Application Disposition Can Be Incorrectly Treated As Resolved

Current final-handoff SQL treats an inbox entry as resolved when ANY application row exists with status：

- APPLIED
- DUPLICATE
- CORROBORATED

It does not prove that this row is：

- for the same active generation。
- the authoritative latest disposition。
- not superseded by a later DEFERRED / CONFLICT outcome。

Therefore examples such as：

- wrong-generation APPLIED。
- earlier APPLIED followed by later CONFLICT。
- stale success evidence followed by later DEFERRED。

can incorrectly satisfy the current handoff predicate。

RF01-B is blocking。

---

## 6. RF01-B Required Semantics

BrokerReportApplication history remains immutable / append-only。

The durable model must provide a non-time-based deterministic application ordering/current-disposition authority per ingress。

Equivalent implementations are allowed, for example：

- per-ingress monotonic application sequence/version。
- immutable history plus a separately durable current-disposition projection。

Timestamps alone MUST NOT become causal/currentness authority。

Final handoff may consider an inbox resolved only when：

1. application belongs to the exact same ingress identity。
2. application belongs to the exact relevant recovery generation。
3. the authoritative CURRENT/LATEST disposition is one of：
   - APPLIED
   - DUPLICATE
   - CORROBORATED
4. authoritative CURRENT/LATEST disposition DEFERRED blocks handoff。
5. authoritative CURRENT/LATEST disposition CONFLICT blocks handoff。
6. wrong-generation success cannot satisfy the active generation。
7. exact duplicate application identity + identical content is idempotent or otherwise deterministically non-destructive。
8. same application identity + conflicting content fails closed。
9. history is never overwritten/deleted。

No wall-clock ordering substitute。

---

## 7. RF01-C — C10 Can Produce PARTIALLY_FILLED With Zero Fill Evidence

Current `reconstruct_broker_order()` computes：

- FILLED when canonical fill quantity == order.quantity。
- otherwise PARTIALLY_FILLED。

Therefore quantity 0 currently yields PARTIALLY_FILLED。

Current C10 test for status-only snapshot carry-forward also uses：

- PARTIALLY_FILLED
- filled_quantity = 0
- no accepted Fill

which does not prove the frozen material-evidence rule。

Frozen ADR requires：

- PENDING -> PARTIALLY_FILLED only when supported by material Fill evidence。
- PARTIALLY_FILLED -> PARTIALLY_FILLED only with newly accepted Fill evidence for a material same-status change。
- status-only recovery carries forward exact prior expected_snapshot_id。

RF01-C is blocking。

---

## 8. RF01-C Required Lifecycle / Economics Semantics

Recovery lifecycle authority and Fill economics must be distinct inputs/concerns。

At minimum：

### Fill-derived economics

- canonical Fill set is the only internal filled-economic authority。
- filled_quantity = exact sum of canonical Fill quantities。
- average_fill_price = exact quantity-weighted canonical Fill value when quantity > 0。
- zero canonical Fill => filled_quantity = 0 and average_fill_price = None。
- zero canonical Fill MUST NOT produce PARTIALLY_FILLED。

### PARTIALLY_FILLED

Canonical PARTIALLY_FILLED requires：

    0 < filled_quantity < order.quantity

and exact accepted Fill evidence。

A same-status PARTIALLY_FILLED -> PARTIALLY_FILLED material event requires newly accepted Fill evidence。

### FILLED

Canonical FILLED requires：

    filled_quantity == order.quantity

and complete identifiable canonical Fill evidence。

### CANCELLED

Canonical CANCELLED may be accepted only with explicit broker-neutral lifecycle evidence and:

    0 <= filled_quantity < order.quantity

Prior/newly reconstructed fills may exist。

### REJECTED

Canonical REJECTED requires explicit verified broker-neutral failure semantics proving original-order failure with zero economic effect。

W3 tests may use fake verified broker-neutral semantics only。

This MUST NOT claim Shioaji V05 production verification。

### SUBMITTED / status-only

A status-only transition requires explicit broker-neutral lifecycle evidence accepted by the frozen semantics。

PendingSubmit alone MUST NOT automatically promote canonical SUBMITTED。

Status-only transition:

- accepts no new Fill。
- carries forward exact prior expected_snapshot_id。
- creates no fabricated economics。

If there is no lifecycle change and no newly accepted material Fill：

no fabricated material recovery event may be committed merely to force progress。

---

## 9. RF01-D — C10 BrokerDeal Scope / Material-Content Integrity Is Incomplete

Current reconstruction checks：

- `order_id`
- `broker_client_order_ref`
- quantity
- price

but does not bind every BrokerDealIdentity to the AccountAuthorityCommit broker/account scope。

Current local-vs-broker same DealIdentity comparison does not include all canonical material content such as occurrence evidence。

Therefore wrong-account evidence with matching order/ref could be accepted by pure reconstruction, and same DealIdentity with materially different persisted occurrence evidence can be treated as corroborating。

RF01-D is blocking。

---

## 10. RF01-D Required Deal Integrity Semantics

For every accepted recovery deal：

1. BrokerDealIdentity.broker must equal the authority mutation broker。
2. BrokerDealIdentity.account_ref must equal the authority mutation account_ref。
3. deal order_id must equal canonical order_id。
4. broker_client_order_ref must equal canonical immutable ref。
5. same BrokerDealIdentity + same canonical material content => duplicate / corroborating。
6. same BrokerDealIdentity + different canonical material content => INTEGRITY_CONFLICT。
7. canonical material-content comparison must include at least:
   - order identity。
   - quantity。
   - price。
   - broker occurrence time when present as canonical evidence。
   - exact broker/account deal scope。
8. no timestamp/price/quantity heuristic is identity。
9. callback-only identity remains insufficient as restart Fill identity。
10. exact verified BrokerDealIdentity remains required。

If reconstruction input explicitly claims a COMPLETE broker DealSet：

- complete broker DealSet proper subset of durable LocalFillSet => INTEGRITY_CONFLICT。
- missing broker-side identity evidence must not be silently repaired from aggregates。

If evidence is incomplete：

- do not make a false corruption claim。
- do not canonically accept a terminal/economic state that requires missing evidence。

---

## 11. C07 Reviewer Decision

C07：

`PASS / NO_CORRECTION_REQUIRED`

C07 is READ-ONLY under RF01。

No C07 runtime/test modification is authorized。

---

## 12. Exact RF01 Runtime / Test / Migration Scope

Authorized runtime/migration files only：

- `trading/broker_recovery.py`
- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/postgres/migrations/0007_broker_recovery_evidence.sql`

Authorized test files only：

- `tests/unit/test_c09_broker_recovery_fence.py`
- `tests/unit/test_c10_broker_reconstruction.py`
- `tests/unit/test_operational_postgres.py`

No new files。

Everything else READ-ONLY。

Specifically READ-ONLY：

- `trading/execution.py`
- `persistence/execution.py`
- `persistence/postgres/execution.py`
- `tests/unit/test_operational_execution.py`
- `tests/unit/test_c07_broker_discovery.py`
- all W1/W2 authority files。
- account projection files。
- recovery orchestration / reconciliation files。
- all Shioaji / Sinopac files。
- capability registry。
- governance docs after this amendment is committed。
- `data/`。

If RF01 cannot be completed inside these exact 7 files：

STOP / REAUTHORIZATION。

---

## 13. Migration Rule

Migration 0007：

NOT EXECUTED。

Therefore 0007 may be amended in a new Git commit under RF01。

Migrations 0001～0006：

READ-ONLY。

Do not create 0008。

Migration execution：

DENY。

Actual PostgreSQL：

DENY。

V07：

DENY。

Backfill：

DENY。

Destructive migration：

DENY。

---

## 14. Required RF01 Tests — C09

Minimum new/updated evidence must prove：

1. new ingress during active recovery atomically advances durable ingress frontier exactly once。
2. exact duplicate ingress does not advance frontier。
3. stale/wrong active generation ingress fails closed。
4. capture/finalize race is serialized by one DB-enforced recovery-control primitive。
5. capture-wins => stale finalization fails。
6. handoff-wins => later capture cannot masquerade as belonging to the closed generation。
7. wrong-generation APPLIED cannot resolve current generation ingress。
8. APPLIED then later CONFLICT => current disposition blocks handoff。
9. DEFERRED then later APPLIED => current disposition may resolve if all other predicates hold。
10. application ordering/current disposition does not use timestamps as authority。
11. duplicate identical application identity is deterministic/idempotent。
12. conflicting duplicate application identity fails closed。
13. PostgreSQL adapter does not commit/rollback independently。
14. 0007 encodes the required durable ordering/frontier constraints/evidence。

C09 targeted：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c09_broker_recovery_fence.py `
        tests/unit/test_operational_postgres.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_c06_broker_action_safety.py `
        -q

---

## 15. Required RF01 Tests — C10

Minimum new/updated evidence must prove：

1. zero Fill set never yields PARTIALLY_FILLED。
2. PENDING -> PARTIALLY_FILLED requires exact accepted Fill evidence。
3. PENDING -> FILLED requires complete canonical Fill evidence。
4. PARTIALLY_FILLED -> PARTIALLY_FILLED material event requires newly accepted Fill evidence。
5. verified broker-neutral CANCELLED with zero fills can be status-only and carries prior exact snapshot。
6. CANCELLED with partial canonical fills preserves fill economics and still carries/updates snapshot according to whether new Fill was accepted in this commit。
7. REJECTED requires verified zero-economic-effect failure semantics。
8. unverified REJECTED / capability-unverified status does not commit。
9. PendingSubmit-like unverified evidence does not auto-promote SUBMITTED。
10. valid status-only transition uses exact prior expected_snapshot_id。
11. no lifecycle change + no new Fill does not fabricate a material event。
12. wrong broker/account BrokerDealIdentity fails closed。
13. same DealIdentity + same full canonical material content corroborates。
14. same DealIdentity + changed quantity conflicts。
15. same DealIdentity + changed price conflicts。
16. same DealIdentity + changed broker occurrence time conflicts when occurrence time is part of accepted canonical evidence。
17. complete broker DealSet proper subset of LocalFillSet conflicts。
18. incomplete broker evidence does not fabricate terminal acceptance。
19. terminal exact duplicate remains corroborating only。
20. terminal enrichment/regression remains blocked。
21. shared AccountAuthorityCommit composition remains intact。
22. no broker I/O surface is introduced。

C10 targeted：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c10_broker_reconstruction.py `
        tests/unit/test_c09_broker_recovery_fence.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_c06_broker_action_safety.py `
        tests/unit/test_c08_broker_client_order_ref.py `
        tests/unit/test_shioaji_mapping.py `
        tests/unit/test_shioaji_submitted_status.py `
        tests/unit/test_operational_execution.py `
        tests/unit/test_operational_postgres.py `
        -q

Read-only regression tests may be executed but not modified。

---

## 16. Full RF01 Verification

After correction：

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

Then exact RF01 scope validation。

---

## 17. Semantic Correction Budget

First pass reported：

- C07：0。
- C09：1。
- C10：1。

RF01 grants：

- C07：0 additional / READ-ONLY。
- C09：maximum 1 final scope-internal semantic correction cycle。
- C10：maximum 1 final scope-internal semantic correction cycle。

If C09 or C10 requires another semantic correction cycle after this RF01 implementation attempt：

STOP / REAUTHORIZATION。

Finite tooling retries remain allowed and do not consume semantic budget。

---

## 18. Side-Effect Envelope

DENY：

- migration execution。
- actual PostgreSQL。
- V07。
- broker network。
- paper broker。
- Shioaji simulation。
- production broker。
- real refresh / list_trades。
- real callback registration。
- credentials。
- V01～V05 verification。
- production activation。
- manual unresolved attempt override。
- quantity-modification recovery。
- C12/C13/C14/C15。
- next Wave。

Tests use fake/mock/in-memory evidence only。

---

## 19. Git Policy

After all RF01 tests / full regression / diff / scope checks pass：

one RF01 correction commit is allowed。

Suggested commit：

`fix(recovery): enforce W3 fence and reconstruction invariants`

Before push：

    git fetch origin master

`origin/master` MUST still equal the RF01 authorization commit created from this amendment。

If remote diverges：

STOP。

No：

- rebase。
- merge。
- force push。
- history rewrite。

After successful push：

STOP。

---

## 20. Completion Boundary

After RF01 correction push：

DO NOT：

- mark W3 accepted/closed。
- credit W3 weight 15。
- modify reviewer closure docs。
- start W4。
- execute migration 0007。
- access actual PostgreSQL。
- perform broker I/O。
- run V01～V05。

Return RF01 evidence to reviewer。

---

## 21. Current Governance

W2：

CLOSED / ACCEPTED。

W3：

HOLD / RF01_REQUIRED。

C07：

PASS。

C09：

HOLD / RF01_REQUIRED。

C10：

HOLD / RF01_REQUIRED。

Accepted correction-core progress：

60 / 113。

Remaining：

53。

Runtime Source Modification Authorization：

BOUNDED_AUTHORIZED_FOR_GAP08_W3_RF01。

Canonical Runtime Authorization：

NOT_AUTHORIZED。

Production Activation：

NOT_AUTHORIZED。