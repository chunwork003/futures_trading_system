# GAP-08 Wave-1 — Runtime Source Modification Authorization

## 1. Authorization Status

Wave ID：

`GAP08-W1-ACCOUNT-AUTHORITY`

Authorization Decision Baseline：

`a6a90dc7cf47c0b7eeb9520be2e38db823ff579c`

Execution package：

`docs/work/GAP08_WAVE1_EXECUTION_PACKAGE.md`

Detailed workflow owner：

`docs/CODEX_EXECUTION_WORKFLOW.md`

Runtime Source Modification Authorization：

`BOUNDED_AUTHORIZED_FOR_GAP08_W1`

Runtime Authorization：

`NOT_AUTHORIZED`

Production Activation：

`NOT_AUTHORIZED`

This authorization becomes effective only after the commit containing this document is successfully pushed to `origin/master`。

The resulting authorization commit is the exact W1 Execution Baseline。

---

## 2. Authorized Leaves

Exact Wave leaf set：

    C02
        -> C04
        -> C21
        -> C03

Authorized Leaves：

- C02 — BrokerAccount Revision Head + Exact Checkpoint。
- C04 — Shared AccountAuthorityCommit Primitive。
- C21 — Protected Action Authorization Enforcement Seam。
- C03 — Expected-State Initialization Authority。

Weight：

19。

C21 depends architecturally on V06 independently。

`C04 -> C21`

is single-agent serialization only。

It MUST NOT be treated as a new architecture dependency。

---

## 3. Automatic Progression

All four leaves are pre-authorized for bounded source modification。

CODEX may automatically progress：

    C02
    -> C04
    -> C21
    -> C03

only while all leaf-local completion gates remain satisfied。

No new leaf may be inserted。

No authorized leaf may silently absorb another correction leaf。

Leaf-local completion does NOT equal final reviewer acceptance。

---

## 4. Authorized Existing Runtime Files

CODEX may modify only when required by the frozen W1 contract：

- `persistence/account.py`
- `persistence/postgres/account.py`
- `persistence/execution.py`
- `persistence/postgres/execution.py`

No other existing runtime file is authorized for modification。

---

## 5. Authorized New Runtime Files

CODEX may create exactly：

- `persistence/account_authority.py`
- `persistence/postgres/account_authority.py`
- `trading/authorization.py`
- `persistence/postgres/migrations/0005_account_authority.sql`

No additional runtime/migration file may be created without reauthorization。

---

## 6. Authorized Existing Test Files

CODEX may modify only：

- `tests/unit/test_operational_execution.py`
- `tests/unit/test_operational_postgres.py`

Only W1 compatibility changes are allowed。

---

## 7. Authorized New Test Files

CODEX may create exactly：

- `tests/unit/test_c02_account_authority.py`
- `tests/unit/test_c04_account_authority_commit.py`
- `tests/unit/test_c21_authorization_seam.py`
- `tests/unit/test_c03_expected_state_initialization.py`

No additional test-file creation is authorized。

---

## 8. Protected Runtime Surfaces

The following remain read-only：

- `persistence/contracts.py`
- `persistence/events.py`
- `persistence/postgres/event_ledger.py`
- `persistence/postgres/uow.py`
- `persistence/postgres/migrations.py`
- `trading/account.py`
- `trading/execution.py`
- `persistence/recovery.py`
- strategy-state persistence。
- C23/C24/C25 market-observation modules。
- broker adapters。
- reconciliation domain/persistence。
- unrelated backtest/strategy/data modules。
- `data/`。

If any protected runtime surface must change：

STOP / REAUTHORIZATION。

---

## 9. Historical Migration Protection

Protected：

- 0001。
- 0002。
- 0003。
- 0004。

Creation authorized：

`0005_account_authority.sql`

Migration execution：

DENY。

Backfill：

DENY。

Historical migration rewrite：

DENY。

Drop/destructive migration：

DENY。

---

## 10. Side-Effect Envelope

    Source Modification:
        ALLOW
        exact W1 scope only

    Test Execution:
        ALLOW

    Migration Creation:
        ALLOW
        0005 only

    Migration Execution:
        DENY

    Actual PostgreSQL Environment Access:
        DENY

    V07:
        DENY

    Broker Network:
        DENY

    Paper Broker I/O:
        DENY

    Production Broker I/O:
        DENY

    Credential Material:
        DENY

    Production Activation:
        DENY

    Runtime Authorization:
        NOT_AUTHORIZED

