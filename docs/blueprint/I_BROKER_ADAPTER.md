# I — Broker Adapter

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

隔離 broker-specific API / SDK / native model，將 canonical trading/account contracts 映射到第一個 broker Sinopac Shioaji。

Broker Adapter 不是 canonical business owner。

First broker：

    SINOPAC / Shioaji

Current implementation 主要位於：

- `backtest/shioaji_broker.py`
- `backtest/shioaji_mapping.py`
- `backtest/shioaji_fill.py`
- `backtest/shioaji_contracts.py`

Target ownership：

    adapters/sinopac/

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| I100 | Broker Capability | broker-supported features / verified limitations |
| I200 | Instrument / Contract Mapping | canonical ↔ Shioaji native contract |
| I300 | Order Mapping | OrderIntent / PositionEffect → native FuturesOrder |
| I400 | Status / Fill Mapping | native Trade / Deal → canonical events |
| I500 | Account Mapping | native account → BrokerAccount |
| I600 | Position Mapping | native futures position → BrokerPositionSnapshot |
| I700 | Connection / Session Lifecycle | API login/session/reconnect boundary |
| I800 | Broker Error Model | native error → explicit adapter error |
| I900 | Production Verification | fake / paper / connectivity evidence matrix |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| I110 | Broker Identity | adapter 使用 stable broker identifier `SINOPAC` | DESIGN_FROZEN | 2 | I01,I04 |
| I120 | Broker Capability Contract | adapter 宣告可支援 account/order/position/status semantics | ACCEPTED | 4 | I06 |
| I130 | Capability Verification Matrix | 每個 capability 有 source + fake/paper/live verification state | ACCEPTED | 4 | I06 |
| I140 | Unsupported Capability Failure | 未驗證/不支援功能 explicit reject，不 fallback 猜測 | ACCEPTED | 4 | I06 |
| I210 | BrokerInstrumentReference Consumption | adapter 只消費 broker-neutral mapping reference | ACCEPTED | 4 | I01,I04 |
| I220 | Futures Contract Native Lookup | broker_contract_code → native Shioaji futures contract | ACCEPTED | 3 | I01 |
| I230 | Canonical Product / Contract Separation | canonical symbol/code 不等同 Shioaji native code | ACCEPTED | 3 | I01,I04 |
| I240 | Native Contract Containment | native contract object 不離開 adapter boundary | ACCEPTED | 4 | I01 |
| I310 | Direction → Native Action | LONG/SHORT execution direction → Buy/Sell mapping | ACCEPTED | 3 | I02 |
| I320 | OrderType → Native PriceType | MARKET/LIMIT/STOP → supported native type | ACCEPTED | 3 | I02 |
| I330 | Native Order Duration / Qualifier | supported native ROD/other qualifier semantics 明確 | IMPLEMENTED | 2 | I02 |
| I340 | PositionEffect → New/Cover | OPEN/CLOSE/REDUCE → explicit native FuturesOCType | ACCEPTED | 5 | I02 |
| I350 | Remove Order-ID Prefix Inference | 禁止從 ENTRY-/EXIT- 推定 New/Cover | ACCEPTED | 5 | I02 |
| I360 | Native Order Construction | canonical order + effect → native FuturesOrder | ACCEPTED | 4 | I02 |
| I410 | Native Order Status Mapping | Shioaji status → canonical OrderStatus | ACCEPTED | 4 | I02,I03 |
| I420 | Native Deal → Fill | deal price / quantity / timestamp → Fill | ACCEPTED | 4 | I03 |
| I430 | Multi-Deal Conversion | one native trade 多 deals → canonical fills | ACCEPTED | 3 | I03 |
| I440 | Deal Dedup Identity | native deal seq 防止重複 delivery | ACCEPTED | 4 | I03 |
| I450 | Partial Fill Synchronization | PartFilled / deals 與 internal order 狀態同步 | ACCEPTED | 4 | I03 |
| I460 | Cancel / Reject Status Mapping | broker terminal state 明確轉換 | ACCEPTED | 3 | I02,I03 |
| I510 | Broker Account Identity Mapping | native account → broker + stable account_ref | ACCEPTED | 4 | I05 |
| I520 | Account Type Normalization | native account type → broker-neutral display/type metadata | ACCEPTED | 3 | I05 |
| I530 | Native / PII Filtering | username/person_id/secret/native SDK object 不進 core | ACCEPTED | 5 | I05 |
| I540 | Account Provider Adapter Seam | read-only account observation mapping seam | DESIGN_FROZEN | 3 | I05 |
| I610 | Futures Position Mapping | native FuturePosition → BrokerPositionSnapshot | ACCEPTED | 5 | I05 |
| I620 | Position Direction Mapping | native Buy → LONG、Sell → SHORT | ACCEPTED | 4 | I05 |
| I630 | Position Quantity / Average Price Mapping | quantity / price → canonical quantity / Decimal average_price | ACCEPTED | 4 | I05 |
| I640 | Position Contract Reverse Resolution | broker contract code → exact canonical listed contract | ACCEPTED | 5 | I04,I05 |
| I650 | Observation-Time Injection | caller 提供 observed_at / as_of_date，不 hidden now | ACCEPTED | 4 | I05 |
| I660 | Unknown Position Mapping Failure | unknown direction/code/ambiguous mapping explicit error | DESIGN_FROZEN | 5 | I05 |
| I710 | API Session Boundary | Shioaji API instance / session adapter-owned | IMPLEMENTED | 3 | I02 |
| I720 | Authentication Boundary | credentials/secrets 不進 canonical model / log | DESIGNED | 5 | I06 |
| I730 | Reconnect / Session Recovery | disconnect/reconnect lifecycle explicit | NOT_DESIGNED | 5 | I06 |
| I740 | Account Selection Boundary | physical broker account 必須 explicit 選擇，不 silent default in live | DESIGNED | 5 | I05,I06 |
| I810 | Mapping Error Translation | native mapping error → adapter/domain explicit error | IMPLEMENTED | 3 | I01-I04 |
| I820 | Network / Broker Error Classification | timeout / reject / disconnected / invalid request 分類 | NOT_DESIGNED | 4 | I06 |
| I830 | Ambiguous Broker Semantics Hard Block | 官方來源無法確認時 HARD_BLOCK | DESIGN_FROZEN | 5 | I06 |
| I910 | Deterministic Fake Tests | no login/network/credentials 的 adapter unit tests | ACCEPTED | 3 | I01-I04 |
| I920 | Broker Paper Verification | broker paper environment semantics verification | NOT_DESIGNED | 4 | I06 |
| I930 | Production Connectivity Verification | production connectivity only after live safety authorization | NOT_DESIGNED | 5 | I06 |
| I940 | Capability Evidence Record | source / version / tested mode / date / result 可追蹤 | ACCEPTED | 4 | I06 |

