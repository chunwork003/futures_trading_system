# GAP-08 Wave-3 — Broker Recovery Evidence Execution Package

## 1. Package Status

Wave ID：

`GAP08-W3-BROKER-RECOVERY-EVIDENCE`

Planning parent / W2 Closure Baseline：

`38dadf8399946cd96b96655fd2dbc21334d0ecbb`

Leaf sequence：

    C07
        -> C09
        -> C10

Candidate weight：

15。

Execution Coherence：

`EXECUTION_COHERENCE_VERIFIED`

Runtime Source Modification Authorization：

`NOT_AUTHORIZED`

Canonical Runtime Authorization：

`NOT_AUTHORIZED`

Production Activation：

`NOT_AUTHORIZED`

This document verifies an exact executable engineering package only。

It does NOT authorize runtime source modification。

---

## 2. Frozen Leaf Contracts

### C07 — Broker Discovery Authority

PASS：

- restart-safe BrokerAccount-scoped broker-neutral discovery。
- explicit completeness / required horizon / exact-match cardinality。
- authoritative refresh is part of the discovery contract where required。
- exact BrokerAccount filtering。
- query/external-state failure is explicit and account-scoped。
- positive evidence may survive incomplete discovery。
- absence has authority only for a complete required scope/horizon。

MUST NOT：

- process-memory Trade/cache satisfy restart authority。
- incomplete zero result prove absence。
- attribute/time-window heuristic become recovery identity authority。
- exact client correlation be treated as broker idempotency authority。

### C09 — Broker Report Inbox + Recovery Fence + Continuity

PASS：

- broker ingress during recovery is durably captured before canonical application。
- post-cut callback evidence is never dropped and never directly bypasses recovery fence。
- BrokerReportInboxEntry itself does not advance AccountStateHead。
- BrokerReportApplication preserves immutable application outcome evidence。
- recovery generation/currentness/fence semantics are durable。
- AccountRecoveryControl or equivalent remains distinct from economic AccountStateHead。
- continuity re-anchor preserves historical degradation instead of rewriting gaps。
- final handoff semantics are race-safe with durable ingress。

MUST NOT：

- callback evidence disappear during recovery。
- callback directly bypass recovery cut。
- stale recovery evaluation promote READY。
- re-anchor erase historical SequenceGap / degraded evidence。
- callback/inbox persistence become a second economic authority。

### C10 — Broker Recovery Reconstruction + Fill Economics

PASS：

- recovery reconstruction uses broker-neutral discovery evidence。
- canonical Fill is created only from deal-level exact broker evidence。
- verified restart-stable BrokerDealIdentity is required before production-authoritative Fill identity may be claimed。
- same exact DealIdentity + same material content is duplicate/corroborating evidence。
- same DealIdentity + conflicting material content is integrity conflict。
- PENDING -> PARTIALLY_FILLED and PENDING -> FILLED are legal evidence-backed recovery transitions。
- PARTIALLY_FILLED -> PARTIALLY_FILLED with a newly accepted Fill is material。
- no unsupported intermediate lifecycle history is fabricated。
- canonical Fill set owns filled_quantity / weighted average_fill_price。
- terminal canonical lifecycle/economics are sealed。
- incomplete/unverified reconstruction performs no partial authority mutation。
- recovery mutation uses existing AccountAuthorityCommit and exact expected_head_revision / recovery-cut revision semantics。
- when one evidence set changes execution lifecycle and resolves a BrokerActionAttempt, execution effects + action resolution share one account-authority commit/revision。
- broker network I/O is outside the account-authority DB lock/UoW。

MUST NOT：

- aggregate deal_quantity / average fabricate Fill。
- timestamp / price / quantity heuristic fabricate Fill identity。
- callback-only identity become restart Fill authority。
- terminal Order accept later economic enrichment/regression。
- broker aggregate values overwrite canonical fill-set economics。
- recovery create an independent economic persistence authority。

---

## 3. Dependency Coherence

Frozen dependencies：

- C07 depends on accepted C08。
- C09 depends on accepted C02 / C04 / C07。
- C10 depends on accepted C04 / C07 / C09 / C11。

Current accepted dependencies：

- C02：ACCEPTED。
- C04：ACCEPTED。
- C08：ACCEPTED。
- C11：ACCEPTED。

Therefore：

    C07 -> C09 -> C10

is dependency-coherent after W2 closure。

No C12/C13/C14/C15 dependency is required to implement the bounded P5 core contracts。

---

## 4. Repository Evidence