Core invariant：

    source modification authorization
    !=
    runtime activation / operation authorization

---

## 11. Rewrite Policy

C02：

ALLOWED。

C04：

PREFERRED。

C21：

EXTEND。

C03：

ALLOWED。

Bounded rewrite means：

smallest coherent delta satisfying frozen contract。

It does NOT mean minimum LOC。

Architecture redesign remains forbidden。

---

## 12. C02 Acceptance

C02 must establish：

- BrokerAccount contiguous account revision。
- exactly one checkpoint per successful material revision。
- exact `expected_snapshot_id` checkpoint reference。
- stable receipt semantics。
- no revision gap。
- no latest-snapshot substitution。
- fail-closed exact-reference integrity semantics。

C02 must NOT initialize expected state。

---

## 13. C04 Acceptance

C04 must establish one shared AccountAuthorityCommit primitive。

One successful material authority commit must produce：

- exactly one account revision。
- exactly one exact checkpoint。
- exactly one stable commit receipt。

Where applicable the same UoW includes：

- event。
- fills。
- order projection。
- expected snapshot。
- authorization attribution。
- future typed transaction participant extension seam。

Repository-owned commit/rollback remains forbidden。

Broker I/O inside authority transaction remains forbidden。

---

## 14. C21 Acceptance

C21 must establish the authoritative core authorization-required enforcement seam。

It must：

- fail closed when trusted production authority is unavailable。
- distinguish trusted production authority from test/sandbox authority。
- reject metadata-only approval as production authorization。
- bind exact protected action/world where required。
- provide durable attribution-compatible evidence/reference。
- preserve authorization as necessary but never sufficient。

C21 must NOT implement full Python IAM / RBAC / OIDC / approval UI。

---

## 15. C03 Acceptance

C03 must implement explicit：

`EXPECTED_STATE_INITIALIZED`

Modes：

- FLAT。
- BROKER_SEED。

Successful initialization establishes：

`account_revision = 1`

and atomically closes：

- initialization TradingEvent。
- complete expected snapshot。
- AccountStateHead revision 1。
- AccountRecoveryCheckpoint revision 1。
- exact expected snapshot reference。
- stable authority receipt。
- required immutable broker-observation evidence already supplied to the operation。
- exact authorization attribution where required。

Initialization must NOT imply READY。

Production broker/currentness authority unavailable：

fail closed。

No broker I/O is authorized inside W1。

---

## 16. Test Policy — C02

Required：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c02_account_authority.py `
        tests/unit/test_expected_state_authority.py `
        tests/unit/test_operational_postgres.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Only after PASS：

C02 leaf-local commit allowed。

---

## 17. Test Policy — C04

