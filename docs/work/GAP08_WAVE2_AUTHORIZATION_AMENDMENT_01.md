# GAP-08 Wave-2 — Authorization Amendment 01 — Reviewer Correction RF01

## 1. Status

Wave：

`GAP08-W2-EXECUTION-SAFETY`

Reviewer input baseline：

`ff57c216cf0b3a1d1c894442a4a14b8a210db7f4`

Original W2 authorization：

`docs/work/GAP08_WAVE2_AUTHORIZATION.md`

Amendment：

`GAP08-W2-RF01`

Current Runtime Source Modification Authorization：

`BOUNDED_AUTHORIZED_FOR_GAP08_W2_RF01`

Canonical Runtime Authorization：

`NOT_AUTHORIZED`

Production Activation：

`NOT_AUTHORIZED`

W2 reviewer acceptance：

`HOLD / RF01_REQUIRED`

Accepted correction-core progress remains：

`46 / 113`

W2 weight 14 remains candidate / NOT CREDITED。

---

## 2. Reviewer Finding RF01

ADR-002 R-04G freezes：

- no blind broker-action retry。
- unresolved BrokerActionAttempt forbids automatic re-invocation。
- complete discovery + zero exact match does not override that rule。
- only a durable `NOT_DISPATCHED` BrokerActionResolution with verified pre-transport proof may restore SideEffectSafetyGate eligibility。
- exact broker match forbids resubmission。
- SUBMIT and CANCEL share the same no-blind-retry contract。

W2 candidate `ff57c216...` currently lets `BrokerActionResolutionParticipant` release the action head for all resolution kinds：

- `SUCCEEDED`
- `FAILED`
- `NOT_DISPATCHED`

That makes a resolved SUCCEEDED/FAILED same Order/action scope automatically eligible for another material broker invocation。

This contradicts R-04G。

RF01 is therefore REQUIRED before W2 can be reviewer-accepted。

---

## 3. Required Corrected Semantics

The durable BrokerActionHead or equivalent projection must distinguish：

1. unresolved attempt — automatic re-invocation blocked。
2. resolved material outcome (`SUCCEEDED` / `FAILED`) — no longer unresolved, but automatic re-invocation remains blocked。
3. verified `NOT_DISPATCHED` — resolved and invocation eligibility may be restored。
4. no attempt yet — first invocation may be eligible subject to all other gates。

Only state 3 may restore same Order/action automatic invocation eligibility after an attempt exists。

Do NOT keep a resolved SUCCEEDED/FAILED attempt falsely labelled "unresolved" merely to block retry。

The physical schema/enum representation is implementation-owned, but the semantic distinction must be durable and database-enforced。

---

## 4. Authorized Existing Runtime Files

RF01 may modify only：

- `persistence/broker_action.py`
- `persistence/postgres/broker_action.py`
- `persistence/postgres/migrations/0006_broker_action_safety.sql`

C08 and C05 runtime files are READ-ONLY under RF01。

---

## 5. Authorized Test Files

RF01 may modify only：

- `tests/unit/test_c06_broker_action_safety.py`
- `tests/unit/test_operational_postgres.py`

No other test file may change。

---

## 6. Migration Rule

Migration 0006：

AUTHORIZED TO AMEND IN A NEW GIT COMMIT because it has never been executed。

This is NOT a public-history rewrite。

Migrations 0001～0005：

READ-ONLY。

Migration execution：

DENY。

New migration 0007：

DENY / NOT REQUIRED。

Backfill：

DENY。

Actual PostgreSQL：

DENY。

---

## 7. Required DB / Repository Semantics

Database-enforced transition must ensure：

- first reservation atomically blocks concurrent invocation。
- unresolved attempt remains blocked。
- SUCCEEDED resolution records durable resolution and clears unresolved classification without restoring invocation eligibility。
- FAILED resolution records durable resolution and clears unresolved classification without restoring invocation eligibility。
- verified NOT_DISPATCHED resolution may atomically restore invocation eligibility。
- a new attempt after verified NOT_DISPATCHED must atomically consume that eligibility and block concurrent invocation again。
- no check-then-write TOCTOU。
- no process-memory-only authority。

Equivalent schema is allowed；field names are not prescribed。

---

## 8. Required Negative Tests

At minimum add/adjust tests proving：

- SUBMIT + SUCCEEDED -> second SUBMIT automatic invocation denied。
- SUBMIT + FAILED -> second SUBMIT automatic invocation denied。
- CANCEL + SUCCEEDED -> second CANCEL automatic invocation denied。
- CANCEL + FAILED -> second CANCEL automatic invocation denied。
- unresolved SUBMIT/CANCEL -> second invocation denied。
- NOT_DISPATCHED without verified pre-transport proof -> rejected。
- verified NOT_DISPATCHED -> later same Order/action invocation may proceed。
- broker_client_order_ref remains correlation only，not idempotency authority。
- no manual force retry/release path is introduced。
- PostgreSQL repository conditional-write semantics encode the same eligibility rule。
- repositories still never commit/rollback independently。

---

## 9. Targeted Verification

Run：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c06_broker_action_safety.py `
        tests/unit/test_operational_postgres.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_c21_authorization_seam.py `
        tests/unit/test_operational_execution.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Then：

    git diff --check

Then exact RF01 scope validation。

---

## 10. Side-Effect Envelope

ALLOW：

- exact RF01 source modification。
- unit/full test execution。
- amend unexecuted 0006 source file。

DENY：

- migration execution。
- actual PostgreSQL。
- V07。
- broker network。
- paper broker I/O。
- Shioaji simulation I/O。
- production broker I/O。
- credentials。
- production activation。
- Shioaji adapter modification。
- C07/C09/C10 implementation。
- manual unresolved-attempt override implementation。

---

## 11. Git Policy

One bounded reviewer-correction commit is allowed after all RF01 gates pass。

Suggested commit：

`fix(execution): enforce no-reinvoke after broker action resolution`

Push：

ALLOW after correction verification。

Force push：

DENY。

Before push：

    git fetch origin master

`origin/master` must still equal the RF01 authorization commit produced by this Amendment materialization。

Unexpected divergence：

STOP。

---

## 12. Correction Budget

RF01 reviewer correction：

maximum 1 semantic correction cycle。

Tooling retry does not consume semantic correction budget but remains finite。

Any need to modify outside exact RF01 scope：

STOP / REAUTHORIZATION。

Any architecture contradiction：

STOP。

---

## 13. Completion Boundary

After RF01 implementation、targeted tests、full regression、scope check、commit and push：

STOP。

Do NOT：

- mark W2 accepted。
- credit W2 weight。
- update closure docs。
- start W3。
- execute migration 0006。
- access actual PostgreSQL。
- perform broker I/O。

Return final RF01 evidence to reviewer。

Reviewer then decides W2 acceptance/closure separately。