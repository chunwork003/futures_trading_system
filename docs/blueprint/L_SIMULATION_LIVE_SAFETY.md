# L — Simulation / Live Safety

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

提供 realistic fault simulation、trading mode contract、LIVE authorization、runtime guards、manual safety control、kill switch 與 production verification。

LIVE_AUTO：

    NOT AUTHORIZED

直到所有 production gates 完成。

SimulationBroker 與 PaperBroker 必須分離。

Target ownership：

    simulation/
    trading/runtime safety boundary

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| L100 | Trading Modes | BACKTEST / SIMULATED / BROKER_PAPER / LIVE_CONFIRM / LIVE_AUTO |
| L200 | SimulationBroker | realistic broker simulation boundary |
| L300 | Latency / Fill Faults | latency / partial fill / delayed event |
| L400 | Reject / Cancel / Disconnect Faults | negative broker/runtime scenarios |
| L500 | Runtime Guards | stale / reconciliation / account / risk guards |
| L600 | LIVE Authorization | explicit time/account/symbol/risk authorization |
| L700 | Manual Safety Control | override / suspension / force-flat |
| L800 | Kill Switch | block unsafe new execution / emergency control |
| L900 | Production Verification | simulation / broker-paper / production evidence |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| L110 | TradingMode Contract | explicit runtime execution mode | IMPLEMENTED | 3 | L02 |
| L120 | BACKTEST Mode | historical deterministic replay only | ACCEPTED | 2 | L02 |
| L130 | SIMULATED Mode | live-like runtime against SimulationBroker | DESIGNED | 3 | L02 |
| L140 | BROKER_PAPER Mode | real broker paper environment boundary | DESIGNED | 4 | L02 |
| L150 | LIVE_CONFIRM Mode | real broker execution requires explicit human approval workflow | DESIGNED | 5 | L02,L03 |
| L160 | LIVE_AUTO Mode | automated real-money execution behind full safety authorization | DESIGN_FROZEN | 5 | L02,L03 |
| L170 | Market / Execution Environment Separation | live market data 不等同 live-money execution authorization | DESIGN_FROZEN | 5 | L02,L03 |
| L210 | SimulationBroker Contract | broker port implementation with controllable realistic behavior | NOT_DESIGNED | 5 | L01 |
| L220 | Deterministic Simulation Seed / Scenario | same scenario/seed 可重現 | NOT_DESIGNED | 3 | L01 |
| L230 | Simulation Clock | controllable event timing / latency clock | NOT_DESIGNED | 4 | L01 |
| L240 | Scenario Configuration | faults / latency / fill rules explicit config | NOT_DESIGNED | 4 | L01 |
| L310 | Submission Latency | configurable broker submit delay | NOT_DESIGNED | 3 | L01 |
| L320 | Fill Latency | configurable execution delay | NOT_DESIGNED | 3 | L01 |
| L330 | Partial Fill Fault | deterministic partial fills | NOT_DESIGNED | 4 | L01 |
| L340 | Delayed Status Fault | fill/status arrival sequencing scenarios | NOT_DESIGNED | 4 | L01 |
| L350 | Stale Status Fault | broker status temporarily stale | NOT_DESIGNED | 4 | L01 |
| L410 | Order Rejection Fault | deterministic broker reject scenario | NOT_DESIGNED | 3 | L01 |
| L420 | Cancel Failure / Race | cancel 與 fills/status race scenario | NOT_DESIGNED | 4 | L01 |
| L430 | Broker Disconnect Fault | connectivity interruption | NOT_DESIGNED | 4 | L01 |
| L440 | Reconnect / Recovery Scenario | disconnect 後重新同步/reconcile | NOT_DESIGNED | 5 | L01,L05 |
| L450 | Duplicate / Delayed Event Scenario | idempotency / ordering verification | NOT_DESIGNED | 4 | L01 |
| L510 | Reconciliation Health Guard | unresolved mismatch 阻止 unsafe execution | NOT_DESIGNED | 5 | L05 |
| L520 | Stale Market Data Guard | market observation 超時時停止 risk-increasing action | NOT_DESIGNED | 5 | L05 |
| L530 | Stale Broker State Guard | account/order/position state 過舊時阻止 unsafe action | NOT_DESIGNED | 5 | L05 |
| L540 | Risk Health Guard | rejected/invalid risk state 不得送 broker | NOT_DESIGNED | 5 | L05 |
| L550 | Persistence / Recovery Health Guard | operational state 未成功 recover 不得 READY | NOT_DESIGNED | 5 | L05 |
| L560 | Trading Session Guard | session / contract / expiry invalid 時拒絕 execution | NOT_DESIGNED | 5 | L05 |
| L570 | Account Scope Guard | execution account 必須在 authorized scope | NOT_DESIGNED | 5 | L05 |
| L610 | LIVE Authorization Record | explicit authorization object / lifecycle | NOT_DESIGNED | 5 | L03,L06 |
| L620 | Authorization Time Window | LIVE authority 有 start/end / expiry | NOT_DESIGNED | 5 | L03 |
| L630 | Broker Account Scope | 只允許指定 BrokerAccount | NOT_DESIGNED | 5 | L03 |
| L640 | Instrument / Symbol Scope | 只允許指定 instruments/contracts | NOT_DESIGNED | 5 | L03 |
| L650 | Position / Exposure Limit | authorization 層 position/exposure hard limit | NOT_DESIGNED | 5 | L03 |
| L660 | Loss Limit | daily/session/account loss threshold | NOT_DESIGNED | 5 | L03 |
| L670 | Authorization Suspension / Revocation | authority 可立即 suspend/revoke | NOT_DESIGNED | 5 | L03,L06 |
| L680 | Default-Deny LIVE_AUTO | 沒有有效 authorization 就禁止 LIVE_AUTO | DESIGN_FROZEN | 5 | L03 |
| L710 | Manual Override Record | manual intervention 必須有 actor/reason/time/audit | NOT_DESIGNED | 5 | L04,L06 |
| L720 | Manual Trading Suspension | operator 可停止新的 risk-increasing action | NOT_DESIGNED | 5 | L04 |
| L730 | Explicit Force-Flat Workflow | 明確授權下產生 closing intent/effect | NOT_DESIGNED | 5 | L04 |
| L740 | Force-Flat Safety Preconditions | account identity/reconciliation/execution capability 必須可確認 | NOT_DESIGNED | 5 | L04 |
| L750 | Manual Override Persistence | override / action / result 進 K Domain audit | NOT_DESIGNED | 4 | L04,L06 |
| L810 | Kill Switch State | emergency execution-disabled state | NOT_DESIGNED | 5 | L04 |
| L820 | Block New Risk-Increasing Orders | kill switch 開啟後禁止新/add exposure | NOT_DESIGNED | 5 | L04 |
| L830 | Existing Order Handling Policy | open orders cancel/retain policy 必須 explicit | NOT_DESIGNED | 5 | L04 |
| L840 | Kill Switch != Force-Flat | kill switch 本身不隱含自動 liquidation | DESIGN_FROZEN | 5 | L04 |
| L850 | Kill Switch Audit | trigger/source/reason/result durable audit | NOT_DESIGNED | 4 | L04,L06 |
| L910 | Simulation Verification Matrix | safety requirements 在 deterministic simulation 驗證 | NOT_DESIGNED | 4 | L07 |
| L920 | Broker Paper Verification Matrix | Shioaji paper behavior 驗證 | NOT_DESIGNED | 4 | L07 |
| L930 | Production Connectivity Verification | limited connectivity verification，不代表 trading authorization | NOT_DESIGNED | 5 | L07 |
| L940 | Recovery Drill | crash/restart/reconcile drill | NOT_DESIGNED | 5 | L07 |
| L950 | Disconnect Drill | broker disconnect/reconnect drill | NOT_DESIGNED | 5 | L07 |
| L960 | Reconciliation Mismatch Drill | intentional mismatch → HALT / review verification | NOT_DESIGNED | 5 | L07 |
| L970 | Backup / Restore Drill | K persistence restore + reconciliation readiness | NOT_DESIGNED | 5 | L07 |
| L980 | Production Authorization Review | all evidence complete 才能考慮 LIVE_AUTO authorization | NOT_DESIGNED | 5 | L07 |

