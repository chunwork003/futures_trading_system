# O — React Workspace

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

提供 V1 投資平台的主要 Web Workspace，涵蓋 research、backtest、strategy、account、orders、risk/live、review/audit 與 system status。

React：

只呼叫 ASP.NET Core Application API / realtime endpoint。

禁止：

- direct PostgreSQL。
- direct Python core。
- direct Shioaji。
- embedded secrets。

Target ownership：

    apps/web/

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| O100 | App Shell | navigation / layout / session / global state |
| O200 | Research Workspace | dataset / research jobs / results |
| O300 | Backtest Workspace | backtest config / run / metrics / comparison |
| O400 | Strategy Workspace | strategy / parameter / version configuration |
| O500 | Account Workspace | logical/broker account / expected/actual |
| O600 | Orders / Positions | order/fill/position operational view |
| O700 | Risk / Live Control | risk/readiness/authorization/safety action UI |
| O800 | Review / Audit | provenance / reconciliation / audit review |
| O900 | System Status | service/broker/db/realtime health |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| O110 | React Application Shell | shared workspace root / routing / layout | DESIGNED | 3 | O01 |
| O120 | Navigation Model | research/trading/account/risk/review/status navigation | DESIGNED | 2 | O01 |
| O130 | Frontend Toolchain Pin Gate | scaffold 前由 human pin React/build tool/TypeScript versions | DESIGNED | 3 | O01 |
| O140 | API Client Boundary | all HTTP calls through typed client/service layer | DESIGNED | 3 | O01 |
| O150 | Realtime Client Boundary | SignalR/realtime subscription isolated from components | DESIGNED | 3 | O01 |
| O160 | Global Error / Loading State | consistent async operation state | DESIGNED | 2 | O01 |
| O170 | Authenticated Session UI | session expiration / unauthorized state explicit | DESIGNED | 3 | O01 |
| O210 | Research Job Submission | create research/backtest-related operation | DESIGNED | 3 | O02 |
| O220 | Research Operation Status | queued/running/succeeded/failed/cancelled view | DESIGNED | 3 | O02 |
| O230 | Dataset / Scope Selection | select available data/instrument/timeframe without editing raw storage | DESIGNED | 3 | O02 |
| O240 | Research Result View | metrics/table/chart projection | DESIGNED | 3 | O02 |
| O310 | Backtest Configuration | strategy/data/cost/risk parameters | DESIGNED | 3 | O02 |
| O320 | Backtest Run Control | submit/cancel/inspect run | DESIGNED | 3 | O02 |
| O330 | Performance Dashboard | return/PF/expectancy/DD/trade stats | DESIGNED | 3 | O02 |
| O340 | Trade / Equity Inspection | trades/equity/drawdown inspection | DESIGNED | 3 | O02 |
| O350 | Comparison Workspace | baseline/parameter/OOS/Monte Carlo comparison | DESIGNED | 4 | O02 |
| O410 | Strategy Definition View | strategy identity/version description | DESIGNED | 3 | O03 |
| O420 | Strategy Instance Configuration | instrument/timeframe/config scope | DESIGNED | 4 | O03 |
| O430 | Config Version View | current/pending/history/version | DESIGNED | 3 | O03 |
| O440 | Safe Config Change UX | active/pending position 時顯示 safe-boundary semantics | DESIGNED | 4 | O03 |
| O510 | Logical Account View | internal capital allocation | DESIGNED | 3 | O04 |
| O520 | Broker Account View | physical broker reference，禁止顯示 secret | DESIGNED | 4 | O04 |
| O530 | Expected Position View | AccountPosition clearly labeled expected | DESIGNED | 4 | O04 |
| O540 | Broker Actual Position View | BrokerPositionSnapshot clearly labeled actual | DESIGNED | 4 | O04 |
| O550 | Expected / Actual Comparison UX | mismatch 不以顏色/文字造成 authority混淆 | DESIGNED | 4 | O04 |
| O610 | Order List / Detail | order lifecycle / intent / status | DESIGNED | 3 | O04 |
| O620 | Fill List / Detail | actual executions / price / quantity | DESIGNED | 3 | O04 |
| O630 | Position View | target / expected / actual 分層顯示 | DESIGNED | 4 | O04 |
| O640 | Order Timeline | OrderIntent → OrderEvent → Fill trace | DESIGNED | 4 | O04,O05 |
| O710 | Risk State View | limits / utilization / RiskDecision | DESIGNED | 4 | O04 |
| O720 | Reconciliation Readiness View | MATCH/mismatch/startup readiness | DESIGNED | 4 | O04,O05 |
| O730 | Trading Mode View | BACKTEST/SIMULATED/BROKER_PAPER/LIVE_CONFIRM/LIVE_AUTO | DESIGNED | 4 | O04 |
| O740 | Authorization Scope View | account/symbol/time/limit scope visible before live action | DESIGNED | 5 | O04 |
| O750 | High-Risk Confirmation UX | force-flat/live action requires explicit confirmation workflow | DESIGNED | 5 | O04 |
| O760 | Kill Switch Control UX | clearly distinct from force-flat | DESIGNED | 5 | O04 |
| O770 | Live Default-Deny UX | unauthorized controls disabled/blocked，server remains final authority | DESIGN_FROZEN | 5 | O04 |
| O810 | Reconciliation Case Review | mismatch evidence / policy / resolution history | DESIGNED | 4 | O05 |
| O820 | Decision / Risk Provenance View | Signal→Decision→Risk→Order→Fill trace | DESIGNED | 4 | O05 |
| O830 | Manual Override Audit View | actor/reason/time/result | DESIGNED | 4 | O05 |
| O840 | Configuration Audit View | config/version/approval history | DESIGNED | 3 | O05 |
| O850 | Search / Filter / Correlation | correlation/order/account/strategy IDs 可追查 | DESIGNED | 3 | O05 |
| O910 | Service Health View | Python/Application/DB health | DESIGNED | 3 | O05 |
| O920 | Broker Connectivity View | connectivity != live authorization | DESIGNED | 4 | O05 |
| O930 | Realtime Connection State | connected/reconnecting/disconnected visible | DESIGNED | 3 | O05 |
| O940 | Runtime Readiness View | READY/DEGRADED/HALTED/REVIEW state | DESIGNED | 4 | O05 |
| O950 | Operational Incident Surface | latest critical failure / safety halt context | DESIGNED | 4 | O05 |