---

## Post-Runtime Broker Recovery Decision Checkpoint

ADR-002 R-04A-E define the current broker-adapter recovery safety contract。

Required adapter direction：

- provide account-scoped authoritative broker execution discovery without relying on pre-restart native Trade memory。
- exact native account filtering is mandatory。
- authoritative refresh precedes restart discovery evaluation。
- health diagnostics do not substitute for refresh。
- broker_client_order_ref requires a verified native round-trip carrier；Shioaji custom_field is candidate only。
- exact attribute/time heuristic matching is forbidden。
- adapter preserves native broker/deal/event evidence required for canonicalization and audit。
- health interpretation uses event_type + reason + required scope。
- NoBaseline is informational by itself。
- NotSubscribed requires continuity remediation rather than automatic current-state failure。
- SequenceGap may be current-state re-anchored while preserving historical degradation。
- persistent PendingReport / UntrackableEventId / ProjectionFailed prevent the affected readiness guarantees according to R-04D。
- deal-before-order-report is supported。
- exact restart-stable Fill identity must be capability-verified。
- callback-only event identity may be provenance but cannot be the sole restart Fill identity。
- PendingSubmit is a broker non-terminal observation and does not automatically mean canonical SUBMITTED。
- PreSubmitted / Inactive / relevant Failed mapping remains verification-gated。
- quantity modification recovery remains default-deny until broker quantity semantics are explicitly verified/frozen。

