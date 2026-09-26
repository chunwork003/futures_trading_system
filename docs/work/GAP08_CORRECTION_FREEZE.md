# GAP-08 Correction-Freeze Work Package

## 1. Status

CORRECTION_FREEZE_COMPLETE / DOCS_ONLY

Runtime Authorization：

NOT_AUTHORIZED。

Architecture Acceptance：

HOLD。

Runtime Conformance：

NOT ASSERTED。

Production Readiness：

NOT ASSERTED。

This document is an execution-planning / correction-freeze artifact。

It is NOT a new Architecture Decision Baseline。

It does NOT authorize runtime modification、migration execution、broker I/O or production use。

---

## 2. Baselines

Architecture Decision Baseline：

`22ceaa729ab6e9da9c00ae52e09ae7116be5a743`

GOV-01 Governance Planning Baseline：

`f45742d9d16165f87f145f0d2bdc8d530772e5ee`

Semantic-neutral governance cleanup before this checkpoint：

`849bc6ea3f3ee0d1de969a5f23862bc60720c4fc`

Runtime Candidate：

`6b62239bca1d11543944f9f078e577e16010bcbf`

Runtime verification retained from candidate：

934 passed / 4 skipped / 1 warning。

No tests are rerun by this docs-only checkpoint。

---

## 3. Planning Inputs

Frozen architecture authority：

- R-01～R-14。
- ADR-002 recovery consistency / market observation decisions。
- Decision Checkpoint 5E remains the Architecture Decision Baseline。

Post-5E accepted planning inputs：

- K520 defer confirmation。
- BG-01～BG-07 broker gate classification。
- Complete Expanded Correction-Scope Map。
- Delta-to-Contract planning rule。
- positive evidence requirement for KNOWN_CONFORMANT。
- Production Gate != engineering leaf。
- DB-CONF-01A / DB-CONF-01B split。

These post-5E items are accepted planning inputs。

They do NOT create a new Architecture Decision Baseline。

---

## 4. Delta-to-Contract Rule

For each exact Frozen Contract Assertion：

    KNOWN_NONCONFORMANT
        -> CORRECTION_REQUIRED

    NOT_IMPLEMENTED
        -> IMPLEMENTATION_REQUIRED

    UNKNOWN_CONFORMANCE
        -> CONFORMANCE_ONLY

    UNKNOWN_CAPABILITY_EVIDENCE
        -> VERIFICATION_REQUIRED

    KNOWN_CONFORMANT
        -> NO_CURRENT_WORK

    DEFERRED
        -> DEFERRED

No defect found != KNOWN_CONFORMANT。

Historical tests passing != proof of current frozen-contract conformance。

Exact positive evidence is required。

Evidence dimensions may be：

    EVIDENCE_ANCHORED

or：

    NOT_APPLICABLE
    + explicit justification

They may not be silently omitted。

---

## 5. Bounded Internal Rewrite Policy

Bounded internal rewrite is allowed and may be preferred when：

1. the candidate abstraction directly contradicts the frozen contract。
2. preserving the old internals would create duplicate authority paths or excessive workaround complexity。
3. rewrite scope has one clear owner / failure boundary。
4. canonical/external behavior can be protected by tests。
5. compatibility facade can preserve unaffected callers where appropriate。
6. persistence history is not rewritten。
7. unrelated architecture is not pulled into scope。

Preferred bounded rewrite areas：

- C01 expected-state authoritative read path。
- C04 AccountAuthorityCommit / ExecutionPersistenceService internals。
- C12 RecoveryCut / ExecutionStateLoader internals。

Bounded rewrite allowed where useful：

- C05 broker-bound submission coordinator。
- C10 recovery-facing Fill / reconstruction plumbing。

Preserve / extend rather than rewrite without new evidence：

- PostgresUnitOfWork。
- migration discovery foundation。
- TradingEvent / EventLedger foundation。
- pure AccountPosition / OrderIntent / PositionEffect foundation。
- pure reconciliation comparison foundation。
- StrategyRegistry basic registry behavior。

Historical migrations：

`0001` / `0002`

MUST NOT be rewritten in place。

Correction schema uses new versioned migration(s)，starting at `0003+` as required。

---

## 6. Correction / Implementation / Enforcement Leaves

Existing Blueprint weight scale 2～5 is reused。

Weight describes bounded engineering / authority / verification effort。

Weight is not LOC、calendar time or completion percentage。

