# N — ASP.NET Core Application

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

提供 application use cases、workflow、authentication、authorization、approval、configuration、Python service orchestration、operational API 與 realtime。

Target logical projects：

    InvestmentPlatform.Api
    InvestmentPlatform.Application
    InvestmentPlatform.Contracts
    InvestmentPlatform.Infrastructure
    InvestmentPlatform.Realtime

ASP.NET Core 不直接碰 Shioaji SDK。

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| N100 | Solution Structure | .NET solution / project dependency |
| N200 | Application Use Cases | workflow / orchestration |
| N300 | Authentication | user/operator identity |
| N400 | Authorization / Approval | policy / live approval / command permission |
| N500 | Python / Broker Orchestration | service client / operational coordination |
| N600 | Operational HTTP API | React-facing BFF/API |
| N700 | Realtime | SignalR projections / notifications |
| N800 | Configuration / Secrets | versioned config workflow / secret provider boundary |
| N900 | Administration / Observability | health / audit / operational status |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| N110 | Solution / Project Layout | Api/Application/Contracts/Infrastructure/Realtime 分離 | DESIGNED | 4 | N01 |
| N120 | .NET Version Pin Gate | scaffold 前由 human pin supported .NET / ASP.NET Core major | DESIGNED | 3 | N01 |
| N130 | Project Dependency Direction | Application 不依賴 Infrastructure implementation | DESIGNED | 4 | N01 |
| N140 | Composition Root | dependency injection / configuration assembly only at host boundary | DESIGNED | 3 | N01 |
| N210 | Application Use Case Contract | UI/API 不直接 orchestration Python/domain primitives | DESIGNED | 4 | N02 |
| N220 | Research Workflow | submit/status/result research job orchestration | DESIGNED | 3 | N02 |
| N230 | Trading Workflow | trading command lifecycle orchestration | DESIGNED | 5 | N02,N05 |
| N240 | Account / Reconciliation Workflow | account sync / case review / readiness orchestration | DESIGNED | 5 | N02,N05 |
| N250 | Manual Intervention Workflow | override / force-flat / suspension explicit workflow | DESIGNED | 5 | N02,N05 |
| N260 | Use Case Correlation | request → Python operation → persistence/audit correlation | DESIGNED | 4 | N02 |
| N310 | Authentication Boundary | operator identity must be authenticated for protected actions | DESIGNED | 5 | N03 |
| N320 | Authentication Scheme Selection Gate | identity mechanism human-selected / source-pinned before implementation | DESIGNED | 4 | N03 |
| N330 | Session / Token Handling | authentication lifecycle does not expose broker credentials | DESIGNED | 4 | N03 |
| N340 | Authentication Audit | security-relevant authentication event audit hook | DESIGNED | 3 | N03 |
| N410 | Policy-Based Authorization | action permission based on explicit policy/resource scope | DESIGNED | 5 | N03,N05 |
| N420 | Trading Mode Permission | LIVE_CONFIRM / LIVE_AUTO permission distinct from read-only access | DESIGNED | 5 | N03,N05 |
| N430 | Account / Instrument Scope Authorization | live permission scoped to account/instrument | DESIGNED | 5 | N03,N05 |
| N440 | Approval Gate | high-risk operation 可要求 explicit approval | DESIGNED | 5 | N02,N05 |
| N450 | Default-Deny High-Risk Commands | missing permission/approval → reject | DESIGN_FROZEN | 5 | N03,N05 |
| N460 | Authorization Audit | actor/policy/resource/result durable audit | DESIGNED | 4 | N03,N05 |
| N510 | Python Service Client | typed/version-aware REST client to M Domain | DESIGNED | 4 | N05 |
| N520 | No Direct Shioaji Dependency | ASP.NET 不 import/call Shioaji SDK | DESIGN_FROZEN | 5 | N05 |
| N530 | Broker Workflow Orchestration | application coordinates broker-related use case only through Python API | DESIGNED | 5 | N05 |
| N540 | Retry / Timeout Boundary | application retry must not duplicate economic trading command | DESIGNED | 5 | N05 |
| N550 | Idempotent Command Propagation | high-risk command carries idempotency/correlation identity | DESIGNED | 5 | N05 |
| N610 | React BFF / API | React only calls Application API | DESIGN_FROZEN | 4 | N04 |
| N620 | Request Validation | HTTP shape validation before application use case | DESIGNED | 3 | N04 |
| N630 | Application DTO Mapping | public API contract separate from Python DTO/internal entity | DESIGNED | 4 | N04 |
| N640 | Problem / Error Mapping | stable HTTP/application error contract | DESIGNED | 3 | N04 |
| N650 | Operational Query API | accounts/orders/positions/risk/system state projections | DESIGNED | 4 | N04 |
| N710 | SignalR Hub Boundary | realtime server→client update channel | DESIGNED | 4 | N04 |
| N720 | Account / Position Realtime | canonical projection updates | DESIGNED | 3 | N04 |
| N730 | Order / Fill Realtime | execution lifecycle updates | DESIGNED | 3 | N04 |
| N740 | Risk / Safety Realtime | risk / reconciliation / safety notification | DESIGNED | 4 | N04 |
| N750 | Realtime Not Authority | realtime message 是 projection/notification，不是 SOR | DESIGN_FROZEN | 4 | N04 |
| N810 | Versioned Application Configuration | config change 可追蹤 / validate / approve | DESIGNED | 4 | N05 |
| N820 | Strategy Config Workflow | strategy parameters 經 safe boundary 生效 | DESIGNED | 4 | N05 |
| N830 | Live Safety Config Workflow | limit / authorization config change 高風險審核 | DESIGNED | 5 | N05 |
| N840 | Secret Provider Boundary | broker/application secret 由 infrastructure secret provider 管理 | DESIGNED | 5 | N03,N05 |
| N850 | No Secret in DTO / Log / DB Domain Model | secrets 不得洩漏到一般 operational model | DESIGN_FROZEN | 5 | N03,N05 |
| N910 | Health Aggregation | Python/DB/realtime dependency health projection | DESIGNED | 3 | N04 |
| N920 | Operational Status | readiness / degraded / halted / maintenance status | DESIGNED | 4 | N04 |
| N930 | Audit Query Boundary | user/action/config/trading audit read API | DESIGNED | 4 | N04,N05 |
| N940 | Structured Logging / Correlation | cross-service request correlation | DESIGNED | 3 | N04 |

