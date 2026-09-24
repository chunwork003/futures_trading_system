# Current Work

## Current Work Package

- ID：GAP-07-CLOSE Stage A — Canonical Margin Actual Consumer Wiring
- Status：COMPLETE；Stage A commit pending。
- Scope：將 explicit/canonical/no-margin resolution 接入 `BacktestEngine` initialization 與既有 `PortfolioRiskManager` consumer。
- Runtime impact：新增 deterministic `from_specifications(..., as_of_date=...)` entry point；legacy constructor/config 行為不變，未修改 broker、database 或 domain。

## Blockers

無 Stage A blocker。targeted 與完整 regression 通過；下一步為 GAP-07 final acceptance / closure。

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

1. GAP-07 final acceptance / closure（本 Bundle Stage B）。
2. Broker Account / Position Sync + Reconciliation。
3. GAP-BROKER-001 — explicit OrderIntent / PositionEffect。
4. GAP-BROKER-002 — broker capability matrix / remaining mapping semantics。
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
- GAP-07-E2：COMPLETE。
- GAP-07-E3：COMPLETE。
