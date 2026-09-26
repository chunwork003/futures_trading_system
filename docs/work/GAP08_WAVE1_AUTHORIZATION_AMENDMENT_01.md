# GAP-08 Wave-1 — Authorization Amendment 01

## 1. Status

Wave：

`GAP08-W1-ACCOUNT-AUTHORITY`

Original Execution Baseline：

`c26cdcb7d94636524943f63d66cb03e1d4e66838`

First-pass Runtime HEAD：

`29479837227310d6ff3287dee37171ab3286990c`

First-pass leaf commits：

- C02：`609891b195a3c74bc1450524ad280daad1050b24`
- C04：`46889ff673dfae1ca43946eba2ec7c1299a46256`
- C21：`25bc4efb55af92da70f52f5ff09a240cf3fb8bf2`
- C03：`29479837227310d6ff3287dee37171ab3286990c`

Reviewer result：

`REVIEW_CORRECTION_REQUIRED`

W1 is NOT closed / accepted yet。

Correction-core accepted / verified progress remains：

27 / 113。

The W1 weight 19 remains candidate only。

---

## 2. Reviewer Findings

### RF01 — Reserved Revision-0 Head Bootstrap Missing

Classification：

BLOCKING IMPLEMENTATION CORRECTION。

Primary leaf：

C02。

Affected downstream leaf：

C03。

Current PostgreSQL adapter supports exact head SELECT ... FOR UPDATE and contiguous UPDATE，but does not provide an atomic reserved revision-0 head creation path。

Required correction：

- transaction-scoped atomic reserved-head bootstrap / lock。
- acceptable semantic form：`INSERT ... ON CONFLICT DO NOTHING` followed by exact `SELECT ... FOR UPDATE`，or equivalent concurrency-safe semantics。
- no repository-owned commit。
- no check-then-unconditional-write TOCTOU。
- generic non-initialization revision-zero commit MUST NOT create the head。
- first logical material authority revision remains 1。
- no broker I/O。
- no migration execution。

Migration 0005 is READ-ONLY during this correction。

### RF02 — Duplicate Receipt Replay Does Not Resolve Durable Checkpoint Closure

Classification：

BLOCKING IMPLEMENTATION CORRECTION。

Primary leaf：

C04。

Before returning an existing receipt as successful idempotent replay：

- resolve the exact checkpoint by broker/account/revision。
- checkpoint must exist。
- checkpoint authority_commit_id must equal receipt authority_commit_id。
- checkpoint expected_snapshot_id must equal receipt expected_snapshot_id。
- account/revision scope must match exactly。
- durable head must not be behind the receipt revision。
- missing/inconsistent closure must fail closed。
- current head MAY be ahead of the historical receipt revision。
- no duplicate material effect may occur。

---

## 3. Correction Authorization

Runtime Source Modification Authorization：

`BOUNDED_AUTHORIZED_FOR_GAP08_W1_REVIEW_CORRECTION_01`

Canonical Runtime Authorization：

`NOT_AUTHORIZED`

Production Activation：

`NOT_AUTHORIZED`

This amendment becomes effective only after this docs commit is pushed to `origin/master`。

The resulting docs commit becomes the exact reviewer-correction execution baseline。

---

## 4. Authorized Runtime Scope

Existing runtime files：

- `persistence/account_authority.py`
- `persistence/postgres/account_authority.py`

Existing test files：

- `tests/unit/test_c02_account_authority.py`
- `tests/unit/test_c04_account_authority_commit.py`
- `tests/unit/test_c03_expected_state_initialization.py`

No other runtime or test file may change。

No new test file is authorized。

---

## 5. Protected Scope

READ-ONLY：

- migrations 0001～0005。
- `trading/authorization.py`。
- every runtime file outside the two authorized runtime files。
- every test outside the three authorized test files。
- governance docs during CODEX correction。
- `data/`。

Migration modification / creation / execution：

DENY。

Actual PostgreSQL / V07：

DENY。

Broker I/O：

DENY。

Credential material：

DENY。

Production activation：

DENY。

---

## 6. Correction Accounting

RF01：

C02 semantic correction cycle 1。

RF02：

C04 semantic correction cycle 1。

Existing first-pass C03 semantic correction count：

1。

If C03 runtime semantics require another bounded correction：

that becomes C03 semantic correction cycle 2。

Any leaf exceeding 2 semantic correction cycles：

STOP / REVIEW。

---

## 7. Required Verification

Targeted：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c02_account_authority.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_c03_expected_state_initialization.py `
        tests/unit/test_expected_state_authority.py `
        tests/unit/test_operational_postgres.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Then：

    git diff --check

Required negative evidence：

- absent PostgreSQL authority head has a concurrency-safe reserved-rev0 bootstrap path for explicit initialization。
- generic revision-zero authority commit still fails。
- competing initialization cannot create two logical revision-1 states。
- exact duplicate receipt requires durable checkpoint closure。
- missing checkpoint fails closed。
- mismatched checkpoint fails closed。
- later head revision does not invalidate an older exact receipt/checkpoint pair。
- no repository-owned commit。
- migrations 0001～0005 unchanged。
- no actual PostgreSQL access。
- no broker I/O。

---

## 8. Git Policy

One bounded reviewer-correction commit：

ALLOW。

Push：

ALLOW after targeted + full regression + exact scope PASS。

Force push：

DENY。

Before push：

fetch origin/master and verify remote still equals correction execution baseline。

Unexpected remote divergence：

STOP。

---

## 9. W2

W2：

NOT_AUTHORIZED。

---

## 10. Efficiency Evidence

User-reported first-pass：

- model：GPT-5.6 Sol / light effort。
- 5-hour quota consumption：33%。
- candidate W1 weight：19。
- candidate first-pass throughput：約 0.576 weight / 1% quota。
- average first-pass quota per leaf：約 8.25%。

Because W1 is not reviewer-accepted yet：

accepted W1 weight remains 0 until correction + closure。

---

## 11. STOP Boundary

After correction commit/push/report：

STOP。

Do NOT：

- update governance closure docs。
- credit W1 weight。
- start W2。
- execute migration。
- access actual PostgreSQL。
- perform broker I/O。

Reviewer performs final W1 acceptance/closure separately。
