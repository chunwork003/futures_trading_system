# GAP-08 W4 Replan V2 — Trusted Readiness Authority

Planning baseline: `b1cde840e63353ed629108b43074fa5394d092c4`

Status: `VIBE_REPLAN_CANDIDATE / NO_EXECUTOR_CODING_AUTHORIZED`

## 1. V2 optimization
V1 proposed a separate `ReadinessWorldHead`。V2 removes it。

Reason:
- `AccountRecoveryControl` already owns active recovery generation and handoff fencing。
- Architect requires a shared currentness/CAS fence，not a new business authority。
- Avoid creating a second readiness/economic head。

V2 adds a dedicated `readiness_revision` to `AccountRecoveryControl`。
`ingress_version` keeps its broker-ingress-only meaning and must not be repurposed。

## 2. Shared recovery fence
`AccountRecoveryControl` becomes:

- broker
- account_ref
- generation
- recovery_cut_revision
- ingress_version
- readiness_revision
- active
- recorded_at

`readiness_revision`:
- starts at 0 for a recovery generation。
- increments whenever a readiness-relevant durable writer commits while recovery is active。
- is not economic authority。
- is not continuity authority。
- only fences same-account readiness world changes。

Final handoff locks the active control row and resolves trusted evidence inside the same transaction。

## 3. Continuity authority
Add durable `ExecutionContinuityHead`:

- broker
- account_ref
- head_revision
- generation
- epoch_id
- transition_receipt_id

Add append-only `ContinuityTransitionReceipt` binding:

- BrokerAccount
- old/new head revision
- generation
- epoch ID
- anchor fingerprint
- ingress frontier
- readiness revision
- account revision
- expected snapshot
- authority commit
- gap semantic fingerprint
- producer ID
- contract version
- evidence ID

Rules:
- exactly one current continuity head per BrokerAccount。
- timestamps / lexical epoch ordering never select current。
- once head advances，old trusted epoch immediately loses READY eligibility。
- later untrusted current epoch must not fall back to an older trusted epoch。

## 4. Durable C07 discovery authority
Add append-only `BrokerDiscoveryReceipt` keyed by exact `discovery_run_id`。

Persist canonical `BrokerDiscoveryResult` material + deterministic fingerprint + producer/contract version。

C14 continues to bind exact `discovery_run_id`。
No latest fallback。

Same ID + same material = idempotent。
Same ID + different material = integrity conflict。

## 5. Durable C10 reconstruction authority
Add append-only positive `BrokerReconstructionReceipt` containing:

- receipt ID
- BrokerAccount
- discovery_run_id
- recovery generation
- RecoveryCut fingerprint
- canonical input coverage fingerprint
- exact accepted Fill IDs
- resulting Order/economic fingerprint
- deal-set completeness
- producer/contract identity
- optional authority_commit_id

Missing required positive receipt => REVIEW。
Durable identity/material conflict => HALT。

## 6. Trusted capability provider
Reuse existing `BrokerCapabilityMatrix` and Sinopac matrix。

Add trusted immutable registry snapshot/provider with:

- registry ID
- contract/version
- broker
- deterministic matrix fingerprint
- SDK version
- exact capability entries
- verification modes
- source IDs

Do not add a PostgreSQL capability table in W4R unless implementation evidence proves runtime mutability is required。

Documentation evidence never implies PRODUCTION verification。

## 7. TrustedReadinessEvidenceBundle
Production readiness path accepts resolver-produced authority，not arbitrary caller DTOs。

Bundle binds:

- BrokerAccount
- generation
- ingress_version
- readiness_revision
- RecoveryCut fingerprint
- AccountStateHead revision
- expected snapshot ID
- authority commit ID
- continuity head revision
- current epoch ID
- transition receipt fingerprint
- semantic SequenceGap fingerprint
- durable discovery receipt fingerprint
- exact broker observation fingerprint
- reconstruction receipt fingerprints
- C13 blocking state + semantic blocker fingerprint
- C14 boundary/outcome fingerprints
- recovery-root closure fingerprint
- BrokerAction semantic fingerprint
- broker report disposition fingerprint
- capability registry ID/version/fingerprint
- requested verification environment

Derived booleans may exist only as cached classifications；they are not trust roots。

## 8. C13 reuse
C15 must directly call:

`ReconciliationCaseRepository.unresolved(account)`

then:

`blocking_case_state(...)`

No duplicate C15 latest/scoped/blocking SQL。

Legacy NULL BrokerAccount scope stays fail-closed。
Explicit other-account cases do not block current account。

Readiness witness includes only semantic blocker material，not audit-only metadata。

## 9. Formal completeness
Caller `expected_complete/actual_complete` booleans are not authority。

Resolver loads exact:

- expected snapshot by C14 `expected_snapshot_id`
- broker observation by C14 `observation_id`
- C14 boundary
- C14 outcome

Completeness is derived from those complete-batch contracts。

Empty/empty is valid only when both exact batches exist and the same C14 run is qualified/completed。

## 10. Minimum recovery-root transitive closure
Roots are the union of:

1. account-scoped non-terminal Orders。
2. Orders referenced by unresolved BrokerAction heads。
3. Orders referenced by accepted reconstruction receipts for this recovery world。
4. exact Order/Event dependency reachable from current expected snapshot provenance。
5. exact Order identity referenced by pending/material broker report when resolvable。

Ambiguous report payload must not guess an Order；readiness remains REVIEW/HALT according to report semantics。

For each root:
`Order -> complete Fill set -> complete canonical OrderEvent sequence -> linkage validation`

