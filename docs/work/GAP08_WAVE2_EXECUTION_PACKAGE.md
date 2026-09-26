# GAP-08 Wave-2 — Execution Safety Execution Package

## 1. Status

Wave ID：

`GAP08-W2-EXECUTION-SAFETY`

Planning Baseline：

`6a444f6a7ed2a586fe8b3f93632e87e25447cb96`

Package type：

EXECUTION COHERENCE / AUTHORIZATION INPUT。

Dependency DAG：

VERIFIED。

Execution Coherence：

VERIFIED FOR A LATER BOUNDED SOURCE-MODIFICATION AUTHORIZATION DECISION。

Runtime Source Modification Authorization：

NOT_AUTHORIZED。

Runtime Authorization：

NOT_AUTHORIZED。

Production Activation：

NOT_AUTHORIZED。

Wave Execution Authorization：

NOT_AUTHORIZED。

CODEX runtime：

NOT_STARTED。

This package does NOT authorize source modification。

---

## 2. Wave Goal

完成 GAP-08 Submission Safety coherent correction bundle：

- C08 — Broker Client Correlation Identity。
- C05 — Durable Initial PENDING + Causal Execution Boundary。
- C06 — BrokerActionAttempt / Resolution / No-Blind-Retry。

Wave engineering weight：

14。

Current accepted / verified correction-core progress：

46 / 113。

Remaining：

67。

W2 weight remains candidate only until later source execution、verification and reviewer closure。

---

## 3. Dependency DAG

Frozen architecture dependencies：

    V06
        -> C08

    C04 + C08 + C25
        -> C05

    C04 + C05
        -> C06

Current prerequisite state：

- V06：COMPLETE / VERIFIED。
- C04：COMPLETE / VERIFIED / ACCEPTED。
- C25：COMPLETE / VERIFIED。
- C21 authorization enforcement seam：COMPLETE / VERIFIED / ACCEPTED。

Therefore all external W2 entry dependencies are satisfied。

Candidate serialization：

    C08
        -> C05
        -> C06

No additional architecture edge is introduced。

---

## 4. Source Requirements

Relevant official/source-registry evidence：

- `SRC-SINOPAC-FUT-ORDER-001`
- `SRC-SINOPAC-ORDER-STATUS-001`
- `SRC-SINOPAC-ORDER-EVENT-001`
- `SRC-SINOPAC-RELEASE-001`

Last repository-recorded verification：

`2026-09-25`

Change risk：

HIGH。

W2 is intentionally broker-neutral for runtime safety semantics。

Shioaji `custom_field` remains only the leading carrier candidate for
`broker_client_order_ref`。

W2 MUST NOT claim：

- verified production custom_field round-trip。
- server-side idempotency。
- restart-safe Shioaji correlation capability。
- production broker capability completion。

Concrete production Shioaji carrier mapping remains capability-gated and default-deny until separately verified。

---

# C08 — Broker Client Correlation Identity

## 5. Canonical Ownership

Canonical owner：

`trading.execution.Order`

New semantic field：

`broker_client_order_ref`

Rules：

- distinct from `broker_order_id`。
- immutable once sequence-0 PENDING becomes durable。
- nonblank before any broker invocation。
- all SUBMIT attempts for one canonical Order reuse the same durable ref。
- retry/recovery MUST NOT create another ref for the same Order。
- attribute/time-window heuristic matching is never authority。

Transient/in-memory Order construction MAY remain compatibility-tolerant before initial persistence。

Durable sequence-0 PENDING persistence MUST reject missing/blank
`broker_client_order_ref`。

This distinction avoids silently redefining historical test/build surfaces while still enforcing the frozen durable invariant。

---

## 6. C08 Persistence Boundary

The client ref must become durable in the same causal transaction that establishes sequence-0 PENDING。

PostgreSQL representation may use a new structured column while retaining `projection_json` as the complete canonical projection payload。

Historical migrations 0001～0005 MUST NOT be rewritten。

No historical backfill is authorized by W2。

Actual environment migration compatibility remains V07 / later environment evidence。

---

# C05 — Durable Initial PENDING + Causal Boundary

## 7. C05 Initial Durable Boundary

Before broker side effect：

one AccountAuthorityCommit transaction must atomically establish the applicable set of：