Production default-deny remains in force for unverified broker correlation/recovery capabilities。

This checkpoint does not promote existing I lifecycle values and does not authorize live connectivity。

## CURRENT / TARGET / MIGRATION

CURRENT：

- existing Shioaji adapter 位於 `backtest/shioaji_*`。
- submit / status / cancel 已存在。
- deal → Fill、multi-fill、dedup、partial fill 已存在。
- BrokerInstrumentReference native lookup 已有 foundation。
- GAP-ACCOUNT-001 已完成 account / position canonical mapping foundation；GAP-BROKER-002 capability matrix foundation 已接受；real network provider 與 broker paper verification 仍待後續。
- `ShioajiBroker.submit_order()` 已要求 explicit OrderIntent；New/Cover 由 PositionEffect 決定，不再依賴 order_id prefix。

TARGET：

- Shioaji native implementation 位於 `adapters/sinopac/`。
- core 只看 broker-neutral contracts。
- account / position read capability 與 order execution capability interface-segregated。
- capability matrix 可明確知道 supported / verified / unsafe。

MIGRATION：

- GAP-ACCOUNT-001 只新增 account/position mapping seam，不搬 existing order execution。
- GAP-BROKER-001 已將 New/Cover inference 替換為 explicit PositionEffect mapping。
- GAP-BROKER-002 已建立 broker-neutral capability/evidence contract 與 Sinopac documentation-only matrix。
- full adapter relocation 是後續 bounded migration，不與 current GAP 混做。

---

## GAP-ACCOUNT-001 Frozen Scope

本 Blueprint 與 ACTIVE provisional mapping 對齊：

    I510 Broker Account Identity Mapping
    I520 Account Type Normalization
    I530 Native / PII Filtering
    I610 Futures Position Mapping
    I620 Position Direction Mapping
    I630 Position Quantity / Average Price Mapping
    I640 Position Contract Reverse Resolution
    I650 Observation-Time Injection

不得在此 GAP 自動實作：

    I340 PositionEffect → New/Cover
    I350 Remove Order-ID Prefix Inference
    I700+ live connection lifecycle
    I900 production verification

---

## Connections

| From | To | Contract |
|---|---|---|
| D600 | I200 | BrokerInstrumentReference |
| H200/H100 | I300 | OrderIntent / PositionEffect / Order |
| I300 | Shioaji | native FuturesOrder / contract |
| Shioaji | I400 | native trade / status / deals |
| I400 | H300/H400 | OrderStatus / Fill / future OrderEvent |
| Shioaji account | I500 | BrokerAccount |
| Shioaji position | I600 | BrokerPositionSnapshot |
| I500/I600 | J200/J400 | broker actual account/position observation |

---

## Authority

- Canonical instrument / contract identity：D Domain。
- OrderIntent / PositionEffect / Order / Fill：H Domain。
- BrokerAccount / AccountPosition / BrokerPositionSnapshot：J Domain。
- Shioaji native contract / account / trade / deal / position object：I Domain adapter-only。
- BrokerInstrumentReference：D Domain canonical broker-neutral mapping reference。
- broker API response 不得直接成為 core canonical authority。
- adapter 不得 silent overwrite expected account state。

---
## External Sources

- SRC-SINOPAC-LOGIN-001。
- SRC-SINOPAC-CONTRACT-001。
- SRC-SINOPAC-FUT-ORDER-001。
- SRC-SINOPAC-POSITION-001。
- SRC-SINOPAC-SIMULATION-001。
- SRC-SINOPAC-ORDER-STATUS-001。
- SRC-SINOPAC-ORDER-EVENT-001。
- SRC-SINOPAC-RELEASE-001。
- SRC-PYDANTIC-001。
- SRC-ADR-001。

Broker API source change risk：HIGH。

任何 broker semantics implementation 前應依 Work Package 規則確認 Last Verified / Revalidation Required。

---

## Key Invariants

