# GAP-08 Wave-2 — Runtime Source Modification Authorization

## 1. Authorization Status

Wave ID：

`GAP08-W2-EXECUTION-SAFETY`

Authorization Decision Baseline：

`97e7545765741c2e08a02fd4c754b6b5ec1195b4`

Execution package：

`docs/work/GAP08_WAVE2_EXECUTION_PACKAGE.md`

Detailed workflow owner：

`docs/CODEX_EXECUTION_WORKFLOW.md`

Runtime Source Modification Authorization：

`BOUNDED_AUTHORIZED_FOR_GAP08_W2`

Canonical Runtime Authorization：

`NOT_AUTHORIZED`

Production Activation：

`NOT_AUTHORIZED`

This authorization becomes effective only after the commit containing this document is successfully pushed to `origin/master`。

The resulting authorization commit is the exact W2 Execution Baseline。

Source modification authorization does not grant broker invocation、runtime activation or production operation authority。

---

## 2. Authorized Leaves

Exact Wave leaf set：

    C08
        -> C05
        -> C06

Authorized Leaves：

- C08 — Broker Client Correlation Identity。
- C05 — Durable Initial PENDING + Causal Execution Boundary。
- C06 — BrokerActionAttempt / Resolution / No-Blind-Retry。

Weight：

14。

All three leaves are pre-authorized for bounded source modification only under this exact Wave。

No new leaf may be inserted。

No authorized leaf may silently absorb another correction leaf。

Leaf-local completion does not equal reviewer final acceptance。

---

## 3. Automatic Progression

CODEX may automatically progress：

    C08
        -> C05
        -> C06

only while all leaf-local completion gates remain satisfied。

Before each next leaf：

- current leaf targeted tests PASS。
- full regression PASS。
- `git diff --check` PASS。
- exact authorized scope PASS。
- leaf commit completed。
- current Working HEAD refreshed。
- next dependency remains valid。
- canonical authority remains unchanged。
- side-effect envelope remains unchanged。
- no new architecture/business decision is required。

Any contradiction triggers STOP。

---

## 4. Authorized Existing Runtime Files

CODEX may modify only when required by the frozen W2 contract：

- `trading/execution.py`
- `persistence/execution.py`
- `persistence/postgres/execution.py`

No other existing runtime file is authorized for modification。

---

## 5. Authorized New Runtime Files

CODEX may create exactly：

- `persistence/broker_action.py`
- `persistence/postgres/broker_action.py`
- `persistence/postgres/migrations/0006_broker_action_safety.sql`

No additional runtime or migration file may be created without reauthorization。

---

## 6. Authorized Existing Test Files

CODEX may modify only：

- `tests/unit/test_operational_execution.py`
- `tests/unit/test_operational_postgres.py`

Only direct W2 compatibility changes are allowed。

---

## 7. Authorized New Test Files

CODEX may create exactly：

- `tests/unit/test_c08_broker_client_order_ref.py`
- `tests/unit/test_c05_durable_pending_submission.py`
- `tests/unit/test_c06_broker_action_safety.py`

No additional test file may be created without reauthorization。

---

## 8. Protected Runtime Surfaces

READ-ONLY：

- `persistence/account_authority.py`
- `persistence/postgres/account_authority.py`
- `trading/authorization.py`
- `persistence/contracts.py`
- `persistence/events.py`
- `persistence/postgres/event_ledger.py`
- `persistence/postgres/uow.py`
- `persistence/postgres/migrations.py`
- `persistence/strategy_state.py`
- `persistence/postgres/strategy_state.py`
- C23/C24/C25 market-observation modules。
- recovery / reconciliation modules。
- broker discovery modules。
- broker adapters。
- `backtest/shioaji_broker.py`
- `backtest/shioaji_mapping.py`
- `backtest/models.py`
- unrelated backtest / strategy / data modules。
- `data/`。

If any protected runtime surface must change：

STOP / REAUTHORIZATION。

---

## 9. Historical Migration Protection

READ-ONLY：

- 0001。
- 0002。
- 0003。
- 0004。
- 0005。

Creation authorized：

`0006_broker_action_safety.sql`

Migration execution：

DENY。

Backfill：

DENY。

Historical migration rewrite：