- canonical sequence-0 OrderEvent：`None -> PENDING`。
- canonical Order projection。
- immutable `broker_client_order_ref`。
- exact current expected snapshot checkpoint reference。
- material-emitting StrategyStateSnapshot participants where applicable。
- AccountRecoveryCheckpoint。
- AccountStateHead revision advancement。
- AccountAuthorityCommitReceipt。

Failure of any included participant rolls back the entire boundary。

Broker invocation is forbidden before this commit succeeds。

---

## 8. C05 Strategy-State Causal Rule

Where a MarketObservation cycle emits material strategy outputs accepted into a broker-bound decision：

the material-emitting strategy snapshots and sequence-0 PENDING boundary must share one crash-consistent transaction。

HOLD-only strategy snapshots are not pulled into the boundary solely because they were evaluated。

Existing：

- `persistence.strategy_state.StrategyStateRepository`
- `persistence.postgres.strategy_state.PostgresStrategyStateRepository`

remain reusable transaction participants。

They are READ-ONLY under W2 unless concrete implementation evidence later proves a write is unavoidable。

Any required modification to those protected files：

STOP / REAUTHORIZATION。

---

## 9. C05 Transaction / Network Separation

Required ordering：

    durable sequence-0 PENDING authority commit
        ->
    transaction fully committed / DB authority lock released
        ->
    C06 durable BrokerActionAttempt authority commit
        ->
    transaction fully committed / DB authority lock released
        ->
    broker invocation

Broker network I/O while AccountStateHead or other authority DB locks are held：

FORBIDDEN。

Best-effort dual write：

FORBIDDEN。

---

# C06 — BrokerActionAttempt / Resolution / No-Blind-Retry

## 10. C06 Durable Evidence

W2 establishes immutable durable：

- BrokerActionAttempt。
- BrokerActionResolution。

And mutable concurrency projection：

- BrokerActionHead or equivalent。

V1 action kinds：

- SUBMIT。
- CANCEL。

BrokerActionAttempt is not OrderStatus。

BrokerActionResolution is not OrderStatus。

Recovery classifications are not OrderStatus。

---

## 11. Attempt Ordering

Before material broker invocation：

BrokerActionAttempt must be durably committed through the shared AccountAuthorityCommit path。

The attempt commit：

- advances BrokerAccount authority revision。
- carries forward the exact expected snapshot reference when expected position does not change。
- updates/reserves the BrokerActionHead concurrency projection。
- must complete before broker network invocation starts。

No BrokerActionAttempt：

broker invocation is impossible by contract。

Existing unresolved attempt：

automatic re-invocation is forbidden。

---

## 12. No-Blind-Retry

Required frozen behavior：

- unresolved SUBMIT attempt -> DO NOT RESUBMIT。
- unresolved CANCEL attempt -> DO NOT RECANCEL。
- complete broker discovery + zero exact match does NOT by itself authorize another invocation。
- timeout after dispatch start -> outcome unknown。
- connection loss after dispatch start -> outcome unknown。
- lost response -> outcome unknown。
- missing callback -> outcome unknown。
- process crash after attempt commit -> outcome potentially occurred。
- broker correlation ref is NOT server-side idempotency authority。

A durable `NOT_DISPATCHED` resolution may restore first-invocation eligibility only when a verified pre-transport boundary positively proves broker network invocation never began。

W2 must not guess such proof from generic exceptions。

---

## 13. BrokerActionHead Concurrency

At most one unresolved attempt may govern the same BrokerAccount / Order / action scope。

Concurrency safety must be database-enforced。

Forbidden：

- SELECT then unconditional INSERT/UPDATE。
- process-memory mutex as durable authority。
- check-then-write TOCTOU。
- concurrent unresolved attempts for the same protected action scope。

Optimistic version / conditional UPDATE / unique constraint / row-lock equivalent implementation is allowed if it satisfies the frozen invariant。

---

## 14. Resolution Boundary

Known material resolution must be durably applied through AccountAuthorityCommit so action-resolution evidence and any included material canonical execution mutation share one authority transaction。

Unknown outcome remains unresolved。

W2 does NOT invent broker-discovery evidence to resolve unknown outcomes。

Exact broker matching / recovery discovery remains C07+。

Broker report durable inbox / recovery fence remains C09+。

