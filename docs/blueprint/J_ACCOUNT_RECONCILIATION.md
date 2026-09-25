# J — Account / Reconciliation

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

管理 internal expected physical account state、broker actual observations，以及兩者的 reconciliation / startup readiness。

核心 invariant：

    StrategyPosition
    != TargetAccountPosition
    != AccountPosition
    != BrokerPositionSnapshot

Target ownership：

    trading/account.py
    trading/reconciliation.py

Current compatibility：

    backtest/account_position.py

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| J100 | Logical Account | internal capital / strategy allocation identity |
| J200 | Broker Account | physical broker account identity |
| J300 | Internal Expected Position | system expected physical position |
| J400 | Broker Actual Position | broker-observed position snapshot |
| J500 | Pure Comparison | deterministic expected-vs-actual comparison |
| J600 | Reconciliation Policy | mismatch handling policy / case state |
| J700 | Startup Readiness | process startup sync / READY gate |
| J800 | Account Snapshot | future cash/equity/margin/position observation |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| J110 | LogicalAccount Identity | internal capital bucket identity | DESIGNED | 4 | J01 |
| J120 | Logical / Broker Separation | LogicalAccount 不等同 BrokerAccount | DESIGN_FROZEN | 4 | J01,J02 |
| J130 | Strategy Allocation | logical account 可承載 strategy allocation | DESIGNED | 3 | J01 |
| J140 | Capital Source Policy | V1 MANUAL capital source；cross-strategy borrowing OFF | DESIGN_FROZEN | 3 | J01 |
| J210 | BrokerAccount Model | broker-neutral physical account reference | ACCEPTED | 4 | J02 |
| J220 | Broker Stable Account Reference | broker + stable opaque account_ref | ACCEPTED | 4 | J02 |
| J230 | Broker Account Metadata Validation | optional account type / display metadata，禁止 secret/PII/native object | ACCEPTED | 4 | J02 |
| J240 | BrokerAccountProvider | separate read-only broker account capability | ACCEPTED | 4 | J02 |
| J250 | LogicalAccount-to-BrokerAccount Mapping | future allocation-to-physical-account relation | DESIGNED | 4 | J01,J02 |
| J310 | Canonical AccountPosition | internal expected consolidated physical position | ACCEPTED | 5 | J03 |
| J320 | Expected Position Identity | broker / account_ref / instrument / listed contract identity | ACCEPTED | 4 | J03 |
| J330 | Expected Quantity / Direction Semantics | LONG/SHORT + quantity > 0；zero 代表 position absence | ACCEPTED | 4 | J03 |
| J340 | Expected State Projection | accepted execution fills/events 投影 internal expected state | DESIGNED | 5 | J03 |
| J350 | Legacy AccountPosition Compatibility | existing minimal backtest model 保留，bounded migration | DESIGN_FROZEN | 3 | J03 |
| J360 | Legacy Minimal AccountPosition Runtime Foundation | `backtest.account_position.AccountPosition` 已存在並有直接 unit test；僅代表 legacy runtime foundation，不是 canonical target | UNIT_VERIFIED | 2 | J03 |
| J410 | BrokerPositionProvider | separate read-only broker position capability | ACCEPTED | 4 | J04 |
| J420 | BrokerPositionSnapshot | broker-neutral actual position observation | ACCEPTED | 5 | J04 |
| J430 | Actual Position Identity | broker/account/instrument/listed-contract exact identity | ACCEPTED | 5 | J04 |
| J440 | Observation / Decimal Semantics | timezone-aware observed_at；average_price 使用 Decimal | ACCEPTED | 4 | J04 |
| J450 | Actual Quantity / Direction | broker actual LONG/SHORT + quantity > 0 | DESIGN_FROZEN | 4 | J04 |
| J460 | Snapshot Immutability Semantics | observation 是當下事實，不是 mutable expected state | DESIGN_FROZEN | 4 | J04 |
| J470 | No Silent Expected-State Overwrite | broker snapshot 不得直接覆寫 AccountPosition | DESIGN_FROZEN | 5 | J03,J04 |
| J510 | Pairwise Position Comparator | pure expected / actual comparison | ACCEPTED | 5 | J05 |
| J520 | ReconciliationStatus | mismatch classification enum | ACCEPTED | 3 | J05 |
| J530 | MATCH | expected 與 actual contract/direction/quantity 一致 | ACCEPTED | 2 | J05 |
| J540 | INTERNAL_ONLY | expected 有 position；broker actual 無 position | ACCEPTED | 3 | J05 |
| J550 | BROKER_ONLY | broker actual 有 position；internal expected 無 position | ACCEPTED | 4 | J05 |
| J560 | CONTRACT_MISMATCH | same account/instrument scope but listed contract 不一致 | ACCEPTED | 4 | J05 |
| J570 | DIRECTION_MISMATCH | contract comparable，但 direction 不一致 | ACCEPTED | 5 | J05 |
| J580 | QUANTITY_MISMATCH | contract/direction 相同，但 quantity 不一致 | ACCEPTED | 4 | J05 |
| J590 | Non-Comparable Identity Error | broker/account/instrument identity 不同時 explicit comparison error | ACCEPTED | 4 | J05 |
| J610 | ReconciliationResult | 保存 status / expected / actual / evidence | DESIGNED | 4 | J05 |
| J620 | ReconciliationCase | mismatch lifecycle / review / resolution record | DESIGNED | 4 | J05 |
| J630 | STRICT_HALT Policy | unresolved mismatch 阻止 READY / live continuation | DESIGN_FROZEN | 5 | J05,J06 |
| J640 | MANUAL_REVIEW Policy | mismatch 交明確人工處理，不 silent repair | DESIGN_FROZEN | 5 | J05,J06 |
| J650 | BROKER_AUTHORITATIVE Policy Contract | 可表示 broker-authoritative resolution，但不隱含 automatic order/mutation | DESIGNED | 5 | J05 |
| J660 | INTERNAL_AUTHORITATIVE Policy Contract | 可表示 expected-authoritative resolution，但 corrective execution 需另行授權 | DESIGNED | 5 | J05 |
| J670 | Comparison Precedence | contract → direction → quantity → MATCH | DESIGN_FROZEN | 3 | J05 |
| J680 | UNKNOWN_EXTERNAL_STATE | broker response 無法安全解讀時 explicit unknown state | DESIGNED | 5 | J05,J06 |
| J690 | No Automatic Corrective Action | comparison/result 本身不產生 broker order | DESIGN_FROZEN | 5 | J05 |
| J710 | Startup Expected-State Load | process start 載入 persisted expected state | DESIGNED | 4 | J06 |
| J720 | Startup Broker Observation | startup query broker actual account/position | DESIGNED | 4 | J06 |
| J730 | Collection Matching | 多 position collection identity matching | DESIGNED | 5 | J06 |
| J740 | Startup Reconciliation | persisted/runtime expected 與 broker actual reconcile | DESIGNED | 5 | J06 |
| J750 | Strategy-State Reconstruction Dependency | account reconciliation 後驗證/reconstruct strategy state | DESIGNED | 4 | J06 |
| J760 | Readiness Decision | validation 完成後才轉 READY | DESIGNED | 5 | J06 |
| J770 | HALT / REVIEW Startup State | unresolved mismatch 不得進 unrestricted runtime | DESIGN_FROZEN | 5 | J06 |
| J780 | No Silent Startup Repair | startup 不得自動以任一側覆蓋另一側 | DESIGN_FROZEN | 5 | J06 |
| J810 | AccountSnapshot Contract | future cash/equity/margin/positions aggregate observation | DESIGNED | 4 | J02,J03,J04 |
| J820 | Account Snapshot Observed Time | account-level observation 使用 timezone-aware timestamp | DESIGNED | 3 | J04 |
| J830 | Account Snapshot Authority Separation | cash/equity/margin actual observation 不等於 risk scenario config | DESIGNED | 4 | J04 |

