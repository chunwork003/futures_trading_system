# M — Python Service Boundary

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

將 Python Quant / Research / Trading Core 透過 stable versioned REST/JSON contract 提供給 ASP.NET Core Application。

V1 default transport：

    REST / JSON

禁止 ASP.NET Core import/embed Python domain objects。

Domain model 不等於 wire DTO。

Target ownership：

    service/

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| M100 | Service Host | Python service process / lifecycle / framework boundary |
| M200 | Wire DTO Contracts | domain ↔ API DTO mapping |
| M300 | Versioning / Error Contract | API version / errors / compatibility |
| M400 | Research / Backtest API | research execution / results |
| M500 | Trading API | strategy/decision/execution operational use cases |
| M600 | Account / Risk API | account/reconciliation/risk operational views/actions |
| M700 | Job / Operation Model | long-running operation lifecycle |
| M800 | Health / Observability API | readiness / health / correlation |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| M110 | Python Service Process Boundary | Python runtime 以獨立 service 對 Application 提供能力 | DESIGNED | 4 | M01 |
| M120 | REST / JSON Transport | V1 synchronous request/response default transport | DESIGN_FROZEN | 3 | M01 |
| M130 | Service Framework Selection Gate | implementation framework 必須由 human design freeze / version pin，不由 Codex自行選擇 | DESIGNED | 3 | M01 |
| M140 | Service Startup / Shutdown | deterministic startup / graceful shutdown / dependency readiness | DESIGNED | 4 | M01 |
| M150 | No Embedded Python in ASP.NET | Application 不 import/embed Python runtime/domain object | DESIGN_FROZEN | 5 | M01 |
| M210 | DTO Boundary | public wire DTO 與 domain model 分離 | DESIGN_FROZEN | 5 | M02 |
| M220 | Stable Identity Fields | DTO 使用 stable IDs，不以 display text 作 identity | DESIGN_FROZEN | 4 | M02 |
| M230 | Version Field | externally meaningful payload 帶 contract/schema version | DESIGNED | 3 | M02 |
| M240 | Timestamp Contract | operational DTO timestamp 必須 timezone-aware / ISO-compatible | DESIGN_FROZEN | 4 | M02 |
| M250 | Decimal Serialization Contract | operational price/money/margin 不以 binary-float semantics 當 wire truth | DESIGNED | 4 | M02 |
| M260 | Expected / Actual Distinction | AccountPosition / BrokerPositionSnapshot wire contract 不混淆 | DESIGN_FROZEN | 5 | M02,M04 |
| M270 | Correlation / Causation | operational DTO 可攜 correlation_id / causation_id | DESIGN_FROZEN | 4 | M02 |
| M310 | API Version Namespace | breaking contract change 需 explicit version strategy | DESIGNED | 4 | M01,M02 |
| M320 | Backward Compatibility Policy | versioned client/server rollout 不 silent break | DESIGNED | 4 | M01,M02 |
| M330 | Error Envelope | machine-readable code / message / details / correlation | DESIGNED | 4 | M02 |
| M340 | Validation Error Contract | invalid input 與 business rejection 分離 | DESIGNED | 3 | M02 |
| M350 | Domain Error Mapping | domain/reconciliation/risk errors 映射 stable API error | DESIGNED | 4 | M02,M04 |
| M360 | No Internal Trace Leakage | production response 不洩漏 secret/internal stack/native broker object | DESIGN_FROZEN | 4 | M02 |
| M410 | Research Request API | research/backtest request contract | DESIGNED | 3 | M03 |
| M420 | Backtest Run API | submit/run bounded backtest job | DESIGNED | 4 | M03 |
| M430 | Backtest Result API | structured metrics/trades/report result | DESIGNED | 3 | M03 |
| M440 | Optimization API | future optimization request/result boundary | DESIGNED | 4 | M03 |
| M450 | OOS / WFO / Monte Carlo API | research validation workflows | DESIGNED | 4 | M03 |
| M510 | Strategy Runtime API | strategy definition/instance operational access | DESIGNED | 4 | M04 |
| M520 | Decision API Boundary | expose target/decision evidence without leaking private classes | DESIGNED | 4 | M04 |
| M530 | Execution Command Boundary | authorized application use case → canonical trading command | DESIGNED | 5 | M04 |
| M540 | Trading Mode Boundary | mode changes / requests retain L Domain safety semantics | DESIGNED | 5 | M04 |
| M610 | Broker Account Query API | read canonical BrokerAccount through application boundary | DESIGNED | 4 | M04 |
| M620 | Account Position API | expected AccountPosition views | DESIGNED | 4 | M04 |
| M630 | Broker Position API | actual BrokerPositionSnapshot views | DESIGNED | 4 | M04 |
| M640 | Reconciliation API | result/case/readiness access | DESIGNED | 5 | M04 |
| M650 | Risk API | RiskDecision / risk state / constraints | DESIGNED | 4 | M04 |
| M660 | Safety Command Boundary | force-flat / override / live control requires N/L authorization workflow | DESIGN_FROZEN | 5 | M04 |
| M710 | Operation ID | long-running research/task 有 stable operation identity | DESIGNED | 3 | M03 |
| M720 | Operation Status | QUEUED / RUNNING / SUCCEEDED / FAILED / CANCELLED style lifecycle | DESIGNED | 3 | M03 |
| M730 | Result Reference | large result 透過 result reference/resource，不要求單一巨大 response | DESIGNED | 3 | M03 |
| M740 | Cancellation Semantics | long-running job cancellation explicit | DESIGNED | 3 | M03 |
| M810 | Liveness Endpoint | process alive，不能等同 operational READY | DESIGNED | 2 | M01 |
| M820 | Readiness Endpoint | required dependencies/core state ready 才回 READY | DESIGNED | 4 | M01,M04 |
| M830 | Dependency Health | DB/broker/core dependency health 可觀測但不洩漏 secrets | DESIGNED | 4 | M01 |
| M840 | Request Correlation Logging | request / domain / downstream correlation | DESIGNED | 3 | M01,M02 |
| M850 | Metrics / Structured Logging Boundary | service operational signals 可由 N/system status 消費 | DESIGNED | 3 | M01 |