Current repo already contains：

- `trading.execution.Order / Fill / OrderEvent`。
- `ExecutionPersistenceService` + AccountAuthorityCommit participant seam。
- `BrokerActionAttempt / Resolution / Head` from accepted W2。
- `AccountStateHead / AccountRecoveryCheckpoint / AccountAuthorityCommit` from accepted W1。
- `persistence/recovery.py` legacy/current orchestration surface。
- reconciliation domain/persistence foundations。
- broker capability matrix with documentation-level TRADE_LIST / ORDER_DEAL_EVENT evidence。
- legacy Shioaji execution/status/fill code under `backtest/shioaji_*`。
- target Sinopac adapter boundary under `adapters/sinopac/`。

But the repo does NOT yet contain one canonical broker-neutral owner implementing all C07/C09/C10 recovery contracts。

Existing `backtest/shioaji_*` process-memory Trade/deal behavior is NOT restart recovery authority。

Existing `persistence/recovery.py` is NOT widened during W3 because C12 later owns coherent RecoveryCut / ExecutionStateLoader correction。

---

## 5. Broker Capability Gates

The following verification leaves remain separate：

- V01 — Shioaji Discovery Scope / Horizon Verification。
- V02 — Client Correlation Round-Trip Verification。
- V03 — Restart-Stable BrokerDealIdentity Verification。
- V04 — Event Tracking / Continuity / Re-anchor Verification。
- V05 — PreSubmitted / Inactive / Failed Semantics Verification。

Documentation evidence exists for Shioaji TRADE_LIST / ORDER_DEAL_EVENT and related API surfaces。

That evidence does NOT prove：

- production restart discovery horizon completeness。
- exact production custom_field round-trip。
- restart-stable production Deal.seq / BrokerDealIdentity uniqueness。
- pinned event-tracking continuity semantics。
- PreSubmitted / Inactive / relevant Failed production semantics。

Therefore W3 core implementation may only consume broker-neutral verified-evidence contracts and fake/mock evidence in tests。

Production capability remains default-deny until the applicable V-leaf verification is separately authorized and accepted。

---

## 6. Proposed Later Existing Runtime Write Scope

If a separate W3 source-modification authorization is later granted, existing runtime writes are bounded to：

- `trading/execution.py`
- `persistence/execution.py`
- `persistence/postgres/execution.py`

Purpose：

### `trading/execution.py`

C10-only compatibility：

- explicit canonical OrderEvent provenance/source capable of LOCAL_OMS / BROKER_CALLBACK / BROKER_DISCOVERY or equivalent frozen semantics。
- permit evidence-backed direct PENDING -> PARTIALLY_FILLED / FILLED transitions。
- preserve terminal immutability。
- reusable fill-set economic validation/projection only if needed to avoid duplicated business authority。

### `persistence/execution.py`

C10-only compatibility：

- preserve shared AccountAuthorityCommit participant usage。
- expose/read complete LocalFillSet by Order where needed for deterministic recovery comparison。
- map canonical event provenance without creating a second event stream。
- do not add independent commit authority。

### `persistence/postgres/execution.py`

C10-only compatibility：

- implement any newly required read-only FillRepository list-by-order/read contract。
- no independent commit/rollback。
- no historical table rewrite。

No other existing runtime file is part of the proposed W3 write scope。

---

## 7. Proposed Later New Runtime Files

Exact proposed new files：