- native `sj.*` object adapter-only。
- broker account secrets / username / person_id 不進 core。
- broker code 不等於 canonical identity。
- ambiguous contract mapping 不猜測。
- account/position query 不擴充 execution Broker ABC。
- account/position foundation 是 read-only。
- corrective order 必須等 GAP-BROKER-001 explicit PositionEffect。
- Order ID prefix 不得長期作 New/Cover business truth。

---

## Current GAP Mapping

- I510-I660 → GAP-ACCOUNT-001。
- I340-I350 → GAP-BROKER-001。
- I120-I140 / I940 → GAP-BROKER-002 ACCEPTED。
- I720 / I730 / I740 / I820 / I920 / I930 → later broker/live phases。
- full physical relocation → GAP-ARCH-001 bounded migration。

---

## GAP-BROKER-001 Sinopac Mapping Freeze

Status：

DESIGN_FROZEN。

Official source：

    SRC-SINOPAC-FUT-ORDER-001

Last verified：

    2026-09-25

### Explicit Mapping Matrix

| Position Direction | PositionEffect | Shioaji Action | FuturesOCType |
|---|---|---|---|
| LONG | OPEN | Buy | New |
| SHORT | OPEN | Sell | New |
| LONG | REDUCE | Sell | Cover |
| SHORT | REDUCE | Buy | Cover |
| LONG | CLOSE | Sell | Cover |
| SHORT | CLOSE | Buy | Cover |

Rules：

- OPEN 只映射 explicit New semantics。
- REDUCE / CLOSE 只映射 explicit Cover semantics。
- 本 GAP 不使用 FuturesOCType.Auto。
- 本 GAP 不使用 FuturesOCType.DayTrade。
- DayTrade semantics 未在本 Work Package 定義，不得猜測。
- native action 必須由 PositionDirection + PositionEffect 共同決定。
- native octype 必須由 PositionEffect 決定。

### Mapping API

to_shioaji_order 不再接受 caller 任意傳入 native octype 作為 business truth。

Target conceptual seam：

    to_shioaji_order(
        order,
        intent
    )

Mapper 必須：

- validate order / intent consistency。
- derive native Action。
- derive native FuturesOCType。
- preserve existing price type / order type / quantity mapping。

### Prefix Removal

禁止：

    order_id.startswith("ENTRY-")

或任何其他 ID naming convention 決定：

- New。
- Cover。
- Buy。
- Sell。

ENTRY / EXIT prefix 可以暫時保留作 legacy identifier formatting。

但不得再具有 broker execution semantics。

### Failure Semantics

以下必須 explicit error：

- missing intent。
- unknown PositionEffect。
- unsupported PositionDirection。
- order / intent quantity mismatch。
- order / intent direction mismatch。
- direct opposite-side reversal request。

不得 fallback：

- Auto。
- order ID inference。
- silent New。
- silent Cover。

## GAP-BROKER-002 Architect Design Freeze

Status：

DESIGN_FROZEN。

Runtime scope：

    I120
    I130
    I140
    I940

Canonical ownership：

    adapters/capabilities.py

Sinopac concrete matrix：

    adapters/sinopac/capabilities.py

This Work Package does not relocate existing backtest/shioaji_* execution code。

### Public Capability IDs

BrokerCapability exact V1 values：

    ACCOUNT_QUERY
    POSITION_QUERY
    ORDER_PLACE
    ORDER_UPDATE
    ORDER_CANCEL
    ORDER_STATUS
    TRADE_LIST
    ORDER_DEAL_EVENT

### Support State

BrokerCapabilitySupport exact values：

    SUPPORTED
    UNSUPPORTED
    UNKNOWN

### Verification Mode

BrokerVerificationMode exact values：

    DOCUMENTATION
    FAKE
    SIMULATION
    PRODUCTION

Modes are independent evidence labels, not an implied hierarchy。

DOCUMENTATION does not imply SIMULATION。

SIMULATION does not imply PRODUCTION。

### BrokerCapabilityEvidence