| ID | Name | Work Type | Weight | Entry Dependencies | Rewrite |
|---|---|---|---:|---|---|
| C01 | Expected State Authority Read Contract | CORRECTION + IMPLEMENTATION | 4 | V06 | PREFERRED |
| C02 | BrokerAccount Revision Head + Exact Checkpoint | IMPLEMENTATION | 5 | V06,C01 | ALLOWED |
| C03 | Expected-State Initialization Authority | IMPLEMENTATION | 5 | C02,C04,C21 | ALLOWED |
| C04 | Shared AccountAuthorityCommit Primitive | IMPLEMENTATION | 5 | V06,C02 | PREFERRED |
| C05 | Durable Initial PENDING + Causal Execution Boundary | CORRECTION + IMPLEMENTATION | 5 | C04,C08,C25 | ALLOWED |
| C06 | BrokerActionAttempt / Resolution / No-Blind-Retry | IMPLEMENTATION | 5 | C04,C05 | ALLOWED |
| C07 | Broker Discovery Authority | IMPLEMENTATION | 5 | C08 | EXTEND |
| C08 | Broker Client Correlation Identity | IMPLEMENTATION | 4 | V06 | EXTEND |
| C09 | Broker Report Inbox + Recovery Fence + Continuity | IMPLEMENTATION | 5 | C02,C04,C07 | ALLOWED |
| C10 | Broker Recovery Reconstruction + Fill Economics | IMPLEMENTATION + CORRECTION | 5 | C04,C07,C09,C11 | ALLOWED |
| C11 | Shioaji Status Mapping Correction | CORRECTION | 2 | none | SMALL_FIX |
| C12 | Coherent RecoveryCut + ExecutionStateLoader | CORRECTION + IMPLEMENTATION | 5 | C01,C02,C04,C09,C13 | PREFERRED |
| C13 | ReconciliationCase BrokerAccount Scope | CORRECTION | 3 | V06 | EXTEND |
| C14 | ReconciliationRun Audit | IMPLEMENTATION | 5 | C12,C13 | EXTEND |
| C15 | BrokerAccount READY / REVIEW / HALT Aggregator | CORRECTION + IMPLEMENTATION | 5 | C07,C09,C10,C12,C14 | EXTEND |
| C16 | Strategy Governing Identity + Canonical Binding | IMPLEMENTATION + CORRECTION | 5 | V06 | EXTEND |
| C17 | Strategy Governing Context Transition | IMPLEMENTATION | 4 | C16 | EXTEND |
| C18 | Strategy Recovery Frontier + Readiness Composition | CORRECTION + IMPLEMENTATION | 5 | C15,C16,C17,C19,C20,C25 | ALLOWED |
| C19 | K520 Applicability Fail-Closed Seam | ENFORCEMENT | 3 | C16 | EXTEND |
| C20 | R14 Completeness Required Seam | ENFORCEMENT | 3 | C23 | EXTEND |
| C21 | Protected Action Authorization Enforcement Seam | ENFORCEMENT | 4 | V06 | EXTEND |
| C22 | Canonical Time Evidence Correction | CORRECTION | 4 | V06 | EXTEND |
| C23 | Canonical MarketObservation Identity + Revision | IMPLEMENTATION | 5 | C22 | NEW_PRIMITIVE |
| C24 | Operational MarketObservation Evidence + Acceptance | IMPLEMENTATION | 5 | V06,C23 | NEW_PRIMITIVE |
| C25 | Durable-before-Strategy Delivery + Revision Reference Migration | IMPLEMENTATION + CORRECTION | 4 | C24 | ALLOWED |

Correction / implementation / enforcement delta：

25 leaves / weight 110。

---

## 7. Leaf Acceptance Boundaries

### C01

PASS：

- NOT_INITIALIZED / EXPLICIT_FLAT / EXPECTED_POSITIONS remain distinct。
- typed read/integrity failures remain distinct。

MUST NOT：

- missing snapshot -> FLAT。
- DB read failure -> NOT_INITIALIZED。
- broken exact reference -> SELECT latest fallback。

### C02

PASS：

- BrokerAccount contiguous authority revision。
- exactly one checkpoint per successful revision。
- checkpoint exact-references expected_snapshot_id。
- stable authority-commit receipt semantics。

MUST NOT：

- revision gap。
- latest snapshot replacing exact checkpoint reference。
- conflicting same commit identity silently deduplicated。

### C03

PASS：

- explicit EXPECTED_STATE_INITIALIZED。
- FLAT / BROKER_SEED validation。
- revision-1 event/snapshot/head/checkpoint/receipt atomic closure。

