# Current Work

## Current Work Package

- ID：GAP-07-D — Canonical Margin Schedule and Effective-Date Resolver
- Status：Implemented / review pending；尚未 commit。
- Scope：broker-neutral `MarginScheduleEntry`、effective-date lookup、contract-specific precedence 與 duplicate ambiguity detection。
- Runtime impact：新增獨立 domain model/resolver；未修改 RiskConfig、BacktestEngine、broker 或 database schema。

## Blockers

無 GAP-07-D blocker。pytest 使用 repository-local `.tmp/`；完整 regression 通過。

## Pending Decisions

- DuckDB margin schema refinement 與 future broker actual margin snapshot 仍待 approved slice。

## Confirmed V1 Decision

- `LogicalAccount != BrokerAccount`。
- 一個實體 BrokerAccount 可對應多個 LogicalAccount / CapitalBucket。
- V1 capital source：manual。
- Cross-strategy capital borrowing：default OFF；未來僅可由人工明確開啟。

## Next Queue

1. GAP-07-E — Backtest / Risk compatibility adapter。
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
- GAP-07-D：implemented / review pending。
