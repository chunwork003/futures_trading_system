# Current Work

## Current Work Package

- ID：GAP-07-C — Canonical Trading Session Reference
- Status：Implemented / review pending；尚未 commit。
- Scope：broker-neutral `TradingSessionRef` 與 canonical session interval `[open, close)`。
- Runtime impact：新增 domain reference，並將 `Session.contains()` close boundary 改為 exclusive；未改 Resolver / Normalizer trade-date logic。

## Blockers

無 GAP-07-C blocker。pytest 使用 repository-local `.tmp/`；完整 regression 通過。

## Pending Decisions

- GAP-07-D 之 effective-dated Margin Schedule exact model。

## Confirmed V1 Decision

- `LogicalAccount != BrokerAccount`。
- 一個實體 BrokerAccount 可對應多個 LogicalAccount / CapitalBucket。
- V1 capital source：manual。
- Cross-strategy capital borrowing：default OFF；未來僅可由人工明確開啟。

## Next Queue

1. GAP-07-D — Margin Schedule。
2. GAP-BROKER-001 — explicit OrderIntent / PositionEffect。
3. Broker Account / Position Sync。
4. GAP-08 — Trading State Persistence & Recovery。
5. GAP-09 — Incremental Feature / Market State Engine。

## Estimated Progress

- Overall V1：40–50%。
- GAP-07-A0：COMPLETE。
- GAP-07-A：COMPLETE。
- GAP-07-B：COMPLETE。
- GAP-07-C：implemented / review pending。