---

## GAP-ACCOUNT-001 Frozen Scope

Implements：

    J210
    J220
    J230
    J240

    J310
    J320
    J330

    J410
    J420
    J430
    J440

    J510
    J520
    J530
    J540
    J550
    J560
    J570
    J580
    J590

Explicitly does not implement：

    J600 policy execution
    J700 startup readiness
    corrective broker execution

---

## Comparison Semantics

Pairwise comparator：

    expected=None, actual=None
        → MATCH

    expected!=None, actual=None
        → INTERNAL_ONLY

    expected=None, actual!=None
        → BROKER_ONLY

    both present
        → validate broker/account/instrument comparability
        → CONTRACT_MISMATCH
        → DIRECTION_MISMATCH
        → QUANTITY_MISMATCH
        → MATCH

Comparator：

- pure。
- no mutation。
- no broker call。
- no corrective order。

---

## CURRENT / TARGET / MIGRATION

CURRENT：

- `backtest.account_position.AccountPosition` 僅有 symbol/contract/direction/quantity。
- canonical BrokerAccount 已由 GAP-ACCOUNT-001 runtime implemented。
- canonical BrokerPositionSnapshot 已由 GAP-ACCOUNT-001 runtime implemented。
- pairwise expected/actual comparison foundation 已完成；reconciliation policy、collection matching 與 startup readiness 尚未 implemented。