---

## Trading Mode Boundary

    BACKTEST
        historical clock
        no broker network

    SIMULATED
        live-like orchestration
        SimulationBroker
        no real-money broker execution

    BROKER_PAPER
        broker paper environment
        no production real-money authority

    LIVE_CONFIRM
        production broker
        explicit human confirmation workflow

    LIVE_AUTO
        production broker
        automated execution
        default disabled
        all authorization/safety gates required

---

## Kill Switch Semantics

Kill switch：

- 禁止新的 risk-increasing execution。
- 可觸發明確 cancel policy。
- 必須 audit。

Kill switch 不自動等同：

    force-flat

Force-flat：

- 是獨立 explicit recovery/safety workflow。
- 需要 H200 OrderIntent / PositionEffect。
- 需要已知 BrokerAccount / AccountPosition。
- 需要 broker capability verification。
- 需要 authorization/audit。

---

## LIVE_AUTO Minimum Dependencies

至少：

- GAP-ACCOUNT-001。
- GAP-BROKER-001。
- GAP-RECON-001。
- GAP-08。
- GAP-PERSIST-001 material provenance。
- GAP-07-TIME-001。
- GAP-07-SESSION-EXPIRY。
- GAP-BROKER-002 critical capability verification。
- GAP-SIM-001 critical scenarios。
- LIVE authorization / guards / overrides / kill switch。