MUST NOT：

- missing rows silently bootstrap。
- broker empty observation create expected FLAT。
- BROKER_SEED fabricate Order / Fill history。

### C04

PASS：

- one material authority commit = one BrokerAccount revision。
- atomic OrderEvent / Fill / expected snapshot / action resolution / checkpoint closure。
- stable idempotent commit receipt。

MUST NOT：

- partial economic commit。
- revision advance without checkpoint。
- ambiguous DB commit blindly applied again。

### C05

PASS：

- durable sequence-0 PENDING before broker side effect。
- material strategy-state causal boundary preserved where applicable。

MUST NOT：

- broker I/O before durable PENDING。
- broker network I/O while authority DB lock is held。
- best-effort dual write replacing crash invariant。

### C06

PASS：

- BrokerActionAttempt durable before material broker invocation。
- SUBMIT / CANCEL unresolved outcome cannot auto re-invoke。
- durable resolution/head concurrency semantics。

MUST NOT：

- zero broker match prove safe retry after dispatched unknown outcome。
- unresolved attempt produce second invocation。

### C07

PASS：

- restart-safe BrokerAccount-scoped broker-neutral discovery。
- explicit completeness/horizon/cardinality。
- authoritative refresh where required。

MUST NOT：

- process-memory Trade/cache satisfy restart authority。
- incomplete zero results prove absence。

### C08

PASS：

- immutable durable broker_client_order_ref before I/O。
- same canonical Order reuses same ref。

MUST NOT：

- create a new ref on retry。
- use attribute/time-window heuristic as authority。

### C09

PASS：

- broker ingress during recovery is durably captured。
- recovery generation/currentness/fence semantics。
- continuity re-anchor does not rewrite historical gaps。

MUST NOT：

- callbacks disappear during recovery。
- callback bypass recovery cut。
- stale evaluation promote READY。

### C10

PASS：

- deal-level identifiable Fill reconstruction。
- fill-set economic authority。
- terminal economic sealing。
- same-status partial Fill material event。

MUST NOT：

- aggregate deal quantity / average fabricate Fill。
- timestamp/price/quantity heuristic Fill identity。
- terminal Order accept later economic enrichment。

### C11

PASS：

- unverified broker statuses remain capability-unverified / non-authoritative as required。

MUST NOT：

- unconditional Inactive -> REJECTED。
- unconditional Failed -> REJECTED without verified zero-effect semantics。
- PreSubmitted automatically claim canonical SUBMITTED semantics without verification。

### C12

PASS：

- ExecutionStateLoader is Read + Validate + Explicit Result。
- coherent complete RecoveryCut。
- VALID -> RecoveryExecutionContext only。

MUST NOT：

- independent latest reads claim coherent cut。
- loader perform broker I/O / repair / economic mutation。
- loader VALID imply READY。

### C13

PASS：

- one primary BrokerAccount scope per ReconciliationCase。
- append-only case history preserved。

MUST NOT：

- global unresolved case gate unrelated accounts。
- case.open become economic/readiness truth authority。

### C14

PASS：

- durable formal ReconciliationRun boundary。
- exact evaluated-world binding。
- technical / qualification / domain-result axes separated。
- crash-consistent terminal audit finalization。

MUST NOT：

- SELECT latest MATCH -> READY。
- finalized Run expose partial required result evidence。

### C15

PASS：

- HALT > REVIEW > READY。
- READY requires positive mandatory predicate proof。
- final handoff validates currentness and unapplied evidence。

MUST NOT：

- position MATCH + restored strategy alone imply BrokerAccount READY。
- UNKNOWN / DEGRADED / NO_ERROR_OBSERVED imply READY。

### C16

PASS：

- exact StrategyInstance/config/implementation/canonical-binding provenance。
- symbol remains non-authoritative alias。

MUST NOT：

- mutable config hash define StrategyInstance identity。
- current alias resolution silently rewrite historical binding。
- symbol directly authorize broker execution。

### C17

PASS：

- PRE_TRANSITION / TRANSITION_IN_PROGRESS / POST_TRANSITION recoverable boundary。

MUST NOT：

- TRANSITION_IN_PROGRESS become TradingReady。
- mixed incompatible pre/post authority activate。

### C18

PASS：

- BrokerAccountExecutionReady / StrategyRestoreValid / StrategyTradingReady / DecisionCohortTradingReady distinct。
- exact governing cohort membership resolved from authority。
- catch-up isolated from normal broker action。

