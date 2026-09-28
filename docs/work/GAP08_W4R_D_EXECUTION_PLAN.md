# GAP-08 W4R-D Execution Plan

Status:

`FROZEN_FOR_BOUNDED_EXECUTION`

Dependencies:

- W4R-A ACCEPTED / FROZEN
- W4R-B ACCEPTED / FROZEN
- W4R-C ACCEPTED / FROZEN

Parent W4R-D internal weight:

`5`

Official W4 correction credit remains zero until W4 final independent review.

## Why D is split

W4R-D contains four distinct risk classes:

1. make every remaining readiness-relevant writer participate in the same currentness fence;
2. bind all accepted evidence into one same-world trusted bundle;
3. perform pure C15 readiness evaluation from that trusted bundle;
4. finalize C09 handoff atomically under the same PostgreSQL transaction and prove concurrency safety.

Combining them into one CODEX package would enlarge context and make reviewer failures ambiguous.

D is therefore split into:

`D1A -> D1B -> D2 -> D3`

No leaf independently receives official correction-core credit.

## D1A — Shared Fence Primitive + Account Authority Writers

Goal:

Create one reusable transaction-local recovery-readiness fence primitive and wire:

- `AccountAuthorityCommit`;
- broker position observation append.

Because BrokerAction reserve/resolve and Order/Fill/Event/snapshot mutations are already AccountAuthorityCommit participants, D1A's single outer fence covers them without a second BrokerAction-specific increment.

Required transaction order for a new material AccountAuthorityCommit:

1. exact stable receipt duplicate/conflict precheck;
2. lock active BrokerAccount recovery-control row, if one exists;
3. lock account authority head;
4. execute material participants;
5. checkpoint/head/receipt writes;
6. validate authority closure;
7. advance locked readiness revision exactly once if recovery was active;
8. commit.

Exact duplicate/no-op AccountAuthorityCommit does not lock/advance the readiness fence.

Material failure rolls back all writes and the readiness advancement.

Broker position observation append follows:

1. lock active recovery fence if present;
2. append exact observation + items;
3. advance once if active;
4. caller-owned commit.

No active recovery control means no readiness advancement; the ordinary material write may continue as a post-/non-recovery write.

No repository may commit internally.

## D1B — C13 / C14 Writer Participation

Requires D1A accepted.

Wire the same frozen readiness-fence primitive into:

- C13 reconciliation-case append/resolution history;
- C14 run establish;
- C14 terminal finalize.

Rules:

- fence lock occurs before first readiness-relevant material write;
- exact C14 duplicate boundary/outcome does not advance readiness;
- genuinely new semantic durable material advances exactly once;
- no C13 blocking semantics change;
- no C14 formal-run semantics change;
- no duplicate C15 SQL.

## D2 — TrustedReadinessEvidenceBundle

Requires D1A + D1B accepted.

Build resolver-produced immutable same-world bundle binding the already accepted evidence:

- BrokerAccount;
- active recovery generation;
- ingress_version;
- readiness_revision;
- exact RecoveryCut fingerprint;
- AccountStateHead/checkpoint/authority receipt;
- continuity head/epoch/transition receipt/gap semantic fingerprint;
- broker report current disposition;
- BrokerAction semantic state;
- C1 reconciliation blocker evidence;
- B1/B2 discovery/reconstruction/expected/observation/capability evidence;
- exact C14 boundary/outcome;
- C2 root-set and execution-closure fingerprints.

D2 is pure trusted resolution/bundle construction.

D2 does not finalize C09 handoff and does not commit.

Caller-provided booleans/fingerprints cannot substitute for repository re-resolution.

## D3 — C15 Integration + Atomic Final Handoff

Requires D2 accepted.

One caller-owned PostgreSQL UoW:

1. lock active AccountRecoveryControl;
2. capture generation / ingress / readiness / cut;
3. re-resolve all D2 trusted evidence under that lock;
4. build trusted bundle;
5. run pure C15 evaluator;
6. non-READY => rollback/no handoff;
7. READY => recheck exact locked control witness;
8. finalize C09 handoff in same UoW;
9. commit.

No broker I/O.

D3 source/unit work does not itself authorize actual PostgreSQL/V07.

Before W4 closure, a separately authorized isolated PostgreSQL concurrency verification gate is still required.

## Frozen writer coverage map

Already covered before D:

- broker report inbox;
- broker report application;
- SequenceGap;
- continuity transition/re-anchor;
- C07 discovery receipt;
- C10 reconstruction receipt.

D1A adds:

- AccountAuthorityCommit:
  - Order;
  - Fill;
  - OrderEvent;
  - expected snapshot;
  - BrokerAction reserve/resolve participants;
- broker position observation.

D1B adds:

- C13 reconciliation case append/resolve;
- C14 establish/finalize.

After D1B, all writer classes listed by W4 Replan V2 must participate in the shared readiness fence.

## STOP boundaries

STOP / REAUTHORIZATION if implementation requires:

- modifying migrations 0001-0009;
- changing C07 semantics;
- changing C10 economics;
- changing C13 blocking semantics;
- changing C14 formal-run semantics;
- repurposing ingress_version;
- broker I/O;
- actual PostgreSQL/V07;
- production capability inference;
- P7;
- changing accepted A/B/C evidence semantics.