Immutable fields：

    capability: BrokerCapability
    support: BrokerCapabilitySupport
    source_ids: tuple[str, ...]
    verification_modes: tuple[BrokerVerificationMode, ...]
    sdk_version: str | None
    verified_on: date
    note: str | None = None

Rules：

- frozen / extra forbid。
- source_ids trim + nonblank + no duplicates。
- verification_modes no duplicates and deterministic canonical ordering。
- sdk_version if supplied trim + nonblank。
- note if supplied trim + nonblank。
- SUPPORTED / UNSUPPORTED require at least one source_id。
- UNKNOWN may have no source, but must not claim verification_modes。
- no hidden now()；verified_on is explicit evidence date。

### BrokerCapabilityMatrix

Immutable fields：

    broker: str
    entries: tuple[BrokerCapabilityEvidence, ...]

Rules：

- broker trim + uppercase + nonblank。
- one entry per BrokerCapability。
- duplicate capability explicit validation error。
- deterministic entry ordering by BrokerCapability enum order。
- matrix is evidence, not execution authority。

### Explicit Failure Contract

BrokerCapabilityUnavailableError：

    RuntimeError

Public pure functions：

    get_broker_capability(
        matrix,
        capability
    ) -> BrokerCapabilityEvidence | None

    require_broker_capability(
        matrix,
        capability,
        *,
        required_mode: BrokerVerificationMode | None = None
    ) -> BrokerCapabilityEvidence

require rules：

- missing capability -> explicit error。
- UNSUPPORTED -> explicit error。
- UNKNOWN -> explicit error。
- requested verification mode absent -> explicit error。
- no fallback / no assumption from another mode。

### SINOPAC_CAPABILITY_MATRIX

Broker：

    SINOPAC

Initial evidence baseline：

    sdk_version = 1.7.6
    verified_on = 2026-09-25

Initial records may claim：

    support = SUPPORTED
    verification_modes = (DOCUMENTATION,)

for capabilities directly supported by reviewed official documentation。

Initial matrix MUST NOT claim：

    SIMULATION
    PRODUCTION

unless an actual explicit verification run is recorded separately。

### Source Mapping

ACCOUNT_QUERY：

    SRC-SINOPAC-LOGIN-001

POSITION_QUERY：

    SRC-SINOPAC-POSITION-001

ORDER_PLACE / ORDER_UPDATE / ORDER_CANCEL：

    SRC-SINOPAC-FUT-ORDER-001

ORDER_STATUS / TRADE_LIST：

    SRC-SINOPAC-ORDER-STATUS-001

ORDER_DEAL_EVENT：

    SRC-SINOPAC-ORDER-EVENT-001
    SRC-SINOPAC-RELEASE-001

Simulation documentation context：

    SRC-SINOPAC-SIMULATION-001

### Explicitly Deferred

Not implemented by GAP-BROKER-002：

- I720 Authentication Boundary runtime。
- I730 Reconnect / Session Recovery。
- I740 live account-selection enforcement。
- I820 network/broker error classification。
- I920 actual broker simulation/paper verification run。
- I930 production connectivity verification。
- CA / credential handling。
- production login。
- real broker network calls。
- live-money authorization。
- adapter physical relocation。

I830 existing ambiguous-semantics HARD_BLOCK invariant remains unchanged。

### Runtime Safety

- capability evidence never authorizes LIVE by itself。
- DOCUMENTATION evidence never upgrades to SIMULATION / PRODUCTION automatically。
- missing / unknown / insufficiently verified capability fails explicitly。
- default broker account behavior must not be adopted as canonical live account selection。
- no credentials / secrets / person_id in capability evidence。

### Source Review

Last verified：

    2026-09-25

Current reviewed Shioaji release：

    1.7.6

Change risk：

    HIGH

Revalidation required before future simulation/production evidence update：

    YES

---

## Domain Acceptance

- I01～I06 全部有 leaf mapping。
- existing implementation 與 target adapter ownership 都清楚。
- GAP-ACCOUNT-001 IDs 與 ACTIVE 完全一致。
- current unsafe New/Cover inference 有明確 future replacement。
- official source requirements 已掛接。