---

## CURRENT / TARGET / MIGRATION

CURRENT：

- React workspace 尚未建立。

TARGET：

- single primary investment workspace。
- research 與 operational trading 共用 shell，但權限/authority清楚。
- realtime 提升可見性，不取代 authoritative query/state。

MIGRATION：

- N Application API 穩定後才 scaffold O。
- scaffold 前 pin React / TypeScript / build tooling。
- 不從 Python/private model 自動生成 UI authority。

---

## Connections

| From | To | Contract |
|---|---|---|
| O | N600 | HTTPS API |
| N700 | O | realtime projection / notification |
| O200-O400 | N/M/F/E | research/strategy workflow through Application |
| O500-O800 | N/J/K/L | account/audit/live workflow through Application |

---

## Authority

- React state：view/session state only。
- operational truth：K/Python domains via Application API。
- authorization：server-side N/L authority。
- realtime event：notification/projection，不是 SOR。
- UI disabled state 不等於 security enforcement。

---

## Key Invariants

- React 不 direct DB。
- React 不 direct Shioaji。
- React 不保存 broker secrets。
- React 不 direct Python trading core。
- server remains final authorization authority。
- expected / actual / target position 必須視覺與文字分離。
- kill switch 不得和 force-flat UX 混為同一動作。
- broker connectivity 不代表 live authorization。

---

## Sources

- SRC-REACT-LEARN-001。
- SRC-REACT-REF-001。
- SRC-ASPNET-SIGNALR-001。
- SRC-ARCH-001。

---

## Domain Acceptance

- O01～O05 全部有 leaf mapping。
- App Shell / Research / Strategy / Account / Live / Audit / Status 責任完整。
- UI 不成為 security/state authority。
- frontend toolchain 有 explicit human pin gate。
