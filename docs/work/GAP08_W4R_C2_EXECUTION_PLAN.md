# GAP-08 W4R-C2 Execution Plan

Status:

`FROZEN_FOR_BOUNDED_EXECUTION`

Dependencies:

- W4R-A ACCEPTED / FROZEN
- W4R-B ACCEPTED / FROZEN
- W4R-C1 ACCEPTED / FROZEN

Parent W4R-C weight:

`4`

W4R-C remains uncredited until C2A + C2B both pass independent review.

## Why C2 is split

The remaining C responsibility contains two different correctness problems:

1. determine the minimum exact recovery-root Order set;
2. validate the complete canonical Order -> Fill -> Event transitive closure.

They are separated to reduce CODEX context and reviewer ambiguity.

## C2A — Recovery Root Authority

Goal:

Resolve the deterministic minimum Order root set without global account-history scans and without guessing BrokerAccount scope.

### Existing scope owner

`Order` itself has no BrokerAccount field.

The existing durable BrokerAccount -> Order scope authority already used by C12 is:

`BrokerActionHead(broker, account_ref, order_id, action)`

Therefore C2A must reuse BrokerActionHead account scope rather than scan all `trading.orders`.

A global Order scan is forbidden.

If a required account-scoped Order cannot be reached from an existing durable scope/provenance owner, fail closed / require reauthorization; do not infer account ownership.

### Root union

C2A root set is the deterministic union of:

1. nonterminal Orders reachable through BrokerAccount-scoped BrokerActionHead authority;
2. Orders referenced by unresolved BrokerAction heads, including terminal projection if the unresolved action still exists;
3. Orders referenced by exact accepted B1 reconstruction receipts selected by the B2 trusted core;
4. exact Order dependency of the current expected snapshot source event;
5. exact Order ID carried by a current material broker-report entry when the report payload provides an explicit unambiguous canonical `order_id`.

### Expected snapshot root

C2A re-reads the B2 core exact expected snapshot.

Its `source_event_id` must resolve through the event ledger to an exact canonical ORDER event envelope.

Required:

- event exists;
- `entity_type == ORDER`;
- event entity/order identity is nonblank;
- source-event relation is exact.

Missing or non-ORDER source event => fail closed.

### Broker report roots

C2A does not decide report currentness/disposition; W4R-D owns the same-world report selection.

C2A provides deterministic root extraction for report entries supplied by that final resolver.

For every supplied material report entry:

- account/generation must match the trusted recovery world;
- explicit string `payload_json.order_id` => canonical root;
- missing order_id => mark ingress as ambiguous, never guess;
- malformed/non-string order_id => integrity failure.

Ambiguous material report IDs are preserved in C2A output so W4R-D cannot silently READY.

### Root evidence output

Resolver-produced immutable evidence should bind:

- BrokerAccount;
- recovery generation;
- deterministic root Order IDs;
- per-root provenance/source categories;
- ambiguous material report ingress IDs;
- deterministic full root-set fingerprint.

Duplicate root IDs from multiple sources are deduplicated, but all source categories remain bound to that root.

## C2B — Exact Order / Fill / Event Closure

Requires C2A accepted.

Goal:

For every C2A root, build and validate the complete canonical closure:

`Order -> all Fill rows -> complete ORDER event sequence`

### Order

Each root ID must resolve to one exact Order projection.

Missing root Order => integrity failure.

### Fill

Read all Fills by exact order_id.

For every Fill:

- fill_id unique;
- fill.order_id == root order_id;
- fill.event_id references an event in the same root event sequence;
- fill.correlation_id matches Order/event correlation;
- fill.causation_id == producing event_id;
- canonical material participates in closure fingerprint.

### Event

Read canonical ORDER ledger events for the root from sequence 0.

Require:

- event_type == ORDER_STATUS_CHANGED;
- source == OMS;
- entity_type == ORDER;
- entity_id == root order_id;
- idempotency_scope == `ORDER_EVENT:<order_id>`;
- exactly one event for each sequence 0..Order.version;
- no gap/duplicate sequence;
- canonical envelope converts to canonical OrderEvent material;
- `validate_order_event_transition` succeeds across the full sequence;
- final event status/correlation/sequence agrees with Order projection.

### Fill/economic closure

At minimum:

- Order.filled_quantity == sum(Fill.quantity);
- zero fills implies filled_quantity == 0;
- nonzero fill set must be consistent with final Order projection material.

Do not derive account ownership from Order material.

### Fingerprint

Produce deterministic closure fingerprint over:

- exact root evidence fingerprint;
- canonical Orders;
- canonical identity-keyed Fill sets;
- canonical authoritative event sequences.

Count alone is never authority.

## No global history scan

C2 may only read:

- exact root Orders;
- Fill sets for exact root IDs;
- event sequences for exact root IDs.

No full account event/fill/order history scan.

## Boundary

C2 does not:

- wire all readiness-relevant writers to readiness_revision;
- build final TrustedReadinessEvidenceBundle;
- evaluate C15 READY;
- finalize handoff;
- execute PostgreSQL/V07;
- perform broker I/O.

Those remain W4R-D.

## Tooling

All C2/D leaves use:

`CONTROLLED_STAGING_ROOT_FIRST`

Do not attempt the known-failing workspace patch route before the controlled path.