Fill comparison:
identity-keyed set by `fill_id` + canonical material。

Event comparison:
per-Order authoritative sequence equality + exact event identity/material。

Same identity + same material = idempotent。
Same identity + different material = HALT。

Do not scan all account history。

## 11. Readiness-relevant writers
While recovery is active，these writers increment `readiness_revision` in the same UoW:

- AccountAuthorityCommit
- broker position observation append
- broker report inbox
- broker report application
- SequenceGap append
- ContinuityHead transition/re-anchor
- BrokerAction head reserve/resolve
- C13 case append/resolve
- C07 discovery receipt append
- C10 reconstruction receipt append
- C14 run establish/finalize

Order/Fill/Event writes already inside one AccountAuthorityCommit cause one readiness revision，not one per row。

Capability registry is process-immutable and re-fingerprinted at final resolution；no DB revision writer。

## 12. Final handoff transaction
One PostgreSQL UoW:

1. lock active `AccountRecoveryControl FOR UPDATE`
2. capture generation / ingress_version / readiness_revision
3. resolve AccountStateHead/checkpoint/receipt
4. resolve ContinuityHead/transition/epoch/gaps
5. resolve broker report disposition
6. resolve BrokerAction state
7. call C13 unresolved + blocking
8. resolve durable C07 receipt
9. resolve exact expected snapshot
10. resolve exact broker observation
11. resolve C10 reconstruction receipts
12. resolve C14 boundary/outcome
13. build exact recovery closure
14. resolve capability registry
15. build TrustedReadinessEvidenceBundle
16. run pure C15 evaluator
17. if not READY => rollback/no handoff
18. recheck locked recovery control values
19. finalize C09 handoff in same UoW
20. commit

No broker I/O occurs in this transaction。

All readiness-relevant writers must lock/update the same active recovery-control row before commit，preventing TOCTOU。

## 13. Migration
Do not modify migrations 0001–0008。

New:
`persistence/postgres/migrations/0009_trusted_readiness_authority.sql`

Planned DDL:

1. add `readiness_revision BIGINT NOT NULL DEFAULT 0 CHECK (readiness_revision >= 0)` to `account_recovery_controls`
2. create continuity transition receipts
3. create continuity heads
4. create broker discovery receipts
5. create broker reconstruction receipts
6. required FK/unique/index constraints

No migration-time inference of current continuity head。
No fabricated C07/C10 history。
Missing new authority => fail closed / require fresh recovery evidence。

## 14. Package DAG

```text
W4R-A
Shared recovery fence + ContinuityHead + migration 0009
        |
        +---------------------+
        |                     |
        v                     v
W4R-B                    W4R-C
C07/C10 durable          C13 reuse +
receipts + trusted       recovery closure
resolver + capability
        |                     |
        +----------+----------+
                   |
                   v
W4R-D
Trusted bundle + final atomic handoff + C15 integration
                   |
                   v
isolated PostgreSQL integration/concurrency
                   |
                   v
independent review -> W4 closure
```

## 15. Provisional weights
Official accounting remains `75/113` until governance accepts a rebase。

Proposal:

- W4R-A = 7
- W4R-B = 7
- W4R-C = 6
- W4R-D = 8
- total = 28

Original W4 = 18，net expansion = +10。

If accepted:
- correction core 113 -> 123
- current accepted remains 75
- after W4R closure = 103/123
- P7 remains 20
- after P7 = 123/123

This is planning only。

## 16. Mandatory counterexamples
- stale trusted old epoch after newer untrusted epoch
- EPOCH-1 vs EPOCH-10 exact identity
- forged/nonexistent capability source
- typed completeness without exact batches
- typed reconstruction without durable receipt
- legacy NULL-scope C13 case
- explicit other-account C13 case
- cross-world evidence bundle
- duplicate identity/different material
- concurrent broker inbox during final handoff
- concurrent C13 case write
- concurrent BrokerAction write
- concurrent continuity-head write
- DB operational error propagation
- programming TypeError propagation

## 17. PostgreSQL verification
Every package:
- unit/fake SQL
- targeted/compatibility tests

Before W4 closure:
- isolated PostgreSQL repository integration
- real transaction/CAS concurrency tests for shared recovery fence

A08-style crash/concurrency verification is recommended as mandatory for W4 closure because race-free handoff is the central new claim。

Actual environment V07 remains separate and NOT_RUN。
Broker I/O remains prohibited。

## 18. STOP / reauthorization boundaries
STOP if implementation requires:

- changing C07 classification semantics
- changing C10 economic semantics
- changing C13 blocking semantics
- changing C14 formal-run semantics
- repurposing ingress_version
- modifying migrations 0001–0008
- broker I/O inside readiness transaction
- timestamp/lexical current authority
- production capability inference
- P7 changes
- accepted authority-owner conflict

## 19. Recommended next sequence
1. Materialize this replan + AI operating model。
2. Normalize CURRENT_WORK / ACTIVE current sections into parseable state。
3. Run Level 3A scheduler preflight。
4. Materialize bounded authorization for **W4R-A only**。
5. CODEX executes A。
6. Automated result intake + VIBE independent review。
7. Repeat B/C/D。
8. Escalate GPT-6 only for new cross-architecture contradiction。

`REPLAN_STATUS = VIBE_READY_FOR_GOVERNANCE_FREEZE`

`NO_EXECUTOR_CODING_AUTHORIZED`

`NO_RUNTIME_AUTHORIZATION_GRANTED`