Required：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_operational_execution.py `
        tests/unit/test_event_ledger.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Only after PASS：

C04 leaf-local commit allowed。

---

## 18. Test Policy — C21

Required：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c21_authorization_seam.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Only after PASS：

C21 leaf-local commit allowed。

---

## 19. Test Policy — C03

Required：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c03_expected_state_initialization.py `
        tests/unit/test_c02_account_authority.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_c21_authorization_seam.py `
        tests/unit/test_expected_state_authority.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Only after PASS：

C03 leaf-local commit allowed。

---

## 20. Semantic Correction Budget

Per leaf：

maximum 2 scope-internal semantic correction cycles。

A correction cycle begins only after an implementation/test failure reveals a semantic/code defect。

Tooling retry does NOT consume semantic correction budget。

Tooling retry is not unbounded。

Repeated same-class tooling failure requires：

root-cause inspection -> corrected approach -> reclassification / STOP if unresolved。

---

## 21. Failure Classes

CODEX must classify failures as：

- TOOLING RETRY。
- IMPLEMENTATION CORRECTION。
- EXTERNAL / ENVIRONMENT FAILURE。
- AUTHORITY / REVISION CONTRADICTION。

AUTHORITY / REVISION CONTRADICTION：

STOP。

---

## 22. Git Policy

    git_commit:
        ALLOW
        per_leaf

    git_push:
        ALLOW
        wave_end

    force_push:
        DENY

Expected local commit sequence：

    C02
    -> C04
    -> C21
    -> C03

No intermediate push is required or authorized by default。

The authorization commit on `origin/master` remains the expected remote base during local Wave execution。

---

## 23. Remote Divergence

At Wave start：

confirm `origin/master` equals W1 Execution Baseline。

Before wave-end push：

    git fetch origin master

If origin/master changed unexpectedly：

STOP。

Forbidden：

- force push。
- arbitrary rebase。
- unrelated merge。
- public-history rewrite。

---

## 24. Wave Shared Context

Resolve once：

- this authorization。
- W1 execution package。
- CODEX workflow。
- frozen W1 contracts。
- exact write/protected scope。
- side-effect envelope。
- test policy。
- Git policy。
- STOP conditions。

Do not reread the complete architecture corpus for every leaf。

---

## 25. Leaf Delta Context

After each leaf commit refresh only：

- current Working HEAD。
- leaf contract。
- changed files/symbols。
- changed READ_SET。
- failing/new evidence。
- required tests。
- correction count。
- next dependency state。

---

## 26. Leaf-Local Completion Gate

Before moving to next leaf：

- targeted tests PASS。
- full regression PASS。
- `git diff --check` PASS。
- exact scope PASS。
- no protected file change。
- no unauthorized side effect。
- correction budget within limit。
- local leaf commit complete。
- Working HEAD refreshed。
- next dependency remains satisfied。

Failure:

STOP or bounded correction according to classification。

---

## 27. Mandatory STOP / Reauthorization

STOP immediately if：

- a file outside authorized write scope must change。
- a fifth leaf is required。
- 0001～0004 must change。
- migration execution is required。
- actual PostgreSQL is required。
- broker/network I/O is required。
- credential access is required。
- production policy must be invented。
- full IAM implementation becomes required。
- C03 would imply READY。
- canonical Runtime Authorization would need semantic change。
- protected runtime surface must change。
- semantic correction budget exceeds 2 for any leaf。
- architecture/business ambiguity appears。
- current leaf invalidates next dependency。
- unexpected remote divergence exists。

---

## 28. Wave Completion Requirements

After C03 passes and is locally committed：

run final：

    .\.venv\Scripts\python.exe -m pytest -q

Then：

- verify exact cumulative W1 scope。
- verify migrations 0001～0004 unchanged。
- verify 0005 created but NOT executed。
- verify no actual PostgreSQL access。
- verify no broker I/O。
- verify Runtime Authorization remains NOT_AUTHORIZED。
- verify all four local commits exist in expected ancestry。
- fetch origin/master。
- verify remote still equals W1 Execution Baseline。
- push local Wave commits once。
- verify origin/master equals final W1 runtime HEAD。
- final report。
- STOP。

No automatic W2 execution is authorized。

---

## 29. Efficiency Evidence

When available，final W1 report should record：

- model/CODEX consumption %。
- accepted engineering weight candidate = 19。
- files read。
- files changed。
- tool operations。
- tooling retries。
- semantic correction cycles by leaf。
- human intervention count。
- targeted/full-regression counts。
- scope violations。
- stale-context incidents。
- elapsed time。

No fixed productivity quota is imposed。

---

## 30. Explicit Non-Authorization

This authorization does NOT authorize：

- C05。
- C06。
- C07。
- C08。
- C09。
- C10。
- C12～C20 except C21。
- C22～C25 rework。
- W2～W5 execution。
- V01～V05 verification。
- V07。
- actual PostgreSQL。
- migration execution。
- broker I/O。
- production activation。
- LIVE trading。
- credentials。
- unrelated refactor。

---

## 31. Effective Execution Baseline

The exact Git commit that introduces this authorization and is successfully pushed to `origin/master` is the effective W1 Execution Baseline。

CODEX must resolve and verify that commit before touching source。

At CODEX start：

    HEAD
    ==
    origin/master
    ==
    authorization commit

except known untracked `data/`。

---

## 32. Current Authority After P5

Runtime Source Modification Authorization：

`BOUNDED_AUTHORIZED_FOR_GAP08_W1`

Runtime Authorization：

`NOT_AUTHORIZED`

Production Activation：

`NOT_AUTHORIZED`

CODEX engineering execution：

AUTHORIZED FOR W1 SOURCE MODIFICATION ONLY。

First leaf：

C02。

No other Wave is authorized。
