# GAP-08 W4R-C2B Authorization

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_C2B_ONLY`

Planning baseline:

`f5a41a6edade61be85cfb31d8ce76e5e8cc4e1a6`

Dependencies:

- W4R-A ACCEPTED / FROZEN
- W4R-B ACCEPTED / FROZEN
- W4R-C1 ACCEPTED / FROZEN
- W4R-C2A ACCEPTED / FROZEN

Execution plan:

`docs/work/GAP08_W4R_C2_EXECUTION_PLAN.md`

## Goal

Implement only the exact canonical recovery closure for every C2A root:

`Order -> all Fill rows -> complete ORDER event sequence`

Do not implement W4R-D, C15 READY, final bundle or handoff.

## Existing read ports to reuse

Use existing ports only:

- `OrderRepository.get(order_id)`
- `FillRepository.list_by_order(order_id)`
- `EventLedgerRepository.list_after("OMS","ORDER",order_id,-1,limit)`

Do not add a second recovery-specific Order/Fill/Event repository API unless the existing ports prove insufficient. If insufficient, STOP / REAUTHORIZATION.

No global history scan.

## C2B-1 Input authority

Resolver input is the accepted immutable `RecoveryRootSetEvidence`.

Require:

- canonical root-set fingerprint re-derives exactly;
- `order_ids` and `roots` remain one-to-one deterministic;
- ambiguous report ingress IDs are preserved in closure evidence;
- caller cannot pass additional root IDs outside C2A evidence.

C2B does not decide whether ambiguity is READY-safe; W4R-D owns that decision.

## C2B-2 Exact Order projection

For every C2A root:

- exact-read `OrderRepository.get(root.order_id)`;
- missing => `RecoveryClosureIntegrityError`;
- embedded `order.order_id` must equal root ID;
- Order canonical material participates in closure fingerprint.

Do not derive BrokerAccount ownership from Order material; C2A owns root scope.

## C2B-3 Complete canonical ORDER event sequence

For each exact root, read only that root's OMS/ORDER events.

The complete sequence must contain exactly:

`0 .. Order.version`

Requirements per envelope:

- `event_type == "ORDER_STATUS_CHANGED"`
- `source == "OMS"`
- `entity_type == "ORDER"`
- `entity_id == root.order_id`
- `idempotency_scope == "ORDER_EVENT:<order_id>"`
- exact event IDs unique
- exact sequences unique/contiguous
- no event beyond `Order.version`
- canonical event envelope must convert to canonical `OrderEvent`
- canonical payload fields must decode:
  - previous_status
  - status
  - broker_order_id
  - provenance
  - nested payload
- `validate_order_event_transition` succeeds from sequence 0 through final event
- final event:
  - sequence == `Order.version`
  - status == `Order.status`
  - correlation_id == `Order.correlation_id`
  - order_id == root.order_id

Read with a bounded limit sufficient to detect one extra event (`Order.version + 2`).

No full event-ledger scan.

## C2B-4 Complete Fill set

For each root:

- `FillRepository.list_by_order(root.order_id)`
- Fill IDs unique
- every `fill.order_id == root.order_id`
- every `fill.event_id` exists in the exact root event sequence
- every `fill.correlation_id == Order.correlation_id`
- every `fill.causation_id == fill.event_id`
- Fill canonical material participates in closure fingerprint

Economic closure:

- `Order.filled_quantity == sum(Fill.quantity)`
- zero Fill set requires `filled_quantity == 0`
- nonzero Fill set requires exact weighted average equal to `Order.average_fill_price`
- zero Fill set requires `Order.average_fill_price is None`
- nonzero Fill set requires `Order.average_fill_price is not None`

Do not invent missing Fill evidence from Order aggregate fields.

## C2B-5 Immutable closure evidence

Add resolver-produced immutable evidence binding at least:

- exact C2A `root_set_fingerprint`
- C2A account
- C2A recovery generation
- deterministic root order IDs
- ambiguous report ingress IDs carried forward unchanged
- deterministic per-root closure fingerprints
- deterministic full closure fingerprint

Full closure fingerprint must bind:

- exact root-set fingerprint
- canonical Order material
- canonical Fill material keyed by fill identity
- canonical authoritative TradingEvent envelopes in sequence order

Counts alone are never authority.

Caller-supplied closure fingerprint must be recomputed/ignored or rejected; caller cannot inject extra roots.

No `ready`, `finalize`, `handoff`, broker I/O or economic mutation surface.

## Required counterexamples first

1. missing root Order => fail closed;
2. returned Order embedded ID differs from root => fail closed;
3. missing sequence 0 => fail closed;
4. event sequence gap => fail closed;
5. duplicate sequence => fail closed;
6. event beyond Order.version => fail closed;
7. wrong event_type/source/entity_type/entity_id => fail closed;
8. wrong `ORDER_EVENT:<order_id>` idempotency scope => fail closed;
9. malformed canonical ORDER event payload => fail closed;
10. illegal lifecycle transition => fail closed;
11. final event status/version/correlation mismatch with Order => fail closed;
12. duplicate Fill ID => fail closed;
13. Fill wrong order ID => fail closed;
14. Fill references event outside exact sequence => fail closed;
15. Fill correlation mismatch => fail closed;
16. Fill causation mismatch => fail closed;
17. Order filled_quantity differs from Fill sum => fail closed;
18. average fill price differs from exact weighted Fill average => fail closed;
19. zero fills with nonzero filled_quantity/average price => fail closed;
20. exact same closure is deterministic regardless repository Fill return order;
21. changed canonical Fill/Event/Order material changes closure fingerprint;
22. ambiguous C2A report ingress IDs are carried forward unchanged;
23. caller cannot add root IDs/fingerprint;
24. no global Order/Fill/Event scan;
25. output has no READY/finalize/handoff surface.

## Exact writable files

Production:

- `persistence/recovery.py`

Tests:

- `tests/unit/test_c15_account_recovery_readiness.py`

Exactly these two files.

No new files.

## Protected / read only

Including but not limited to:

- `persistence/execution.py`
- `persistence/postgres/execution.py`
- `persistence/events.py`
- `persistence/postgres/event_ledger.py`
- `trading/execution.py`
- W4R-A/B/C1/C2A frozen code outside the exact writable section
- migrations
- docs
- broker network code
- `data/`

Need protected scope => `STOP / REAUTHORIZATION`.

## Test gates

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-c2b-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_operational_execution.py tests/unit/test_event_ledger.py tests/unit/test_c10_broker_reconstruction.py tests/unit/test_c12_recovery_cut.py tests/unit/test_c13_reconciliation_case_scope.py -q --basetemp .\.tmp\pytest-w4r-c2b-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-c2b-full
```

If production code changes after the full regression, rerun final full regression and report transparently.

## Tooling mode

`CONTROLLED_STAGING_ROOT_FIRST`

Use one controlled staging root containing exactly the two writable files.

Use the known-working route before first edit.

## Efficiency report

Report:

- actual changed files;
- approximate diff additions/deletions;
- semantic correction cycles;
- tooling retries;
- 5HR consumption.

Pytest count is verification, not workload.

## Git

Exactly one runtime commit:

`feat(recovery): validate W4R-C2B exact execution closure`

Before push:

- origin/master must still equal the C2B authorization baseline;
- no amend/rebase/force push.

Push once then STOP reviewer.

## Side effects

ALLOW:

- exact two-file source/test change;
- local tests;
- one commit/push.

DENY:

- W4R-D;
- C15 READY/final handoff;
- global Order/Fill/Event history scans;
- repository/migration changes outside exact scope;
- migration execution;
- actual PostgreSQL/V07;
- A08;
- broker/paper/Shioaji I/O;
- production;
- P7;
- W4 closure/credit.