---

## CURRENT / TARGET / MIGRATION

CURRENT：

- ASP.NET Core solution 尚未建立。

TARGET：

- Application 是 user/workflow/security orchestration owner。
- Python 保持 quant/trading core owner。
- React 只呼叫 N Application API。

MIGRATION：

- M9 Python service contract 穩定後才 scaffold N。
- scaffold 前 pin .NET major / auth approach / source versions。
- 不先建立會與 Python canonical model重複的 C# domain hierarchy。

---

## Connections

| From | To | Contract |
|---|---|---|
| O | N600/N700 | HTTPS / realtime UI contract |
| N200/N500 | M | versioned REST/JSON |
| N800 | K/Application persistence | approved config / audit state |
| N300/N400 | L600/L700 | authentication / authorization / approval |
| N700 | O | SignalR projections |

---

## Authority

- authentication / authorization / workflow：N Domain。
- trading/risk/account business truth：Python G/H/J/L Domains。
- operational SOR：K/PostgreSQL。
- realtime payload：projection only。
- broker native SDK：I Domain，N 禁止直接依賴。

---

## Key Invariants

- ASP.NET Core 不直接碰 Shioaji SDK。
- ASP.NET Core 不 embed Python domain objects。
- React 不直接呼叫 Python service。
- authentication != authorization。
- high-risk command default deny。
- application retry 不得 duplicate economic order。
- realtime notification 不得成為 state authority。
- broker secrets 不進普通 DTO/log/domain model。

---

## Sources

- SRC-ASPNET-001。
- SRC-ASPNET-WEBAPI-001。
- SRC-ASPNET-SIGNALR-001。
- SRC-ASPNET-SECURITY-001。
- SRC-ASPNET-AUTHZ-001。
- SRC-POSTGRES-001。
- SRC-ARCH-001。

---

## Domain Acceptance

- N01～N05 全部有 leaf mapping。
- solution/application/contracts/infrastructure/realtime responsibility 清楚。
- authN / authZ / approval 分離。
- Python orchestration 不等於 direct broker integration。
- .NET/auth mechanism 在 runtime scaffold 前有 explicit human gate。

## Recovery Decision Checkpoint 5E — Production Authorization Ownership

N remains target application owner of production operator authentication、authorization、approval and high-risk command workflow。

R-13 does not require GAP-08 to scaffold or implement the full ASP.NET authorization subsystem。

The Python trading/recovery core must nevertheless enforce authorization-required semantics at its own authoritative protected-action boundary and default-deny when trusted production authority is unavailable。

Caller-supplied `actor`、`confirmed_by`、reason strings or booleans are not substitutes for N-governed production authorization evidence。

Future N authorization decisions must preserve exact protected resource/action scope and durable correlation without becoming broker-side idempotency authority。

Full security mechanics such as provider、MFA、RBAC/claims details、approval count and UI remain separately implementation-gated。
