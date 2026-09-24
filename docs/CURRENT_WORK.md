# Current Work

## Current Work Package

- ID：M0-A — Project Governance Scaffold
- Status：In review；文件已建立，尚未 commit。
- Scope：AI / Human 開發治理、交接、GAP 與進度文件。
- Runtime impact：無。不得修改 trading runtime behavior。

## Blockers

無 M0-A blocker。pytest TEMP permission 是已知環境 GAP，不影響純文件 Work Package 驗收。

## Pending Decisions

- M0-B：package boundary、canonical domain model、migration direction。
- GAP-07 pre-check：Instrument / Contract specification exact model。

## Confirmed V1 Decision

- `LogicalAccount != BrokerAccount`。
- 一個實體 BrokerAccount 可對應多個 LogicalAccount / CapitalBucket。
- V1 capital source：manual。
- Cross-strategy capital borrowing：default OFF；未來僅可由人工明確開啟。

## Next Queue

1. 人工 / architect review M0-A。
2. M0-B — Architecture Boundary ADR。
3. GAP-07 — Contract / Futures Specification。
4. Broker Account / Position Sync。
5. GAP-08 — Trading State Persistence & Recovery。

## Estimated Progress

- Overall V1：40–50%。
- M0-A：implementation complete，等待 review；commit 前不視為正式完成。