Broker execution reconstruction / Fill economics remains C10+。

---

## 15. Authorization Boundary

C21 remains the existing authorization-required enforcement seam。

W2 MUST NOT implement a new IAM / RBAC / approval system。

Where a protected broker action requires authorization attribution：

the exact authorization reference/evidence must be bound durably to the protected command / attempt before broker side effect。

Normal presence of historical authorization never permits creation of an additional BrokerActionAttempt。

Manual release/retry of unresolved attempts is NOT implemented by W2。

Production manual override remains default-deny unless separately authorized under the existing R-13/C21 contract。

---

# Exact Proposed Source Scope

## 16. Existing Runtime Write Scope

A later W2 source-modification authorization MAY allow only：

- `trading/execution.py`
- `persistence/execution.py`
- `persistence/postgres/execution.py`

Purpose：

### `trading/execution.py`

C08 bounded extension of canonical operational Order with
`broker_client_order_ref` semantics。

### `persistence/execution.py`

C05 bounded transaction-scoped sequence-0 PENDING participant / compatibility refactor so ExecutionPersistenceService logic can participate in caller-owned AccountAuthorityCommit transaction。

It MUST NOT own commit independently when used inside AccountAuthorityCommit。

### `persistence/postgres/execution.py`

Persist/query the structured broker client correlation identity and retain optimistic projection semantics。

No broker I/O belongs here。

---

## 17. New Runtime Files

A later W2 authorization MAY create exactly：

- `persistence/broker_action.py`
- `persistence/postgres/broker_action.py`
- `persistence/postgres/migrations/0006_broker_action_safety.sql`

Ownership：

### `persistence/broker_action.py`

Owns broker-neutral durable action safety contracts：

- BrokerActionAttempt。
- BrokerActionResolution。
- BrokerActionHead。
- repository protocols。
- transaction participants。
- broker-bound submission/action coordinator。
- injected broker invocation port。
- typed dispatch/no-blind-retry result boundary。

It MUST NOT contain Shioaji-native DTO semantics。

### `persistence/postgres/broker_action.py`

PostgreSQL adapters for durable attempts / resolutions / concurrency head。

Repositories MUST NOT own commit/rollback。

### `0006_broker_action_safety.sql`

Non-destructive W2 persistence schema only。

Migration execution remains DENY。

---

## 18. Existing Test Write Scope

A later W2 authorization MAY modify only：

- `tests/unit/test_operational_execution.py`
- `tests/unit/test_operational_postgres.py`

Only direct W2 compatibility changes are allowed。

---

## 19. New Test Files

A later W2 authorization MAY create exactly：

- `tests/unit/test_c08_broker_client_order_ref.py`
- `tests/unit/test_c05_durable_pending_submission.py`
- `tests/unit/test_c06_broker_action_safety.py`

No other new test file without reauthorization。

---

# Protected Scope

## 20. Protected Runtime Files

READ-ONLY during W2：

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
- C23/C24/C25 market-observation files。
- recovery / reconciliation files。
- broker discovery files。
- broker adapters。
- `backtest/shioaji_broker.py`
- `backtest/shioaji_mapping.py`
- `backtest/models.py`
- unrelated backtest / strategy / data modules。
- `data/`。

Any required write outside exact W2 scope：

STOP / REAUTHORIZATION。

---

## 21. Historical Migration Protection

READ-ONLY：

- 0001。
- 0002。
- 0003。
- 0004。
- 0005。

Candidate new migration only：

`0006_broker_action_safety.sql`

Migration creation：

candidate ALLOW under later authorization。

Migration execution：

DENY。

Backfill：

DENY。

Drop / destructive migration：

DENY。

Historical migration rewrite：

DENY。

---

## 22. 0006 Minimum Semantics

0006 must support：

- structured/queryable `broker_client_order_ref` representation for new durable Order projections。
- no historical migration rewrite。
- append-only BrokerActionAttempt。
- append-only BrokerActionResolution。
- database-enforced BrokerActionHead concurrency semantics。
- exact BrokerAccount / Order / action scoping。
- required durable authorization reference where applicable。
- stable immutable attempt identity。
- stable immutable resolution identity。
- Traditional Chinese TABLE/COLUMN comments。

Physical schema may preserve historical rows without claiming they satisfy new production conformance。

No migration execution or historical backfill occurs in W2。

