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

Status：IN_PROGRESS / ARCHITECTURE_ACCEPTANCE_HOLD / CORRECTION_FREEZE_REQUIRED

Accepted：

- GAP-08ABCD Persistence Foundation + Event Ledger。

GAP-08EFGHI：

- runtime candidate implemented。
- runtime commit：`6b62239bca1d11543944f9f078e577e16010bcbf`。
- verification：934 passed / 4 skipped / 1 warning。
- architecture acceptance：HOLD。
- original 35 leaves / weight 151：NOT ACCEPTED。

Post-runtime architecture decisions：

- R-01 DECIDED。
- R-02 DECIDED。
- R-03A-D DECIDED。
- R-03 overall DECIDED。
- R-04A-H DECIDED。
- R-04 overall DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

Expanded R-03/R-04 correction scope is not yet lifecycle-weighted。

Linked dependencies：R-12 / R-13 / R-14 / K520。

Broker capability gates remain implementation/production authorization requirements。

Runtime Gate：HOLD_FOR_BOUNDED_CORRECTION_FREEZE。

Runtime Authorization：NOT_AUTHORIZED_FOR_FURTHER_EXECUTION。

Next：map/freeze/reweight bounded correction Work Package before implementation。

Official lifecycle remains 47.92% architecture-freeze baseline until correction/acceptance rebase。


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

GAP-08EFGHI READY_FOR_EXECUTION / RELEASED_ARCHITECTURE_FREEZE。

Progress source：

`docs/blueprint/METRICS.md` + 603 engineering-leaf lifecycle baseline。

## Recovery Architecture Checkpoint 5A

Closed through this checkpoint：R-01、R-02、R-03、R-04、R-05。

R-01/R-02/R-04 include architecture amendments discovered by closed-loop consistency audit。

R-05 ExecutionStateLoader contract is DECIDED but runtime conformance remains unimplemented/unverified。

Immediate next：R-06 + R-07 Recovery Boundary Cluster。

Runtime correction remains gated behind later：

decision completion → correction scope freeze → reweight → explicit runtime authorization。

Runtime Gate：NOT_AUTHORIZED。

## Recovery Architecture Checkpoint 5B

Closed through this checkpoint：R-01 through R-07。

Checkpoint 5B closes：

- R-06 Multi-strategy recovery boundary。
- R-07 ReconciliationCase BrokerAccount isolation/query boundary。

Immediate next architecture work：R-08 + R-09 identity/config authority cluster。

R-10 formal closure and R-11 clock authority follow after R-08/R-09。

Correction runtime remains gated behind completion of remaining architecture decisions、correction scope freeze/reweight and explicit runtime authorization。

Runtime Gate：NOT_AUTHORIZED。

## Recovery Architecture Checkpoint 5C

Closed through this checkpoint：R-01 through R-09。

Checkpoint 5C closes R-08 / R-09 identity/config/lifecycle authority。

Immediate next：R-10 formal closure，then R-11 clock authority。

Runtime correction remains gated behind remaining decision closure、boundary classification、correction-scope freeze/reweight and explicit authorization。

Runtime Gate：NOT_AUTHORIZED。

## Recovery Architecture Checkpoint 5D

Closed through this checkpoint：R-01 through R-11。

Checkpoint 5D closes R-10 initialization provenance and R-11 operational clock/timestamp authority。

Immediate next：R-12 ReconciliationRun audit contract。

Then：R-13 / R-14 boundary classification、K520 defer confirmation、broker capability classification、correction-scope freeze/reweight、explicit runtime authorization。

Runtime Gate：NOT_AUTHORIZED。

## Recovery Architecture Checkpoint 5E

Closed/classified recovery decision sequence now covers R-01 through R-14。

Checkpoint 5E closes：
- R-12 ReconciliationRun audit contract。
- R-13 operator authorization boundary classification。
- R-14 market-data completeness boundary classification。

Architecture closure does not imply runtime conformance or runtime authorization。

Runtime candidate remains `6b62239bca1d11543944f9f078e577e16010bcbf` and remains NOT ACCEPTED。

Next phase is classification/freeze preparation，not architecture free exploration：

1. K520 defer confirmation。
2. Broker capability gate classification。
3. Complete correction-scope map。
4. Reweight expanded Work Package。
5. Explicit bounded runtime authorization decision。

Runtime Gate：NOT_AUTHORIZED。
