# Current Work

## Current Work Package

- ID：GAP-07-A — Canonical Instrument Specification
- Status：Implemented / review pending；尚未 commit。
- Scope：broker-neutral `InstrumentSpec`、既有 `domain.Instrument` compatibility、canonical identity 與 linear tick value derived behavior。
- Runtime impact：新增 canonical model 與 legacy conversion；未遷移既有 consumer。

## Blockers

無 GAP-07-A blocker。pytest 使用 repository-local `.tmp/`；完整 regression 通過。

## Pending Decisions

- GAP-07-B 之 Contract specification exact model 與 lifecycle validation。

## Confirmed V1 Decision

- `LogicalAccount != BrokerAccount`。
- 一個實體 BrokerAccount 可對應多個 LogicalAccount / CapitalBucket。
- V1 capital source：manual。
- Cross-strategy capital borrowing：default OFF；未來僅可由人工明確開啟。

## Next Queue

1. GAP-07-B — Canonical Contract Specification。
2. GAP-BROKER-001 — explicit OrderIntent / PositionEffect。
3. Broker Account / Position Sync。
4. GAP-08 — Trading State Persistence & Recovery。
5. GAP-09 — Incremental Feature / Market State Engine。

## Estimated Progress

- Overall V1：40–50%。
- GAP-07-A0：COMPLETE。
- GAP-07-A：implemented / review pending。