MUST NOT：

- caller-provided loaded list become cohort authority。
- failed required strategy silently dropped/substituted。
- startup catch-up emit normal material broker action。

### C19

PASS：

- K520 applicability uses positive exact StrategyInstance recovery contract。
- safe deterministic reconstruction requires proven sufficient horizon and governing behavior。

MUST NOT：

- missing payload == NOT_APPLICABLE。
- current implementation appears stateless == NOT_APPLICABLE。
- UNKNOWN impact become TradingReady。

### C20

PASS：

- authoritative completeness-required seam。
- production/test completeness authority separated。
- unproven required completeness blocks dependent Strategy/Cohort readiness。

MUST NOT：

- fake test provider become production authority。
- R14 COMPLETE replace K520 relevance proof。
- no candidate imply authoritative no-trade。

### C21

PASS：

- trusted authorization-required core enforcement seam。
- production missing authority -> DEFAULT DENY。
- durable protected-action attribution。

MUST NOT：

- actor string / reason / bool become production authorization proof。
- approval bypass HALT or R04G no-resubmit。

### C22

PASS：

- occurred_at / received_at / observed_at / recorded_at semantics remain distinct。
- explicit clock/source-time authority。

MUST NOT：

- received_at = occurred_at convenience fallback。
- UNKNOWN source occurrence filled with local now。
- timestamp become causal authority。

### C23

PASS：

- MarketObservationLogicalKey / Fingerprint / RevisionId distinct。
- deterministic mor1 identity。
- canonical decimal / UTC encoding。
- golden-vector behavior。

MUST NOT：

- raw float or generic JSON define identity。
- listed future without contract_id become canonical observation。
- revision_seq enter cross-environment mor1 identity。

### C24

PASS：

- candidate/provenance evidence separate from accepted revision。
- versioned acceptance policy。
- per-logical-key revision ordering。
- database atomic uniqueness/conflict classification。

MUST NOT：

- last-write-wins。
- application SELECT-if-missing -> INSERT as uniqueness authority。
- source tier automatically become price truth。

### C25

PASS：

- recovery-capable strategy consumes durable accepted observation revision。
- StrategyStateSnapshot / ExecutionTriggerRef use exact revision-specific references。
- bounded compatibility migration。

MUST NOT：

- strategy delivery before durable accepted revision。
- legacy arbitrary ID remain recovery authority after canonical writer exists。
- legacy/canonical dual authority silently disagree。

---

## 8. Verification Leaves

| ID | Name | Weight | Scope |
|---|---|---:|---|
| V01 | Shioaji Discovery Scope / Horizon Verification | 4 | broker capability |
| V02 | Client Correlation Round-Trip Verification | 4 | broker capability |
| V03 | Restart-Stable BrokerDealIdentity Verification | 4 | broker capability |
| V04 | Event Tracking / Continuity / Re-anchor Verification | 4 | broker capability |
| V05 | PreSubmitted / Inactive / Failed Semantics Verification | 3 | broker capability |
| V06 | Repository Persistence Baseline Verification | 3 | repository / DB design evidence |
| V07 | Actual PostgreSQL Environment Conformance | 4 | environment conditional |

V01～V05 total：

19。

V06：

3。

V07：

4 conditional。

Production Gate itself is status metadata and has coding weight 0。

PAPER_VERIFIED != PRODUCTION_VERIFIED。

V01～V05 do not imply broker I/O is currently authorized。

V07 enters an execution envelope only when a specific PostgreSQL environment / migration/integration scope is explicitly authorized。

---

## 9. Reweighted GAP-08 Planning Envelope

Original GAP-08EFGHI candidate：

35 leaves / weight 151。

Current correction / implementation / enforcement delta：

C01～C25：

weight 110。

Repository persistence verification：

V06：

weight 3。

Bounded Correction Core：

    110 + 3
    = 113

Original candidate + bounded correction core：

    151 + 113
    = 264

Separate broker capability verification inventory：

    V01～V05
    = 19

Full mapped planning envelope excluding actual environment conformance：

    264 + 19
    = 283

Conditional actual PostgreSQL environment conformance：

    V07
    = 4

Maximum mapped envelope if V07 is explicitly brought into scope：

    283 + 4
    = 287

These values are planning / engineering weights。

They do not grant acceptance credit by themselves。

The original 151 candidate remains IMPLEMENTED CANDIDATE / NOT ACCEPTED until correction execution and acceptance complete。

