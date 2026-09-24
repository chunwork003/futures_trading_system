# Current Work

## Current Work Package

- ID：M0-B — Architecture Boundary ADR
- Status：Final documentation / commit pending；ADR-001 已 ACCEPTED。
- Scope：canonical package / domain boundary、dependency direction 與漸進式 migration design。
- Runtime impact：無。不得開始 runtime refactor。

## Blockers

無 M0-B blocker。pytest TEMP permission 是已知環境 GAP，不影響純文件 Work Package 驗收。

## Pending Decisions

- GAP-07 pre-check：Instrument / Contract specification exact model。

## Confirmed V1 Decision

- `LogicalAccount != BrokerAccount`。
- 一個實體 BrokerAccount 可對應多個 LogicalAccount / CapitalBucket。
- V1 capital source：manual。
- Cross-strategy capital borrowing：default OFF；未來僅可由人工明確開啟。

## Next Queue

1. GAP-07 — Contract / Futures Specification Pre-check。
2. GAP-BROKER-001 — explicit OrderIntent / PositionEffect。
3. Broker Account / Position Sync。
4. GAP-08 — Trading State Persistence & Recovery。
5. GAP-09 — Incremental Feature / Market State Engine。

## Estimated Progress

- Overall V1：40–50%。
- M0-B：architecture design complete；final documentation commit pending。
