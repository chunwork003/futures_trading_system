# Current Work

## Current Work Package

- ID：GAP-07-CLOSE Stage B — Final Acceptance
- Status：COMPLETE；GAP-07 CLOSED。
- Scope：確認 canonical market specification inventory、actual consumer wiring、broker mapping seam 與 architecture boundaries。
- Runtime impact：無；Stage B 僅執行 acceptance、regression 與 governance closure。

## Blockers

無 blocker。Final regression 745 passed；GAP-07 closure criteria 全部通過。

## Pending Decisions

- DuckDB margin schema refinement 與 future broker actual margin snapshot 仍待 approved slice。
- Legacy `Order.contract` 仍直接作為 broker lookup key；依 GAP-BROKER-001 與 execution migration 後續處理。
- Broker capability matrix 與 mapping persistence 仍待 GAP-BROKER-002 後續 slice。

## Confirmed V1 Decision

- `LogicalAccount != BrokerAccount`。
- 一個實體 BrokerAccount 可對應多個 LogicalAccount / CapitalBucket。
- V1 capital source：manual。
- Cross-strategy capital borrowing：default OFF；未來僅可由人工明確開啟。

## Next Queue

1. Broker Account / Position Sync + Reconciliation。
2. GAP-BROKER-001 — explicit OrderIntent / PositionEffect。
3. GAP-BROKER-002 — broker capability matrix / remaining mapping semantics。
4. GAP-08 — Trading State Persistence & Recovery。
5. GAP-09 — Incremental Feature / Market State Engine。

## Estimated Progress

- Overall V1：40–50%。
- GAP-07-A0：COMPLETE。
- GAP-07-A：COMPLETE。
- GAP-07-B：COMPLETE。
- GAP-07-C：COMPLETE。
- GAP-07-D：COMPLETE。
- GAP-07-E：COMPLETE。
- GAP-07-F：COMPLETE。
- GAP-07-E2：COMPLETE。
- GAP-07-E3：COMPLETE。
- GAP-07：CLOSED。