---

## Connections

| From | To | Contract |
|---|---|---|
| C/D | L500 | session/contract/time validity |
| G900 | L500/L600 | RiskDecision / exposure limits |
| H/I | L200-L400 | broker port / adapter behavior simulation reference |
| J600/J700 | L500 | reconciliation / readiness health |
| K700 | L500 | recovery health |
| L600/L700/L800 | N application | future auth/workflow/orchestration |
| L audit events | K600/K800 | durable audit / provenance |

---

## Authority

- SimulationBroker：simulation behavior authority only。
- PaperBroker：simple deterministic paper baseline，不是 realistic simulator。
- Authorization：permission to enter specific live mode/scope。
- Reconciliation：J authority。
- Execution：H authority。
- Broker capability：I authority。
- Audit persistence：K authority。

---

## Secrets / Security Boundary

- secrets 不進 domain/account/order model。
- secrets 不進 logs / Blueprint / fixtures。
- authentication / authorization application workflow 主要由 N Domain 實作。
- L Domain 定義 trading safety requirement，不自行成為 credential store。

---

## Key Invariants

- live market data 不代表 LIVE_AUTO authorization。
- BROKER_PAPER 不代表 production verification。
- LIVE_AUTO default disabled。
- unresolved reconciliation mismatch 阻止 unsafe live execution。
- stale market/broker state 阻止 risk-increasing action。
- kill switch 不等於 automatic force-flat。
- force-flat 是 explicit PositionEffect-based workflow。
- manual override 必須 authenticated/authorized/audited。
- simulation verification 不等於 production authorization。

---

## Sources

- SRC-SINOPAC-LOGIN-001。
- SRC-SINOPAC-FUT-ORDER-001。
- SRC-SINOPAC-POSITION-001。
- SRC-TAIFEX-CALENDAR-001。
- SRC-ADR-001。
- SRC-ARCH-001。

Production implementation 時若涉及 authentication/security framework，必須先在 SOURCE_REGISTRY 新增對應 pinned official source。

---

## Current GAP Mapping

- L210-L450 → GAP-SIM-001。
- L610-L980 → GAP-LIVE-001 / production readiness。
- L510-L570 依賴 GAP-ACCOUNT-001 / GAP-RECON-001 / GAP-08。
- broker verification → GAP-BROKER-002。

---

## Domain Acceptance

- L01～L07 全部有 leaf mapping。
- PaperBroker / SimulationBroker 清楚分離。
- market environment / execution environment 清楚分離。
- authorization / guards / manual override / kill switch 各自責任清楚。
- LIVE_AUTO 有 explicit default-deny gate。
