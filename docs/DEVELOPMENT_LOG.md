# Development Log

## MASTER SCOPE OVERVIEW

### Major Features

- Historical data pipeline、Trading Calendar、Parquet / DuckDB research layer。
- Backtest core、execution lifecycle、portfolio accounting、risk、position sizing。
- Paper trading、Shioaji adapter foundation、multi-strategy decision、strategy attribution、target account position。

### Minor Features

- Parameter optimization / sensitivity / stability。
- OOS、walk-forward、Monte Carlo、performance 與 trade analysis。

### Deferred Features

- News Intelligence、Local LLM、mature ML pipeline、GIS / Property、Mobile、production server、Full Drawing Engine。

### Milestone and Progress

- Current milestone：M0 — Governance / Architecture Consolidation。
- Completed：GAP-03 Execution Lifecycle、G-5 Multi-Strategy Decision Architecture、GAP-06 Position Sizing / Capital Allocation。
- Pending：M0-B、GAP-07、broker sync/reconciliation、persistence/recovery、incremental state。
- Overall V1：40–50%。以 Work Package weight 與 acceptance criteria 評估；不可使用 LOC 或 file count。
- M0-A remaining：< 1 engineering hour（等待 review / commit authorization）。
- V1 provisional remaining：45–75 engineering hours。
- 此為 dynamic estimate，不是 deadline；每個 checkpoint / milestone 後重新估算。發現 architecture blocker 或新增 scope 時可上調；已有功能比預期成熟時可下調。

## Chronological Log

### 2026-09-24 19:41 +08:00

- Milestone：M0-A — Project Governance Scaffold。
- Overall progress：40–50%。
- Major completed count：3（GAP-03、G-5、GAP-06）。
- Minor completed count：以既有 research / analysis 能力計，未在本次重新估算。
- Added scope：治理入口、現況、工作佇列、GAP register、AI handoff、development log、repository-local temporary convention。
- Completed：建立 M0-A governance scaffold；未修改 runtime behavior。
- In progress：人工 / architect review。
- Blocked：無；pytest TEMP permission 另列 GAP-ENV-001。
- Pending review：M0-B architecture boundary、canonical models、LogicalAccount boundary。
- Estimated remaining hours：M0-A < 1 engineering hour；V1 provisional 45–75 engineering hours（dynamic estimate，非 deadline）。
- Next：M0-B，然後 GAP-07。

新增事件必須插在此 chronological log 的最上方，並維持相同欄位；每筆必須包含 Estimated remaining hours。此估計每個 checkpoint / milestone 後重新評估，architecture blocker 或新增 scope 可上調，既有功能成熟度較高時可下調。
