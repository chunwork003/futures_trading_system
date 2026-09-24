# Current Work

## Current Work Package

- ID：GAP-07-E2 — Actual Backtest / Risk Consumer Integration
- Status：Implemented / review pending；尚未 commit。
- Scope：將 canonical multiplier resolution 接入 `BacktestEngine` initialization，建立單一 run-time config 並供既有 Portfolio、PnL、cost 與 position-sizing path 使用。
- Runtime impact：新增 optional canonical factory 與 resolved multiplier traceability；legacy constructor/config 行為不變。未接 margin consumer，未修改 broker、database 或 domain。

## Blockers

無 GAP-07-E2 blocker。pytest 使用 repository-local `.tmp/`；完整 regression 通過。

## Pending Decisions

- DuckDB margin schema refinement 與 future broker actual margin snapshot 仍待 approved slice。
- Legacy `Order.contract` 仍直接作為 broker lookup key；依 GAP-BROKER-001 與 execution migration 後續處理。
- Broker capability matrix 與 mapping persistence 仍待 GAP-BROKER-002 後續 slice。
- GAP-07-E3：margin actual consumer wiring 需先建立 deterministic `as_of_date` injection；不得使用 hidden current date。

## Confirmed V1 Decision

- `LogicalAccount != BrokerAccount`。
- 一個實體 BrokerAccount 可對應多個 LogicalAccount / CapitalBucket。
- V1 capital source：manual。
- Cross-strategy capital borrowing：default OFF；未來僅可由人工明確開啟。

## Next Queue

1. GAP-07-E3 — Margin actual consumer wiring。
2. GAP-BROKER-001 — explicit OrderIntent / PositionEffect。
3. GAP-BROKER-002 — broker capability matrix / remaining mapping semantics。
4. Broker Account / Position Sync。
5. GAP-08 — Trading State Persistence & Recovery。

## Estimated Progress

- Overall V1：40–50%。
- GAP-07-A0：COMPLETE。
- GAP-07-A：COMPLETE。
- GAP-07-B：COMPLETE。
- GAP-07-C：COMPLETE。
- GAP-07-D：COMPLETE。
- GAP-07-E：COMPLETE。
- GAP-07-F：COMPLETE。
- GAP-07-E2：implemented / review pending。