---

# Broker Adapter Boundary

## 23. Shioaji Boundary

W2 broker invocation tests use fake/mock injected broker ports only。

W2 MUST NOT modify：

- Shioaji broker adapter。
- Shioaji order mapper。
- credentials。
- login。
- CA。
- actual simulation environment。
- actual production environment。

`custom_field` is not yet accepted as production correlation authority。

Concrete carrier verification belongs to broker capability verification。

Therefore W2 can establish broker-neutral safety architecture without making an unsupported production broker claim。

---

# Side-Effect Envelope

## 24. Proposed W2 Side-Effect Envelope

For a later explicit W2 source authorization：

    Source Modification:
        ALLOW — exact W2 scope only

    Test Execution:
        ALLOW

    Migration Creation:
        ALLOW — 0006 only

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

    Runtime Authorization:
        retain canonical NOT_AUTHORIZED

Source modification authority does not imply runtime/broker authority。

---

# Test Policy

## 25. C08 Targeted Tests

Required：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c08_broker_client_order_ref.py `
        tests/unit/test_operational_execution.py `
        tests/unit/test_operational_postgres.py `
        -q

Required negative evidence：

- durable sequence-0 PENDING rejects missing/blank client ref。
- persisted ref survives reload。
- later projection update cannot silently replace the ref。
- same canonical Order reuses same ref。
- broker_order_id remains distinct。
- no time-window/attribute heuristic identity。

Then：

    .\.venv\Scripts\python.exe -m pytest -q

---

## 26. C05 Targeted Tests

Required：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c05_durable_pending_submission.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_operational_execution.py `
        tests/unit/test_c25_market_observation_delivery.py `
        tests/unit/test_strategy_state_recovery.py `
        -q

Required negative evidence：

- broker invoker not called before durable PENDING commit。
- failed PENDING participant -> full rollback / zero broker call。
- failed material strategy snapshot -> full rollback / zero broker call。
- broker invocation does not occur while authority UoW/lock is active。
- exact expected snapshot checkpoint reference is preserved。
- sequence-0 PENDING contains the durable client ref。
- no best-effort dual write。

Then：

    .\.venv\Scripts\python.exe -m pytest -q

---

## 27. C06 Targeted Tests

Required：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c06_broker_action_safety.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_c21_authorization_seam.py `
        tests/unit/test_operational_execution.py `
        -q

Required negative evidence：

- BrokerActionAttempt commits before broker invocation。
- attempt commit failure -> zero broker invocation。
- unresolved attempt -> second invocation denied。
- zero exact broker match is not retry authority。
- generic timeout is not NOT_DISPATCHED。
- post-dispatch connection loss is outcome unknown。
- proven NOT_DISPATCHED may release the head only through durable resolution。
- concurrent unresolved attempts are rejected by durable concurrency semantics。
- SUBMIT and CANCEL share no-blind-retry rule。
- broker ref is not treated as server-side idempotency。
- no manual override is invented。

Then：

    .\.venv\Scripts\python.exe -m pytest -q

---

## 28. Wave Final Verification

After all three leaf-local commits：

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

Actual PostgreSQL：

NOT REQUIRED / NOT AUTHORIZED。

Broker I/O：

NOT REQUIRED / NOT AUTHORIZED。

---

# Correction / Retry Policy

## 29. Semantic Correction Budget

Per leaf：

maximum 2 scope-internal semantic correction cycles。

Tooling retry：

does not consume semantic correction budget。

Repeated same-class tooling failure：

root-cause inspection -> corrected approach -> reclassify / STOP if unresolved。

AUTHORITY / REVISION contradiction：

STOP。

---

# Git Policy

## 30. Candidate W2 Git Policy

A later explicit authorization may allow：

    git_commit:
        ALLOW
        per_leaf

    git_push:
        ALLOW
        wave_end

    force_push:
        DENY

Expected sequence：

    C08 commit
        ->
    refresh HEAD
        ->
    C05 commit
        ->
    refresh HEAD
        ->
    C06 commit
        ->
    final Wave verification
        ->
    fetch origin/master
        ->
    verify remote ancestry
        ->
    wave-end push

Unexpected remote divergence：

STOP。

No rebase through unknown remote work。

No force push。

No public-history rewrite。

---

# Execution Coherence