- `trading/broker_recovery.py`
- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/postgres/migrations/0007_broker_recovery_evidence.sql`

### `trading/broker_recovery.py`

Owns broker-neutral C07/C10 domain contracts：

- BrokerAccount-scoped discovery provider protocol/equivalent。
- immutable discovery observation / run identity。
- discovery completeness/horizon/cardinality classification。
- broker-neutral observed order/deal evidence。
- recovery discovery/continuity gates where domain-pure。
- exact correlation matching。
- reconstruction classification。
- typed incomplete/conflict/capability-unverified results。
- pure Fill-set/lifecycle reconstruction planning where possible。

It MUST NOT import Shioaji。

### `persistence/broker_recovery.py`

Owns C09 durable evidence/control and C10 authority coordination：

- BrokerReportInboxEntry。
- BrokerReportApplication。
- AccountRecoveryControl or equivalent generation/fence control。
- ExecutionContinuityEpoch or equivalent durable continuity evidence。
- durable broker deal/discovery evidence where required for audit/conflict detection。
- repository protocols。
- inbox capture/application services。
- recovery authority coordinator that composes existing:
  - AccountAuthorityCommitService。
  - ExecutionPersistenceService participant。
  - BrokerActionResolution participant when applicable。

It MUST NOT become a second AccountStateHead/economic authority。

### `persistence/postgres/broker_recovery.py`

Owns PostgreSQL adapters for the new broker-recovery evidence/control contracts。

Repositories never commit/rollback independently。

### `0007_broker_recovery_evidence.sql`

May create/alter only new W3 recovery-evidence/control structures required by C07/C09/C10。

Conceptual durable structures may include equivalent forms of：

- broker discovery observation/run evidence。
- broker report inbox。
- broker report application history。
- account recovery control/generation。
- execution continuity epoch/history。
- exact broker deal evidence/conflict identity support。

Physical names may differ if the semantic contract is preserved。

---

## 8. Proposed Later Existing Test Write Scope

Only：

- `tests/unit/test_operational_execution.py`
- `tests/unit/test_operational_postgres.py`

These may receive only direct compatibility/adapter tests required by W3。

---

## 9. Proposed Later New Tests

Exact proposed new tests：

- `tests/unit/test_c07_broker_discovery.py`
- `tests/unit/test_c09_broker_recovery_fence.py`
- `tests/unit/test_c10_broker_reconstruction.py`

No additional test file is pre-authorized by this package。

---

## 10. Protected / Read-Only Surfaces

Unless separately reauthorized, W3 keeps these READ-ONLY：

### Accepted account/submission authority

- `persistence/account_authority.py`
- `persistence/postgres/account_authority.py`
- `persistence/broker_action.py`
- `persistence/postgres/broker_action.py`
- `trading/authorization.py`

W3 must consume these authorities；it must not rewrite them。

### Deferred recovery/reconciliation leaves

- `persistence/recovery.py`
- `persistence/reconciliation.py`
- `persistence/postgres/reconciliation.py`
- `trading/reconciliation.py`

Reason：

- C12 later owns coherent RecoveryCut + ExecutionStateLoader。
- C13/C14 later own corrected ReconciliationCase/ReconciliationRun boundaries。
- C15 later owns final BrokerAccount READY / REVIEW / HALT aggregation。

P5 may produce evidence/gates consumed later；it does not implement those later leaves。

### Strategy / market-observation authority

- `persistence/strategy_state.py`
- `persistence/postgres/strategy_state.py`
- `persistence/market_observation.py`
- `persistence/postgres/market_observation.py`
- `persistence/market_observation_delivery.py`

### Account projection foundation

- `persistence/account.py`
- `persistence/postgres/account.py`
- `trading/account.py`

If C10 cannot reuse these without modification：

STOP / REAUTHORIZATION。

### Broker adapters

All existing broker-specific execution adapters remain READ-ONLY：

- `backtest/shioaji_broker.py`
- `backtest/shioaji_fill.py`
- `backtest/shioaji_mapping.py`
- other `backtest/shioaji_*`。
- `adapters/sinopac/*`。
- `adapters/capabilities.py`。

W3 core must not claim concrete production Shioaji discovery/reconstruction capability。

### Data / unrelated runtime

- `data/`
- backtest engine/strategy/risk modules。
- unrelated domain/application modules。

---

## 11. Historical Migration Protection

Migrations 0001～0006：

READ-ONLY。

0006 is accepted W2 source and remains NOT EXECUTED。

Proposed new migration：

`0007_broker_recovery_evidence.sql`

Creation：

candidate for later bounded authorization only。

Execution：

DENY。

Backfill：

DENY。

Historical rewrite：

DENY。

Destructive migration：

DENY。

Actual PostgreSQL：

DENY。

V07：

DENY。

---

## 12. C07 Detailed Acceptance

C07 implementation must prove：

1. discovery input/output is BrokerAccount-scoped。
2. wrong-account evidence fails typed/fail-closed。
3. authoritative refresh/currentness evidence is explicit where required。
4. one immutable discovery_run_id fences one coherent evidence collection。
5. post-refresh health belongs to the same discovery world。
6. completeness and exact-match cardinality are separate。
7. cardinality has zero / exactly-one / more-than-one semantics。
8. incomplete zero does NOT prove absence。
9. complete zero means only “no exact broker match in the verified required scope/horizon”；it does not override an unresolved BrokerActionAttempt。
10. more than one exact correlation match is an integrity/ambiguity result。
11. process-memory Trade cache is never restart authority。
12. discovery provider is read-only and separate from submit/cancel。
13. typed query/external-state failure remains account-scoped。
14. no Shioaji object escapes the broker-neutral contract。

C07 does NOT establish production V01/V02/V03/V04/V05 verification。

---

## 13. C09 Detailed Acceptance

C09 implementation must prove：

1. broker report/callback evidence can be durably captured before canonical application。
2. inbox identity is immutable/idempotent。
3. duplicate exact inbox evidence deduplicates without losing provenance。
4. conflicting same inbox identity fails closed。
5. BrokerReportInboxEntry does not advance AccountStateHead。
6. application history is immutable and supports at least:
   - APPLIED
   - DUPLICATE
   - CORROBORATED
   - DEFERRED
   - CONFLICT
7. post-cut evidence is DEFERRED/captured rather than dropped or directly applied through the fence。
8. AccountRecoveryControl/generation is durable and separate from economic account revision。
9. stale recovery generation/cut cannot finalize handoff。
10. continuity state distinguishes current trust from historical stream degradation。
11. re-anchor never deletes/rewrites SequenceGap history。
12. PendingReport / unresolved material broker evidence prevents the applicable completeness/continuity trust。
13. final handoff primitive is race-safe with concurrent durable ingress at repository/transaction level。
14. no production callback registration/network I/O occurs in W3 tests。

---

## 14. C10 Detailed Acceptance

C10 implementation must prove：

1. canonical reconstruction consumes only broker-neutral discovery/inbox evidence。
2. callback/discovery provenance is explicit on canonical OrderEvent/equivalent。
3. no fabricated intermediate lifecycle event is required。
4. PENDING -> PARTIALLY_FILLED / FILLED works when exact evidence supports it。
5. same-status PARTIALLY_FILLED with new exact Fill evidence advances material lifecycle evidence。
6. broker Deal evidence requires exact BrokerDealIdentity authority。
7. no timestamp/price/quantity heuristic Fill ID fallback。
8. no aggregate deal quantity/average synthetic Fill。
9. same exact DealIdentity + same material content deduplicates/corroborates。
10. same exact DealIdentity + different material content is integrity conflict。
11. canonical LocalFillSet is read completely before economics are projected。
12. filled_quantity equals canonical Fill-set quantity sum。
13. average_fill_price is exact quantity-weighted canonical Fill-set value。
14. broker aggregate values are validation evidence only。
15. terminal accepted Order rejects later Fill/economic enrichment/regression。
16. incomplete/unverified evidence returns typed incomplete/capability result and commits no partial authority mutation。
17. recovery-cut revision maps to existing AccountAuthorityCommit expected_head_revision semantics。
18. stale revision fails/aborts rather than silently applying evidence。
19. position-changing Fill requires complete AccountPositionSnapshot in the same authority transaction。
20. status-only transition carries the prior exact expected_snapshot_id。
21. action resolution may join the same authority commit via accepted W2 participant semantics。
22. no broker network call occurs while AccountAuthorityCommit UoW/lock is active。

---

## 15. Capability Default-Deny Rules

W3 source implementation MUST NOT claim that:

- Shioaji discovery horizon is production verified。
- `custom_field` is production restart-stable correlation authority。
- `Deal.seq` is production restart-stable BrokerDealIdentity。
- event tracking/re-anchor capability is production verified。
- PreSubmitted / Inactive / Failed semantics are production verified。
- quantity modification recovery is supported。
- callback delivery is exactly once。
- list_trades projection is sufficient after ProjectionFailed。
- broker supports server-side idempotent resubmission。

These remain verification/deferred gates。

---

## 16. Proposed C07 Test Policy

Required targeted suite：

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

---

## 17. Proposed C09 Test Policy

Required targeted suite：

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

Then exact C09 scope validation。

---

## 18. Proposed C10 Test Policy

Required targeted suite：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c10_broker_reconstruction.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_c06_broker_action_safety.py `
        tests/unit/test_c11_shioaji_status_mapping.py `
        tests/unit/test_operational_execution.py `
        tests/unit/test_operational_postgres.py `
        -q

If `tests/unit/test_c11_shioaji_status_mapping.py` does not exist at authorization time,
the authorization package must replace it with the exact existing C11 test file(s)
without expanding W3 runtime scope。

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Then：

    git diff --check

Then exact C10 scope validation。

---

## 19. Proposed Wave Final Verification

At Wave end：

    .\.venv\Scripts\python.exe -m pytest `
        tests/unit/test_c07_broker_discovery.py `
        tests/unit/test_c09_broker_recovery_fence.py `
        tests/unit/test_c10_broker_reconstruction.py `
        tests/unit/test_c04_account_authority_commit.py `
        tests/unit/test_c06_broker_action_safety.py `
        tests/unit/test_c08_broker_client_order_ref.py `
        tests/unit/test_operational_execution.py `
        tests/unit/test_operational_postgres.py `
        tests/unit/test_broker_capabilities.py `
        -q

Then：

    .\.venv\Scripts\python.exe -m pytest -q

Then：

    git diff --check

Then cumulative exact scope validation。

No actual broker or PostgreSQL environment verification is part of this Wave。

---

## 20. Proposed Git Policy

If later authorized：

    git_commit:
        ALLOW
        per_leaf

    git_push:
        ALLOW
        wave_end

    force_push:
        DENY

Expected local commit sequence：

    C07
        -> C09
        -> C10

No intermediate push by default。

Remote divergence before wave-end push：

STOP。

---

## 21. Semantic Correction Budget

Proposed maximum：

2 scope-internal semantic correction cycles per leaf。

Tooling retries do not consume semantic correction budget but remain finite。

Architecture / authority contradiction：

STOP。

---

## 22. Source Documentation Requirements

Important new module/class/public function/public contract must use Traditional Chinese comments/docstrings explaining applicable：

- 用途。
- 責任。
- upstream / data source。
- downstream consumer。
- important invariant。
- non-obvious broker/recovery rule。
- explicit non-responsibility。

No low-value translation-only comments。

---

## 23. STOP / Reauthorization Boundary

STOP if implementation requires：

- any existing runtime file outside the exact proposed write scope。
- any new runtime/test/migration file outside the exact proposed list。
- modification of `persistence/recovery.py`。
- modification of reconciliation modules。
- modification of W1/W2 account/broker action authority modules。
- modification of account projection modules。
- any Shioaji/Sinopac adapter modification。
- actual broker network/paper/simulation/production I/O。
- callback registration against a real broker。
- migration execution。
- actual PostgreSQL / V07。
- production capability verification。
- manual retry/release/approval authority。
- C12/C13/C14/C15 implementation。
- V01～V05 execution。
- quantity-modification recovery。
- credential/security boundary change。
- new architecture/business decision。
- destructive migration。
- unrelated regression。
- remote divergence。

---

## 24. Execution Coherence Decision

C07 -> C09 -> C10 is execution-coherent because：

- C08 already provides immutable client correlation identity。
- C02/C04 already provide BrokerAccount account-authority revision/commit primitive。
- C06 already provides durable action attempt/resolution/head semantics。
- C11 already fail-closes unverified broker statuses。
- C07 can introduce broker-neutral discovery evidence without concrete broker network use。
- C09 can durably capture ingress/fence/continuity without advancing AccountStateHead for observation-only evidence。
- C10 can compose existing execution/account/action participants under AccountAuthorityCommit。
- all tests can use fake/mock broker-neutral evidence。
- production capability gates remain separately default-deny。
- C12/C13/C14/C15 do not need to be implemented to construct the bounded P5 evidence primitives。

Therefore：

`EXECUTION_COHERENCE_VERIFIED`

But：

`RUNTIME_SOURCE_MODIFICATION_NOT_AUTHORIZED`

---

## 25. Current Progress

Accepted correction-core progress：

60 / 113。

Remaining：

53。

W3 candidate weight：

15。

W3 weight credited：

NO。

Tooling evidence：

- W3 precheck attempt 1：TOOLING RETRY due strict Unicode punctuation marker。
- W3 precheck v2：PASS。
- semantic correction：0。

---

## 26. Next Governance Action

Next：

separate explicit bounded W3 Runtime Source Modification Authorization decision。

That authorization must revalidate：

- exact file list still exists/matches。
- exact C11 test filename used in C10 targeted suite。
- no remote divergence。
- no newly discovered architecture contradiction。
- 0007 is still the next migration number。
- side-effect envelope remains unchanged。

Until that separate authorization is committed/pushed：

DO NOT start C07 runtime。

DO NOT hand runtime implementation to CODEX。

---

## 27. Current Authority

W2：

COMPLETE / VERIFIED / REVIEWER_ACCEPTED / CLOSED。

W3：

EXECUTION_COHERENCE_VERIFIED / RUNTIME_NOT_AUTHORIZED。

Canonical Runtime Authorization：

NOT_AUTHORIZED。

Production Activation：

NOT_AUTHORIZED。