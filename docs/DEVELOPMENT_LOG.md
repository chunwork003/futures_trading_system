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

- Current milestone：GAP-07 — Contract / Futures Specification。
- Completed：GAP-03 Execution Lifecycle、G-5 Multi-Strategy Decision Architecture、GAP-06 Position Sizing / Capital Allocation、M0-B、GAP-07-A0、GAP-07-A、GAP-07-B、GAP-07-C、GAP-07-D、GAP-07-E、GAP-07-F。
- Pending：GAP-07-E2 review、GAP-07-E3 margin consumer wiring、broker execution migration、sync/reconciliation、persistence/recovery、incremental state。
- Overall V1：40–50%。以 Work Package weight 與 acceptance criteria 評估；不可使用 LOC 或 file count。
- GAP-07-E2 remaining：< 1 engineering hour（等待 review / commit authorization）。
- V1 provisional remaining：45–75 engineering hours。
- 此為 dynamic estimate，不是 deadline；每個 checkpoint / milestone 後重新估算。發現 architecture blocker 或新增 scope 時可上調；已有功能比預期成熟時可下調。

## Chronological Log

### 2026-09-24 21:41 +08:00

- Milestone：GAP-07-E2 — Actual Backtest / Risk Consumer Integration。
- Overall progress：40–50%（provisional；本 slice 不重新估算整體百分比）。
- Major completed count：3（GAP-03、G-5、GAP-06）。
- Minor completed count：GAP-07-F complete；GAP-07-E2 implemented / review pending。
- Added scope：GAP-07-E3 — deterministic margin actual consumer wiring。
- Completed：optional canonical engine factory、single run-time multiplier config、legacy/default source traceability、Portfolio real calculation proof；targeted 4 passed、related existing 41 passed、full regression 737 passed。
- In progress：architect review 與 commit authorization。
- Blocked：無。
- Pending review：GAP-07-E2 implementation；margin consumer wiring 留待 GAP-07-E3，避免 hidden current date 與 risk config scope expansion。
- Estimated remaining hours：V1 provisional 45–75 engineering hours；GAP-07-E3 pre-check 後重新估算。
- Next：GAP-07-E3 approved Work Package。

### 2026-09-24 21:31 +08:00

- Milestone：GAP-07-F — BrokerInstrumentReference / Broker Mapping Contract。
- Overall progress：40–50%（provisional；本 slice 不重新估算整體百分比）。
- Major completed count：3（GAP-03、G-5、GAP-06）。
- Minor completed count：GAP-07-E complete；GAP-07-F implemented / review pending。
- Added scope：無；GAP-BROKER-002 更新為 mapping contract complete、capability matrix / persistence pending。
- Completed：broker-neutral mapping reference、inclusive effective-date resolution、exact listed mapping、missing/ambiguity errors、SINOPAC native lookup seam；domain targeted 19 passed、Shioaji targeted 5 passed、full regression 733 passed。
- In progress：architect review 與 commit authorization。
- Blocked：無。
- Pending review：GAP-07-F implementation；legacy `Order.contract` lookup 留待 GAP-BROKER-001/execution migration。
- Estimated remaining hours：V1 provisional 45–75 engineering hours；broker execution migration pre-check 後重新估算。
- Next：GAP-BROKER-001 approved Work Package。

### 2026-09-24 21:22 +08:00

- Milestone：GAP-07-E — Backtest / Risk Compatibility Resolution。
- Overall progress：40–50%（provisional；本 slice 不重新估算整體百分比）。
- Major completed count：3（GAP-03、G-5、GAP-06）。
- Minor completed count：GAP-07-D complete；GAP-07-E implemented / review pending。
- Added scope：無；GAP-07-MARGIN-001 更新為 runtime domain 與 compatibility path complete，database/live pending。
- Completed：explicit override / canonical resolution precedence、來源追蹤、明確缺值錯誤、explicit no-margin mode；targeted new tests 11 passed、相關既有 tests 67 passed、full regression 712 passed。
- In progress：architect review 與 commit authorization。
- Blocked：無。
- Pending review：GAP-07-E implementation；legacy `BacktestConfig.multiplier=200` 保留 compatibility，但不是 canonical truth。
- Estimated remaining hours：V1 provisional 45–75 engineering hours；GAP-07 後續 slices 完成後重新估算。
- Next：GAP-07 後續 approved slice。

### 2026-09-24 21:08 +08:00

- Milestone：GAP-07-D — Canonical Margin Schedule and Effective-Date Resolver。
- Overall progress：40–50%（provisional；本 slice 不重新估算整體百分比）。
- Major completed count：3（GAP-03、G-5、GAP-06）。
- Minor completed count：GAP-07-C complete；GAP-07-D implemented / review pending。
- Added scope：GAP-07-MARGIN-001 具體化為 runtime domain complete、database/live pending。
- Completed：Decimal margin reference、effective-date lookup、contract precedence、instrument fallback、duplicate detection；targeted 31 passed；full regression 701 passed。
- In progress：architect review 與 commit authorization。
- Blocked：無。
- Pending review：GAP-07-D implementation；DuckDB schema refinement 與 broker actual margin snapshot 留待 approved slice。
- Estimated remaining hours：V1 provisional 45–75 engineering hours；GAP-07 後續 slices 完成後重新估算。
- Next：GAP-07-E — Backtest / Risk compatibility adapter。