## 31. File / Symbol Compatibility

Result：

PASS。

C08 extends the canonical operational Order identity。

C05 reuses existing sequence-0 OrderEvent / Order projection / StrategyState repositories and C04 AccountAuthorityCommit transaction participant seam。

C06 adds an isolated durable broker-action evidence family and reuses the same account authority commit primitive。

No frozen requirement requires broker adapter modification during broker-neutral W2 implementation。

---

## 32. Side-Effect Compatibility

Result：

PASS。

All C08/C05/C06 implementation and verification can run using：

- deterministic unit tests。
- fake broker invocation port。
- fake/in-memory UoW。
- PostgreSQL adapter unit doubles。

No actual broker/network I/O is required。

No actual PostgreSQL is required。

No migration execution is required。

---

## 33. Protected-History Compatibility

Result：

PASS。

No W2 contract requires rewriting 0001～0005。

NEW 0006 is sufficient as the candidate schema boundary for action-attempt safety evidence。

Historical/backfill conformance remains outside W2。

---

## 34. Broker Capability Barrier

Result：

PASS WITH PRODUCTION DEFAULT-DENY。

The unresolved Shioaji custom_field round-trip capability does not block broker-neutral source implementation because：

- W2 does not modify the concrete Shioaji carrier。
- W2 does not perform broker I/O。
- W2 does not assert production capability。
- production submission remains default-deny until capability evidence exists。

Therefore no new broker architecture decision is required for bounded W2 implementation。

---

## 35. Human Decision Barrier

Result：

PASS FOR BOUNDED IMPLEMENTATION。

No new business or architecture decision is required。

W2 explicitly does NOT decide：

- production Shioaji custom_field capability。
- server-side idempotency。
- broker discovery horizon。
- restart-safe Fill identity。
- manual unresolved-attempt release policy。
- final BrokerAccount READY。
- production activation。

Those remain existing downstream/capability boundaries。

---

## 36. Overall W2 Execution Coherence

Dependency DAG：

VERIFIED。

Exact Leaf Set：

VERIFIED。

File / Symbol Scope：

VERIFIED。

Side-Effect Envelope：

VERIFIED。

Rewrite Compatibility：

VERIFIED。

Protected History：

VERIFIED。

Acceptance / Test Compatibility：

VERIFIED。

Broker Capability Barrier：

VERIFIED WITH DEFAULT-DENY PRODUCTION BOUNDARY。

Human Decision Barrier：

VERIFIED / NO NEW DECISION REQUIRED FOR BOUNDED IMPLEMENTATION。

Git Policy：

VERIFIED。

Retry / Correction Policy：

VERIFIED。

Reviewer / STOP Barrier：

VERIFIED。

Overall：

`EXECUTION_COHERENCE_VERIFIED`

This is planning evidence only。

It does NOT grant source modification authority。

---

# Next Authorization Input

## 37. Exact Proposed Later W2 Authorization

A separate later decision may authorize：

    Wave ID:
        GAP08-W2-EXECUTION-SAFETY

    Authorized Leaves:
        C08
        C05
        C06

    Runtime Source Modification Authorization:
        BOUNDED_AUTHORIZED_FOR_GAP08_W2

    Runtime Authorization:
        NOT_AUTHORIZED

    Migration Creation:
        0006 only

    Migration Execution:
        DENY

    Actual PostgreSQL:
        DENY

    Broker Network:
        DENY

    Paper Broker I/O:
        DENY

    Shioaji Simulation I/O:
        DENY

    Production Broker I/O:
        DENY

    Production Activation:
        DENY

    git_commit:
        ALLOW / per_leaf

    git_push:
        ALLOW / wave_end

    force_push:
        DENY

That authorization MUST be a separate explicit governance decision / commit。

Until that authorization becomes effective：

W2 runtime remains NOT_AUTHORIZED。

---

## 38. STOP Boundary

After this execution package is committed/pushed：

STOP。

Do NOT：

- modify runtime。
- modify tests。
- create migration 0006。
- execute any migration。
- access actual PostgreSQL。
- invoke paper broker。
- invoke Shioaji simulation。
- invoke production broker。
- access credentials。
- start C08。
- give W2 runtime work to CODEX。

Next action：

explicit bounded W2 Runtime Source Modification Authorization decision only。