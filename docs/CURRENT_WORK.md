# Current Work

## Current Work Package

- ID：GAP-07-E — Backtest / Risk Compatibility Resolution
- Status：Implemented / review pending；尚未 commit。
- Scope：建立 explicit override → canonical specification / margin schedule → explicit no-margin mode 的可追溯 resolution seam。
- Runtime impact：新增獨立 backtest compatibility resolver；未修改既有 config、RiskConfig、BacktestEngine、domain model、broker 或 database schema。

## Blockers

無 GAP-07-E blocker。pytest 使用 repository-local `.tmp/`；完整 regression 通過。

## Pending Decisions

- DuckDB margin schema refinement 與 future broker actual margin snapshot 仍待 approved slice。

## Confirmed V1 Decision

- `LogicalAccount != BrokerAccount`。
- 一個實體 BrokerAccount 可對應多個 LogicalAccount / CapitalBucket。
- V1 capital source：manual。
- Cross-strategy capital borrowing：default OFF；未來僅可由人工明確開啟。

## Next Queue

1. GAP-07 後續 approved slice。
2. GAP-BROKER-001 — explicit OrderIntent / PositionEffect。
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
- GAP-07-E：implemented / review pending。