---

## CURRENT / TARGET / MIGRATION

CURRENT：

- Python research/trading runtime 已存在。
- 尚無正式 Python service host。
- 尚無 wire DTO contract。

TARGET：

- Python core 保持主要 quant/trading ownership。
- ASP.NET Core 透過 versioned REST/JSON 呼叫。
- public DTO 與 Python domain model 明確分離。

MIGRATION：

- M9 開始前 human 必須先 pin Python service framework/version。
- service framework 不得反向污染 domain model。
- 不把 backtest/private class 直接 JSON serialize 當 public API。

---

## Connections

| From | To | Contract |
|---|---|---|
| F | M400 | research/backtest use cases |
| G/H/J/L | M500/M600 | trading/account/risk/safety use cases |
| K | M400/M600 | persistent operational/research result access through ports |
| M | N | versioned REST/JSON DTO |

---

## Authority

- Python domain/trading models：Python core authority。
- wire DTO：M Domain API contract。
- Application workflow/authentication：N Domain。
- React view state：O Domain。
- DTO 不得成為 domain canonical model。

---

## Key Invariants

- Domain model != wire DTO。
- ASP.NET Core 不 import/embed Python domain object。
- V1 default REST/JSON。
- gRPC 只有 profiling 證明需要才評估。
- V1 不導入 Kafka/RabbitMQ。
- API command 不得繞過 L Domain safety gate。
- broker native object 不得出現在 wire DTO。

---

## Sources

- SRC-ARCH-001。
- SRC-BLUEPRINT-001。

Python service framework 尚未 pin；M9 implementation 前必須新增官方 framework source。

---

## Domain Acceptance

- M01～M04 全部有 leaf mapping。
- domain / DTO / application responsibilities 分離。
- service framework selection 被列為 explicit human gate。
- long-running research 不強迫使用同步巨大 request。
