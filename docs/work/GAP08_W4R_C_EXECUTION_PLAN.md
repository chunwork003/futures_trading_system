# GAP-08 W4R-C Execution Plan

Status:

`FROZEN_FOR_BOUNDED_EXECUTION`

Dependencies:

- W4R-A ACCEPTED / FROZEN
- W4R-B ACCEPTED / FROZEN

Parent W4R-C weight:

`4`

No sub-leaf earns official or W4R-C weight independently.
W4R-C becomes accepted only after C1 + C2 both pass independent review.

## C1 — C13 Semantic Owner Reuse

Goal:

Make the trusted readiness path consume C13's semantic owner directly, without duplicate reconciliation-case SQL or caller-provided booleans.

Required call order:

1. `ReconciliationCaseRepository.unresolved(account)`
2. `blocking_case_state(...)`
3. build deterministic semantic blocker witness from the same returned versions.

No alternate currentness query.

### Semantic blocker witness

The witness must bind readiness-relevant case semantics only.

Include canonical unresolved case material such as:

- case_id;
- BrokerAccount;
- reconciliation result status/material;
- reconciliation policy;
- blocking case state.

Exclude audit-only version metadata:

- `ReconciliationCaseVersion.version`;
- `recorded_at`;
- `actor_ref`;
- version-level `evidence`.

A change in audit-only metadata must not alter the semantic blocker fingerprint.

A change in case identity, account, result/material, policy, or blocking state must alter it.

Legacy NULL BrokerAccount scope remains fail closed through the existing C13 repository.

Other-account cases must not block the requested account.

C1 does not modify C13's blocking semantics.

## C2 — Minimum Recovery-Root Exact Closure

Requires C1 accepted.

Goal:

Build the minimum complete canonical transitive closure of readiness-relevant Order roots.

Root union:

1. BrokerAccount-scoped nonterminal Orders;
2. Orders referenced by unresolved BrokerAction heads;
3. Orders referenced by accepted reconstruction receipts for the selected recovery world;
4. exact Order/Event dependency reachable from current expected snapshot provenance;
5. exact Order identity from pending/material broker reports only when resolvable without guessing.

For each root:

`Order -> complete Fill set -> complete canonical OrderEvent sequence -> linkage validation`

### Fill authority

- identity = immutable `fill_id`;
- exact canonical material comparison;
- exact `order_id` / `event_id` linkage;
- set equality by identity;
- same ID + same material = idempotent;
- same ID + different material = integrity failure.

### Event authority

- identity = immutable `event_id`;
- authoritative per-Order sequence;
- exact canonical event material;
- exact entity/order linkage;
- sequence uniqueness/continuity according to existing event contract;
- same identity + different material = integrity failure.

No account-history-wide scan.

Ambiguous broker report payload must not guess an Order.

## C boundary

C1/C2 do not:

- wire all readiness writers to shared fence (D);
- build final `TrustedReadinessEvidenceBundle` (D);
- evaluate C15 READY;
- finalize handoff;
- change C13 blocking semantics;
- change C10 economics;
- execute PostgreSQL/V07;
- perform broker I/O.

## Tooling policy

Repeated reparse-point/Git sandbox patch failures are now classified as a stable environment property.

For all C/D CODEX leaves:

`TOOLING_MODE = CONTROLLED_STAGING_ROOT_FIRST`

Meaning:

- do not first attempt the known-failing direct workspace patch route;
- immediately mirror only authorized writable files into one controlled staging root;
- patch there;
- synchronize back once;
- immediately run hash/diff/scope guard;
- do not count this planned route as a tooling retry.

Unexpected failure inside the controlled route is a tooling retry and must be reported.
