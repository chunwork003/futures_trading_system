# Current Work

## Current Work Package

- ID：GAP-07-F — BrokerInstrumentReference / Broker Mapping Contract
- Status：Implemented / review pending；尚未 commit。
- Scope：建立 broker-neutral `BrokerInstrumentReference`、effective-date resolver 與 SINOPAC native lookup compatibility seam。
- Runtime impact：新增 domain mapping contract，並在既有 Shioaji contract helper 增加薄 seam；未修改 Order、ShioajiBroker lifecycle、broker account 或 database。

## Blockers

無 GAP-07-F blocker。pytest 使用 repository-local `.tmp/`；完整 regression 通過。

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

1. GAP-BROKER-001 — explicit OrderIntent / PositionEffect。
2. GAP-BROKER-002 — broker capability matrix / remaining mapping semantics。
3. Broker Account / Position Sync。
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
- GAP-07-F：implemented / review pending。
