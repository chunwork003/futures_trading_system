# V1 Roadmap

## Status

AUTHORITATIVE MILESTONE ROADMAP

詳細 capability：

`V1_CAPABILITY_MAP.md`

Technical issues：

`GAP_REGISTER.md`

Current execution queue：

`CURRENT_WORK.md`

---

# M0 — Governance / Architecture

Status：

CLOSED

Completed：

- governance。
- authoritative docs。
- ADR-001。
- Work Package quality gate。
- issue classification。

---

# M1 — Historical Data / Research Foundation

Status：

MOSTLY COMPLETE

Completed foundation：

- ingestion。
- validation。
- cleaning。
- aggregation。
- Parquet。
- DuckDB。
- trading calendar。
- features。
- strategy。
- backtest。
- analysis。
- optimization。
- OOS。
- WFO。
- Monte Carlo。

Remaining：

- local data governance。
- continuous roll completeness。
- final Return/Sharpe validation。

---

# M2 — Trading Core Foundation

Status：

MOSTLY COMPLETE

Completed：

- execution lifecycle。
- partial fills。
- LONG/SHORT。
- paper trading。
- multi-strategy decision。
- target position。
- global risk。
- position sizing。
- capital management。
- Shioaji adapter foundation。

---

# M3 — Canonical Futures Specification

ID：

GAP-07

Status：

CLOSED

Completed：

- InstrumentSpec。
- ContractSpec。
- TradingSessionRef。
- MarginSchedule。
- specification resolution。
- BrokerInstrumentReference。
- actual multiplier consumer。
- actual margin consumer。

---

# M4 — Broker Account / Position Sync Foundation

Status：

READY_FOR_EXECUTION

Main scope：

- BrokerAccount。
- BrokerPositionSnapshot。
- internal AccountPosition boundary。
- account/position read port。
- Shioaji fake mapping tests。
- pure expected/actual mismatch detection。

Safety：

此階段只允許 read-only sync foundation。

不得 automatic corrective broker order。

---

# M5 — Explicit Execution Semantics + Reconciliation

Status：

PENDING

GAP-BROKER-001：

- OrderIntent。
- PositionEffect。
- OPEN/CLOSE/REDUCE semantics。
- 移除 ID prefix 推定 New/Cover。

Reconciliation：

- ReconciliationResult。
- mismatch policies。
- startup readiness。
- strict/manual handling。

GAP-BROKER-002：

- broker capability matrix。
- verified semantics。
- mapping persistence follow-up。

---

# M6 — Persistence / Recovery / Provenance

Status：

PENDING

GAP-08：

- PostgreSQL operational SOR。
- Order persistence。
- Fill persistence。
- OrderEvent persistence。
- Position/account snapshots。
- strategy state。
- event history。
- idempotency。
- restart recovery。
- broker reconciliation after restart。

GAP-PERSIST-001：

- DecisionContext。
- RiskDecision。
- correlation/causation。
- audit trace。

---

# M7 — Incremental Feature / Market State

ID：

GAP-09

Status：

PENDING

- incremental feature state。
- paper/live market state。
- no full-history recalculation per bar。
- deterministic reconstruction。

---

# M8 — Simulation / Live Safety

Status：

PENDING

- SimulationBroker。
- latency。
- partial fill。
- rejection。
- disconnect。
- stale state。
- execution modes。
- authorization。
- runtime risk。
- manual override。
- force-flat。
- kill switch。
- verification matrix。

---

# M9 — Python Service Boundary

Status：

PENDING

- versioned REST/JSON。
- wire DTO。
- research/backtest API。
- account/trading API。
- stable IDs。
- versioned payloads。

---

# M10 — ASP.NET Core Application

Status：

PENDING

- Api。
- Application。
- Contracts。
- Infrastructure。
- Realtime。
- authentication。
- authorization。
- workflows。
- approval gates。
- configuration。

---

# M11 — React Workspace

Status：

PENDING

- shell。
- research/backtest。
- strategy/configuration。
- account/orders/positions。
- risk/live control。
- review/audit。
- system status。

---

# M12 — Full V1 Integration / Readiness

Status：

PENDING

Required：

- end-to-end workflow。
- restart recovery drill。
- broker disconnect drill。
- reconciliation mismatch drill。
- backup/restore drill。
- security review。
- operational observability。
- simulation verification。
- Shioaji connectivity verification。
- complete full regression。

LIVE_AUTO real money：

仍需獨立 production authorization。

---

# Current Progress

Provisional weighted V1 completion：

45–52%。

Center：

約 49%。

下一次正式 re-estimate：

M4 Broker Account / Position Sync + Reconciliation foundation 完成後。
