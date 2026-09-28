# GAP-08 W4R-C2A Independent Review — RF01 Required

Reviewed runtime candidate:

`cdd979d6fe46b161b9376f6c58c14ed1aa90e749`

Execution baseline:

`6eb931637c0e9d1b0bb54e9311ec56150b4b70ab`

Disposition:

`HOLD / W4R_C2A_RF01_REQUIRED`

Official correction-core acceptance remains:

`75 / 113`

W4 weight remains:

`18 / NOT_CREDITED`

W4R-A / W4R-B / W4R-C1 remain:

`ACCEPTED / FROZEN / READ_ONLY`

## Mechanical result

PASS:

- exactly one C2A runtime commit;
- master == runtime candidate;
- exactly six authorized files changed;
- no migration changes;
- no actual PostgreSQL/V07/A08/broker I/O claimed;
- governance docs unchanged by runtime commit;
- executor stopped before C2B/D.

Executor evidence:

- targeted = 95 passed;
- compatibility = 42 passed;
- final full regression = 1310 passed / 4 skipped;
- correction-driven full regression rerun = same result;
- semantic correction cycles = 2;
- tooling retries = 0;
- diff ~= +224 / -3;
- user-observed 5HR consumption = 17%.

## Accepted C2A work retained

Retain:

- BrokerAccount-scoped `BrokerActionRepository.list_heads`;
- deterministic PostgreSQL `ORDER BY order_id, action`;
- no global Order scan;
- nonterminal head-owned Orders as roots;
- unresolved BrokerAction Orders remain roots even when terminal;
- terminal resolved head alone is excluded;
- exact B2 reconstruction receipt ID/full-fingerprint binding;
- exact expected snapshot source-event root concept;
- explicit material report `order_id` extraction;
- missing report `order_id` preserved as ambiguous ingress;
- malformed report identity fail closed;
- deterministic root dedupe with all source categories;
- resolver-derived root-set fingerprint;
- no READY/finalize/handoff surface.

## Material blocker — Exact read identity closure is incomplete

C2A correctly calls exact-read repository APIs, but the resolver does not positively verify all decoded identities returned by those repositories.

### BrokerAction -> Order

For every `BrokerActionHead`, the resolver calls `OrderRepository.get(head.order_id)` and checks only for `None`. It must also require:

`order.order_id == head.order_id`

Otherwise a row selected by one durable Order ID can decode a mismatched projection JSON and silently replace the BrokerAccount-owned root with another Order ID.

### Trusted core -> Expected snapshot

After exact snapshot re-read require:

- `snapshot.snapshot_id == trusted_core.expected_snapshot_id`;
- `(snapshot.broker, snapshot.account_ref) == trusted_core.account`.

Missing or mismatched snapshot must fail closed.

### Expected snapshot -> Source event

After `EventLedgerRepository.get(snapshot.source_event_id)` require:

- event exists;
- `event.event_id == snapshot.source_event_id`;
- `event.entity_type == "ORDER"`.

Only then may canonical `event.entity_id` become the root.

## Required counterexamples first

1. head asks for `ORDER-1`, repository returns `Order(order_id="ORDER-2")` => fail closed;
2. expected core asks for `SNAP-1`, repository returns `SNAP-2` => fail closed;
3. expected snapshot account differs from trusted core account => fail closed;
4. snapshot source_event_id is `EVENT-1`, repository returns ORDER event `EVENT-2` => fail closed;
5. exact matching Order/snapshot/event preserves the same deterministic root set;
6. no READY/finalize/handoff surface;
7. no global Order/history scan.

## Boundary

This does not reopen B1/B2 and does not change BrokerAction, EventLedger, Order repository, C10, C13/C14, C2B, or W4R-D semantics.

W4R-C2A remains unaccepted.
W4R-C2B/D remain NOT_AUTHORIZED.
No GPT-6 escalation is required.
