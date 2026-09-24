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
| I120 | Broker Capability Contract | adapter 宣告可支援 account/order/position/status semantics | DESIGNED | 4 | I06 |
| I130 | Capability Verification Matrix | 每個 capability 有 source + fake/paper/live verification state | NOT_DESIGNED | 4 | I06 |
| I140 | Unsupported Capability Failure | 未驗證/不支援功能 explicit reject，不 fallback 猜測 | DESIGNED | 4 | I06 |
| I210 | BrokerInstrumentReference Consumption | adapter 只消費 broker-neutral mapping reference | ACCEPTED | 4 | I01,I04 |
| I220 | Futures Contract Native Lookup | broker_contract_code → native Shioaji futures contract | ACCEPTED | 3 | I01 |
| I230 | Canonical Product / Contract Separation | canonical symbol/code 不等同 Shioaji native code | ACCEPTED | 3 | I01,I04 |
| I240 | Native Contract Containment | native contract object 不離開 adapter boundary | ACCEPTED | 4 | I01 |
| I310 | Direction → Native Action | LONG/SHORT execution direction → Buy/Sell mapping | ACCEPTED | 3 | I02 |
| I320 | OrderType → Native PriceType | MARKET/LIMIT/STOP → supported native type | ACCEPTED | 3 | I02 |
| I330 | Native Order Duration / Qualifier | supported native ROD/other qualifier semantics 明確 | IMPLEMENTED | 2 | I02 |
| I340 | PositionEffect → New/Cover | OPEN/CLOSE/REDUCE → explicit native FuturesOCType | NOT_DESIGNED | 5 | I02 |
| I350 | Remove Order-ID Prefix Inference | 禁止從 ENTRY-/EXIT- 推定 New/Cover | NOT_DESIGNED | 5 | I02 |
| I360 | Native Order Construction | canonical order + effect → native FuturesOrder | ACCEPTED | 4 | I02 |
| I410 | Native Order Status Mapping | Shioaji status → canonical OrderStatus | ACCEPTED | 4 | I02,I03 |
| I420 | Native Deal → Fill | deal price / quantity / timestamp → Fill | ACCEPTED | 4 | I03 |
| I430 | Multi-Deal Conversion | one native trade 多 deals → canonical fills | ACCEPTED | 3 | I03 |
| I440 | Deal Dedup Identity | native deal seq 防止重複 delivery | ACCEPTED | 4 | I03 |
| I450 | Partial Fill Synchronization | PartFilled / deals 與 internal order 狀態同步 | ACCEPTED | 4 | I03 |
| I460 | Cancel / Reject Status Mapping | broker terminal state 明確轉換 | ACCEPTED | 3 | I02,I03 |
| I510 | Broker Account Identity Mapping | native account → broker + stable account_ref | DESIGN_FROZEN | 4 | I05 |
| I520 | Account Type Normalization | native account type → broker-neutral display/type metadata | DESIGN_FROZEN | 3 | I05 |
| I530 | Native / PII Filtering | username/person_id/secret/native SDK object 不進 core | DESIGN_FROZEN | 5 | I05 |
| I540 | Account Provider Adapter Seam | read-only account observation mapping seam | DESIGN_FROZEN | 3 | I05 |
| I610 | Futures Position Mapping | native FuturePosition → BrokerPositionSnapshot | DESIGN_FROZEN | 5 | I05 |
| I620 | Position Direction Mapping | native Buy → LONG、Sell → SHORT | DESIGN_FROZEN | 4 | I05 |
| I630 | Position Quantity / Average Price Mapping | quantity / price → canonical quantity / Decimal average_price | DESIGN_FROZEN | 4 | I05 |
| I640 | Position Contract Reverse Resolution | broker contract code → exact canonical listed contract | DESIGN_FROZEN | 5 | I04,I05 |
| I650 | Observation-Time Injection | caller 提供 observed_at / as_of_date，不 hidden now | DESIGN_FROZEN | 4 | I05 |
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
| I940 | Capability Evidence Record | source / version / tested mode / date / result 可追蹤 | NOT_DESIGNED | 4 | I06 |

---

## CURRENT / TARGET / MIGRATION

CURRENT：

- existing Shioaji adapter 位於 `backtest/shioaji_*`。
- submit / status / cancel 已存在。
- deal → Fill、multi-fill、dedup、partial fill 已存在。
- BrokerInstrumentReference native lookup 已有 foundation。
- account / position canonical mapping 尚未完成。
- `ShioajiBroker.submit_order()` 仍使用 order_id prefix 推定 New/Cover。

TARGET：

- Shioaji native implementation 位於 `adapters/sinopac/`。
- core 只看 broker-neutral contracts。
- account / position read capability 與 order execution capability interface-segregated。
- capability matrix 可明確知道 supported / verified / unsafe。

MIGRATION：

- GAP-ACCOUNT-001 只新增 account/position mapping seam，不搬 existing order execution。
- GAP-BROKER-001 才替換 New/Cover inference。
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
- I120-I140 / I720-I940 → GAP-BROKER-002 / GAP-LIVE-001。
- full physical relocation → GAP-ARCH-001 bounded migration。

---

## Domain Acceptance

- I01～I06 全部有 leaf mapping。
- existing implementation 與 target adapter ownership 都清楚。
- GAP-ACCOUNT-001 IDs 與 ACTIVE 完全一致。
- current unsafe New/Cover inference 有明確 future replacement。
- official source requirements 已掛接。