DENY。

Drop / destructive migration：

DENY。

---

## 10. Side-Effect Envelope

    Source Modification:
        ALLOW
        exact W2 scope only

    Test Execution:
        ALLOW

    Migration Creation:
        ALLOW
        0006 only

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

    Shioaji Simulation I/O:
        DENY

    Production Broker I/O:
        DENY

    Credential Material:
        DENY

    Production Activation:
        DENY

    Canonical Runtime Authorization:
        NOT_AUTHORIZED

Core invariant：

    Runtime Source Modification Authorization
    !=
    Runtime Authorization
    !=
    Production Activation

---

## 11. Broker Capability Boundary

Shioaji `custom_field` remains only the leading broker-native carrier candidate for `broker_client_order_ref`。

W2 MUST NOT claim：

- production custom_field round-trip verified。
- server-side idempotency。
- restart-stable Shioaji correlation capability。
- production broker capability completion。

Broker-neutral C08/C05/C06 implementation may proceed using fake/mock broker invocation ports only。

Concrete Shioaji carrier verification remains a separate capability gate。

Production submission remains default-deny until that capability is independently verified。

---

## 12. C08 Acceptance

C08 must establish：

- canonical operational `trading.execution.Order` owns `broker_client_order_ref`。
- client ref is distinct from broker-assigned `broker_order_id`。
- durable sequence-0 PENDING has a nonblank immutable client ref。
- same canonical Order reuses the same ref。
- later projection updates cannot silently replace it。
- retry/recovery never creates a replacement correlation identity。
- attribute/time-window heuristic is not identity authority。

C08 must NOT modify Shioaji broker/mapping adapters。

---

## 13. C05 Acceptance

C05 must establish the broker-bound durable initial boundary：

    material strategy causal evidence where applicable
        +
    sequence-0 PENDING OrderEvent
        +
    canonical Order projection
        +
    broker_client_order_ref
        +
    exact expected-state checkpoint reference
        +
    AccountAuthorityCommit closure

in one crash-consistent authority transaction where applicable。

Required ordering：

    durable PENDING authority commit
        ->
    DB transaction fully closed
        ->
    C06 durable action-attempt commit
        ->
    DB transaction fully closed
        ->
    broker invocation

Broker network I/O while authority DB lock/UoW remains active：

FORBIDDEN。

Best-effort dual write：

FORBIDDEN。

Strategy-state persistence modules remain READ-ONLY unless reauthorized。

---

## 14. C06 Acceptance

C06 must establish durable broker-neutral：

- BrokerActionAttempt。
- BrokerActionResolution。
- BrokerActionHead or equivalent durable concurrency projection。

V1 action kinds：

- SUBMIT。
- CANCEL。

Requirements：

- attempt durable before material broker invocation。
- attempt commit advances BrokerAccount authority revision through shared AccountAuthorityCommit semantics。
- unresolved attempt blocks automatic second invocation。
- zero exact broker match is not retry authority。
- timeout / disconnect / lost response after dispatch start remains outcome unknown。
- durable NOT_DISPATCHED may restore eligibility only with positive verified pre-transport proof。
- concurrency safety is database-enforced。
- check-then-write TOCTOU is forbidden。
- broker client correlation identity is not server-side idempotency authority。
- SUBMIT and CANCEL share no-blind-retry semantics。

Manual unresolved-attempt release/override remains outside W2 and default-deny without separate authority。

---

## 15. C08 Test Policy

Required targeted suite：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c08_broker_client_order_ref.py `
        tests/unit/test_operational_execution.py `
        tests/unit/test_operational_postgres.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Only after PASS：

C08 leaf-local commit allowed。

---

## 16. C05 Test Policy

Required targeted suite：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c05_durable_pending_submission.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_operational_execution.py `
        tests/unit/test_c25_market_observation_delivery.py `
        tests/unit/test_strategy_state_recovery.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Only after PASS：

C05 leaf-local commit allowed。

---

## 17. C06 Test Policy