---

## 10. Global Lifecycle Metric Rule

The existing 47.92% remains the recorded architecture-freeze lifecycle baseline for now。

This correction-freeze checkpoint does NOT invent a new global percentage。

Reason：

- package reweight is now available。
- runtime correction is not implemented/accepted。
- the repository currently exposes several distinct progress metrics。
- no new lifecycle percentage should be inferred merely by arithmetic against one denominator without the accepted rebase procedure。

Global lifecycle / Blueprint totals must be rebased only through an explicit accepted lifecycle update。

No acceptance percentage is gained by this docs-only checkpoint。

---

## 11. Dependency / Execution Phases

### P0 — Persistence Baseline Verification

V06。

### P1 — Small Known Corrections

C01 -> C22 -> C11。

Weight：

10。

### P2 — Market Evidence Authority

C23 -> C24 -> C25。

Weight：

14。

### P3 — Account Authority Core

C02 -> C04 -> C21 -> C03。

Weight：

19。

### P4 — Submission Safety

C08 -> C05 -> C06。

Weight：

14。

### P5 — Broker Recovery Evidence

C07 -> C09 -> C10。

Weight：

15。

### P6 — Local Recovery / Reconciliation

C13 -> C12 -> C14 -> C15。

Weight：

18。

### P7 — Strategy Recovery Authority

C16 -> C17 -> C19 -> C20 -> C18。

Weight：

20。

### P8 — Broker Capability Verification

V01～V05。

Weight：

19。

Requires explicit authorization envelope for the applicable documentation/paper/production verification modes。

### P9 — Actual PostgreSQL Environment Verification

V07。

Weight：

4 conditional。

Requires explicit target-environment authorization。

---

## 12. CODEX Execution Rule

Phase is a context grouping only。

It is NOT permission to commit an entire phase as one uncontrolled change。

Default execution remains：

    one bounded leaf
    -> precheck
    -> implementation
    -> targeted tests
    -> relevant integration tests
    -> full regression
    -> git diff --check
    -> exact scope validation
    -> commit
    -> push
    -> verify
    -> stop / next authorization boundary

Same-context consecutive leaves may reuse architectural context，but each leaf keeps its own acceptance and failure boundary unless a future explicit Work Package proves an atomic merge is safer。

CODEX receives the bounded leaf contract rather than being asked to reinterpret all of R-01～R-14。

---

## 13. Deferred / Excluded From Current Correction Core

Explicitly deferred：

- full K520 / GAP-09 incremental feature-state implementation。
- full R14 / GAP-DATA-001 production completeness detector。
- full N/L production authentication / authorization / approval platform。
- server-side idempotent Shioaji resubmission dependency。
- quantity modification / amend / replace recovery。
- full LIVE safety stack。
- global timestamp rewrite。
- full strategy provisioning/config UI。
- cross-store redesign。
- backup / restore。
- retention/archive redesign。
- unrelated broker features。
- unrelated API/web/application work。

Deferred != waived。

Where a deferred production capability is mandatory for a production path，that path remains DEFAULT DENY / BLOCKED until evidence exists。

---

## 14. Runtime Authorization Boundary

After this Correction-Freeze Checkpoint，the next planning action is：

EXPLICIT BOUNDED RUNTIME AUTHORIZATION DECISION。

A future authorization must record at least：

- Authorization Baseline。
- Authorized Leaf Set。
- Runtime Modification Scope。
- Excluded / Deferred Scope。
- Environment Scope。
- DB Side Effects。
- Broker Network I/O。
- Broker Paper I/O。
- Production Broker I/O。
- Migration Execution。
- Capability Verification Modes。
- Required Tests。
- Stop Boundary。

A bare：

AUTHORIZED

is insufficient。

This correction-freeze document itself grants no runtime authority。

---

## 15. Checkpoint Result

Frozen Contract Assertion Inventory：

COMPLETE。

Delta-to-Contract Evidence Classification：

COMPLETE FOR CURRENT PLANNING。

Required Work Materialization：

COMPLETE。

Deduplication：

COMPLETE。

Dependency DAG：

COMPLETE。

Correction Weighting：

COMPLETE。

Expanded GAP-08 Reweight：

COMPLETE。

Correction-Freeze Planning：

COMPLETE。

Architecture Decision Baseline：

UNCHANGED。

Runtime Authorization：

NOT_AUTHORIZED。

Next：

Explicit Bounded Runtime Authorization Decision。