TARGET：

- `trading.account` 擁有 canonical account contracts。
- `trading.reconciliation` 擁有 expected-vs-actual compare/result/policy。
- broker read capability 與 execution Broker port 分離。

MIGRATION：

- GAP-ACCOUNT-001 不移除 legacy AccountPosition。
- 新 canonical model 與 legacy behavior 先 coexist。
- multi-position/startup/policy 留 GAP-RECON-001。

---

## Connections

| From | To | Contract |
|---|---|---|
| G400 | J300 | desired target vs expected account state |
| H400 | J300 | Fill / OrderEvent 更新 expected projection |
| I500 | J200 | BrokerAccount observation |
| I600 | J400 | BrokerPositionSnapshot |
| J300/J400 | J500 | expected vs actual |
| J500 | J600 | mismatch result |
| J600/J700 | K/L | persisted case / runtime readiness |
| K700 | J700 | recovered expected state |

---

## Authority

- LogicalAccount：internal allocation identity。
- BrokerAccount：physical broker account reference。
- AccountPosition：internal expected physical position。
- BrokerPositionSnapshot：broker actual observation。
- ReconciliationResult：comparison outcome。
- Reconciliation policy 不改變 execution authority。

---

## Key Invariants

- LogicalAccount != BrokerAccount。
- StrategyPosition != TargetAccountPosition != AccountPosition != BrokerPositionSnapshot。
- PositionDirection canonical values 為 LONG / SHORT。
- quantity = 0 代表沒有 position，不建立 zero-quantity position object。
- BrokerPositionSnapshot observed_at 必須 timezone-aware。
- operational average price 使用 Decimal。
- broker actual 不得 silent overwrite internal expected。
- reconciliation comparator 不得執行 corrective order。
- startup unresolved mismatch 預設 STRICT_HALT / MANUAL_REVIEW。
- automatic corrective broker execution 必須先完成 H200 explicit PositionEffect。

---

## Sources

- SRC-SINOPAC-LOGIN-001。
- SRC-SINOPAC-POSITION-001。
- SRC-SINOPAC-CONTRACT-001。
- SRC-PYDANTIC-001。
- SRC-ADR-001。
- SRC-ARCH-001。

---

## Current GAP Mapping

- J210-J590 selected leaves → GAP-ACCOUNT-001。
- J610-J780 → GAP-RECON-001。
- J810-J830 deeper broker account snapshot → future Account / Persistence slice。

---

## Domain Acceptance

- J01～J06 全部有 leaf mapping。
- ACTIVE J IDs 完全存在。
- expected / actual / policy / execution authority 不混淆。
- startup readiness 與 pairwise comparison 明確分階段。