Required targeted suite：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c06_broker_action_safety.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_c21_authorization_seam.py `
        tests/unit/test_operational_execution.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Only after PASS：

C06 leaf-local commit allowed。

---

## 18. Wave Final Verification

Required：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c08_broker_client_order_ref.py `
        tests/unit/test_c05_durable_pending_submission.py `
        tests/unit/test_c06_broker_action_safety.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_c21_authorization_seam.py `
        tests/unit/test_operational_execution.py `
        tests/unit/test_operational_postgres.py `
        tests/unit/test_c25_market_observation_delivery.py `
        tests/unit/test_strategy_state_recovery.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Then：

    git diff --check

No actual PostgreSQL or broker environment verification is authorized by this Wave。

---

## 19. Semantic Correction Budget

Per leaf：

maximum 2 scope-internal semantic correction cycles。

Tooling retry does NOT consume semantic correction budget。

Tooling retry remains finite。

Repeated same-class tooling failure requires：

root-cause inspection -> corrected approach -> reclassification / STOP if unresolved。

AUTHORITY / REVISION CONTRADICTION：

STOP。

---

## 20. Code Documentation Requirements

Important new module / class / public function / public contract must use Traditional Chinese comment/docstring describing applicable：

- 用途。
- 責任。
- upstream / data source。
- downstream consumer。
- important invariant。
- non-obvious business/broker rule。
- explicit non-responsibility。

Do not add low-value name-translation comments。

---

## 21. Git Policy

    git_commit:
        ALLOW
        per_leaf

    git_push:
        ALLOW
        wave_end

    force_push:
        DENY

Expected local commit sequence：

    C08
        -> C05
        -> C06

No intermediate push is required or authorized by default。

Before wave-end push：

    git fetch origin master

Expected `origin/master`：

the exact W2 Execution Baseline created by this authorization commit。

Unexpected remote divergence：

STOP。

Forbidden：

- force push。
- arbitrary rebase through unknown remote work。
- unrelated merge。
- public-history rewrite。
- `data/` staging。

---

## 22. CODEX Start Contract

At CODEX start：

    HEAD
    ==
    origin/master
    ==
    W2 authorization commit

except known `data/` state。

CODEX must read at minimum：

- `AGENTS.md`
- `docs/CURRENT_STATE.md`
- `docs/CODEX_EXECUTION_WORKFLOW.md`
- `docs/work/GAP08_WAVE2_EXECUTION_PACKAGE.md`
- `docs/work/GAP08_WAVE2_AUTHORIZATION.md`
- `docs/work/GAP08_CORRECTION_FREEZE.md`

First executable leaf：

`C08`

Execution Mode：

`LEVEL_3A_BOUNDED`

Model recommendation：

`GPT-5.6 Sol`

Wave context model：

Wave Shared Context + Leaf Delta Context。

---

## 23. Reviewer / Reauthorization Barrier

STOP / reauthorization if：

- write scope expansion is required。
- protected file modification is required。
- new runtime/test/migration file outside exact list is required。
- migration execution becomes necessary。
- actual PostgreSQL becomes necessary。
- broker/network/paper/simulation/production I/O becomes necessary。
- credential/security boundary changes。
- Shioaji carrier semantics must be assumed rather than verified。
- server-side idempotency must be assumed。
- strategy-state module modification becomes necessary。
- manual unresolved-attempt release semantics are required。
- C07/C09/C10 or another leaf is required to finish W2。
- canonical Runtime Authorization semantics would change。
- new architecture/business decision is required。
- semantic correction budget is exceeded。
- unrelated core regression occurs。
- remote divergence occurs。

---

## 24. W2 Completion Boundary

After C06 leaf-local completion、Wave final verification and wave-end push：

STOP。

CODEX must NOT：

- update reviewer acceptance/closure status。
- credit W2 weight 14 as accepted。
- mark GAP-08 closed。
- start W3。
- execute migration 0006。
- access actual PostgreSQL。
- perform broker I/O。
- activate runtime or production。

Reviewer/governance closure occurs separately。

---

## 25. Current Authority

Runtime Source Modification Authorization：

`BOUNDED_AUTHORIZED_FOR_GAP08_W2`

Canonical Runtime Authorization：

`NOT_AUTHORIZED`

Production Activation：

`NOT_AUTHORIZED`

CODEX engineering execution：

AUTHORIZED FOR W2 SOURCE MODIFICATION ONLY。

First leaf：

C08。

No other Wave is authorized。