### 2026-09-24 20:59 +08:00

- Milestone：GAP-07-C — Canonical Trading Session Reference。
- Overall progress：40–50%（provisional；本 slice 不重新估算整體百分比）。
- Major completed count：3（GAP-03、G-5、GAP-06）。
- Minor completed count：GAP-07-B complete；GAP-07-C implemented / review pending。
- Added scope：GAP-07-TIME-001、GAP-07-SESSION-001、GAP-07-SESSION-EXPIRY。
- Completed：domain-owned `TradingSessionRef`、IANA timezone validation、canonical `[open, close)` boundary；targeted 15 passed；full regression 670 passed。
- In progress：architect review 與 commit authorization。
- Blocked：無。
- Pending review：GAP-07-C implementation；timezone migration、session rule duplication 與 expiry-day consolidation 留待已登錄 GAP。
- Estimated remaining hours：V1 provisional 45–75 engineering hours；GAP-07 後續 slices 完成後重新估算。
- Next：GAP-07-D — Margin Schedule。

### 2026-09-24 20:41 +08:00

- Milestone：GAP-07-B — Canonical Contract Specification。
- Overall progress：40–50%（provisional；本 slice 不重新估算整體百分比）。
- Major completed count：3（GAP-03、G-5、GAP-06）。
- Minor completed count：GAP-07-A complete；GAP-07-B implemented / review pending。
- Added scope：無；依 approved Work Package 實作 canonical `ContractSpec`。
- Completed：monthly/quarterly/weekly/other listed series、weekly without contract month、lifecycle validation、legacy conversion；targeted 28 passed；full regression 660 passed。
- In progress：architect review 與 commit authorization。
- Blocked：無。
- Pending review：GAP-07-B implementation；下一 slice Trading Session / Calendar reference exact model。
- Estimated remaining hours：V1 provisional 45–75 engineering hours；GAP-07 後續 slices 完成後重新估算。
- Next：GAP-07-C — Trading Session / Calendar Reference。

### 2026-09-24 20:26 +08:00

- Milestone：GAP-07-A — Canonical Instrument Specification。
- Overall progress：40–50%（provisional；本 slice 不重新估算整體百分比）。
- Major completed count：3（GAP-03、G-5、GAP-06）。
- Minor completed count：GAP-07-A0 complete；GAP-07-A implemented / review pending。
- Added scope：無；依 approved Work Package 實作 canonical `InstrumentSpec`。
- Completed：canonical symbol 固定為 TX / MTX / TMF；alias namespace 與 canonical identity 分離；targeted 17 passed；full regression 628 passed。
- In progress：architect review 與 commit authorization。
- Blocked：無。
- Pending review：GAP-07-A implementation；下一 slice Contract Specification exact model。
- Estimated remaining hours：V1 provisional 45–75 engineering hours；GAP-07 後續 slices 完成後重新估算。
- Next：GAP-07-B — Canonical Contract Specification。

### 2026-09-24 20:00 +08:00

- Milestone：M0-B — Architecture Boundary ADR final corrections。
- Overall progress：40–50%（provisional）。
- Major completed count：3（GAP-03、G-5、GAP-06）。
- Minor completed count：以既有 research / analysis 能力計，未在本次重新估算。
- Added scope：ADR-001 architecture ownership、dependency direction、migration strategy 已 ACCEPTED。
- Completed：architecture boundary accepted；無 runtime change，無 test change。
- In progress：final documentation / commit pending。
- Blocked：無。
- Pending review：GAP-07 Contract / Futures Specification exact model。
- Estimated remaining hours：V1 provisional 45–75 engineering hours；GAP-07 pre-check 完成後重新估算。
- Next：GAP-07 Contract / Futures Specification Pre-check。

### 2026-09-24 19:59 +08:00

- Milestone：M0-B — Architecture Boundary ADR。
- Overall progress：40–50%。
- Major completed count：3（GAP-03、G-5、GAP-06）。
- Minor completed count：以既有 research / analysis 能力計，未在本次重新估算。
- Added scope：ADR-001 提出 canonical ownership、adapter dependency direction、compatibility strategy 與 migration gates。
- Completed：完成 read/analyze/design；未修改 runtime behavior。
- In progress：architect review ADR-001。
- Blocked：無；broker semantics、reconciliation 與 persistence 仍為後續 feature GAP。
- Pending review：canonical `trading/` 最小首次範圍、Python/C# REST V1 default、migration sequence。
- Estimated remaining hours：M0-B review < 2 engineering hours；V1 provisional 45–75 engineering hours（dynamic estimate，非 deadline）。
- Next：GAP-07 pre-check，僅於 ADR review 後開始。

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
