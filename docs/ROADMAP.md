# V1 Roadmap

## Status

AUTHORITATIVE MILESTONE ROADMAP

詳細 capability：

`V1_CAPABILITY_MAP.md`

Technical issues：

`GAP_REGISTER.md`

Current execution queue：

`CURRENT_WORK.md`

Engineering decomposition：

`V1_SYSTEM_BLUEPRINT.md`

Blueprint：

不是額外產品 milestone。

它是 M0～M12 的跨 milestone engineering decomposition / traceability layer。

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

CLOSED

Accepted runtime commit：

`50813b679f818f3837a9f50fdcda9921495ab507`

Completed：

- BrokerAccount。
- canonical internal AccountPosition foundation。
- BrokerPositionSnapshot。
- separate account / position read ports。
- exact broker contract reverse resolution。
- Sinopac pure account / position mapping。
- pure mismatch comparison。

Verification：

- targeted 50 passed。
- compatibility 48 passed。
- full regression 776 passed。

Safety：

無 corrective broker order。

---

# M5 — Explicit Execution Semantics + Reconciliation

Status：

COMPLETED / ACCEPTED

GAP-BROKER-001：

CLOSED / ACCEPTED。

GAP-RECON-001：

CLOSED / ACCEPTED。

Architecture / Design Freeze：

J610-J780 COMPLETED。

Runtime slice 001A：

COMPLETED / ACCEPTED。

Runtime commit：

`d7dbd884f09e72d7737726409e11e0679206ed8d`

Runtime slice 001B：

COMPLETED / ACCEPTED。

Runtime commit：

`4049f982474454556baf8734a5729ecbedc7a438`

Safety preserved：

- no silent repair。
- no automatic corrective execution。
- no persistence implementation inside reconciliation。

Next ordered mainline：

GAP-BROKER-002 CLOSED / ACCEPTED。

Accepted runtime commit：`7d7fdabcb99da59d3d23ccec62b11c6572ceea82`。

---


# M6 — Persistence / Recovery / Provenance

Status：IN_PROGRESS / GAP-08EFGHI_READY_FOR_EXECUTION

Accepted：

- GAP-08ABCD Persistence Foundation + Event Ledger。

Current：

GAP-08EFGHI Operational Persistence + Recovery。

Merged scope：EF + required OMS + GHI + necessary StrategyInstance/Account dependencies。

Design Freeze：COMPLETED。

Runtime Gate：HOLD_FOR_ARCHITECTURE_FREEZE_COMMIT。

Runtime：NOT_YET_AUTHORIZED。

K520：DEFERRED_TO_GAP_09。

Projected lifecycle after full acceptance：約 53.57%。

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

Lifecycle-weighted V1 completion：

47.92%。

Architecture Design Coverage：87.60%。
Design Freeze Coverage：60.88%。
Runtime Implementation：43.19%。
Unit Verification：39.96%。
Integration Verification：39.87%。
Accepted Capability：39.87%。

Capability status：

COMPLETE 12 / PARTIAL 51 / NOT_STARTED 29。

Operational readiness：NOT_READY。
Production Live readiness：BLOCKED。
LIVE_AUTO：NOT_AUTHORIZED。

Current mainline：

GAP-08EFGHI READY_FOR_EXECUTION / HOLD_FOR_ARCHITECTURE_FREEZE_COMMIT。

Progress source：

`docs/blueprint/METRICS.md` + 603 engineering-leaf lifecycle baseline。
