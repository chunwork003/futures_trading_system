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
| J340 | Expected State Projection | accepted execution fills/events 投影 internal expected state | DESIGN_FROZEN | 5 | J03 |
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
| J610 | ReconciliationResult | 保存 status / expected / actual / evidence | ACCEPTED | 4 | J05 |
| J620 | ReconciliationCase | mismatch lifecycle / review / resolution record | ACCEPTED | 4 | J05 |
| J630 | STRICT_HALT Policy | unresolved mismatch 阻止 READY / live continuation | ACCEPTED | 5 | J05,J06 |
| J640 | MANUAL_REVIEW Policy | mismatch 交明確人工處理，不 silent repair | ACCEPTED | 5 | J05,J06 |
| J650 | BROKER_AUTHORITATIVE Policy Contract | 可表示 broker-authoritative resolution，但不隱含 automatic order/mutation | ACCEPTED | 5 | J05 |
| J660 | INTERNAL_AUTHORITATIVE Policy Contract | 可表示 expected-authoritative resolution，但 corrective execution 需另行授權 | ACCEPTED | 5 | J05 |
| J670 | Comparison Precedence | contract → direction → quantity → MATCH | ACCEPTED | 3 | J05 |
| J680 | UNKNOWN_EXTERNAL_STATE | broker response 無法安全解讀時 explicit unknown state | ACCEPTED | 5 | J05,J06 |
| J690 | No Automatic Corrective Action | comparison/result 本身不產生 broker order | ACCEPTED | 5 | J05 |
| J710 | Startup Expected-State Load | process start 載入 persisted expected state | ACCEPTED | 4 | J06 |
| J720 | Startup Broker Observation | startup query broker actual account/position | ACCEPTED | 4 | J06 |
| J730 | Collection Matching | 多 position collection identity matching | ACCEPTED | 5 | J06 |
| J740 | Startup Reconciliation | persisted/runtime expected 與 broker actual reconcile | ACCEPTED | 5 | J06 |
| J750 | Strategy-State Reconstruction Dependency | account reconciliation 後驗證/reconstruct strategy state | ACCEPTED | 4 | J06 |
| J760 | Readiness Decision | validation 完成後才轉 READY | ACCEPTED | 5 | J06 |
| J770 | HALT / REVIEW Startup State | unresolved mismatch 不得進 unrestricted runtime | ACCEPTED | 5 | J06 |
| J780 | No Silent Startup Repair | startup 不得自動以任一側覆蓋另一側 | ACCEPTED | 5 | J06 |
| J810 | AccountSnapshot Contract | future cash/equity/margin/positions aggregate observation | DESIGN_FROZEN | 4 | J02,J03,J04 |
| J820 | Account Snapshot Observed Time | account-level observation 使用 timezone-aware timestamp | DESIGN_FROZEN | 3 | J04 |
| J830 | Account Snapshot Authority Separation | cash/equity/margin actual observation 不等於 risk scenario config | DESIGN_FROZEN | 4 | J04 |

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
- pairwise / collection reconciliation、policy/case 與 startup readiness foundation 已完成；persistence-backed expected loader 與 restart recovery 留 K Domain。

TARGET：

- `trading.account` 擁有 canonical account contracts。
- `trading.reconciliation` 擁有 expected-vs-actual compare/result/policy。
- broker read capability 與 execution Broker port 分離。

MIGRATION：

- GAP-ACCOUNT-001 不移除 legacy AccountPosition。
- 新 canonical model 與 legacy behavior 先 coexist。
- GAP-RECON-001A / 001B runtime foundation 已完成；persistence-backed recovery integration 留 GAP-08。

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
- J610-J690 → GAP-RECON-001A Policy / Result / Case。
- J710-J780 → GAP-RECON-001B Collection / Startup Readiness。
- J810-J830 deeper broker account snapshot → future Account / Persistence slice。

---

## GAP-RECON-001 Architect Design Freeze

Status：

DESIGN_FROZEN。

Canonical owner：

    trading/reconciliation.py

Runtime plan：

    GAP-RECON-001A
        Policy / Result / Case

    GAP-RECON-001B
        Collection / Startup Readiness

兩個 bounded runtime Work Packages 仍屬同一 GAP。

GAP-RECON-001A 完成後不得宣告整個 GAP CLOSED。

---

### ReconciliationStatus

Canonical values：

    MATCH
    INTERNAL_ONLY
    BROKER_ONLY
    CONTRACT_MISMATCH
    DIRECTION_MISMATCH
    QUANTITY_MISMATCH
    UNKNOWN_EXTERNAL_STATE

Existing six pairwise statuses 保持 compatibility。

UNKNOWN_EXTERNAL_STATE：

- 表示 broker actual state 無法安全取得或解讀。
- 不等於 BROKER_ONLY。
- 不得猜測 actual position。
- pairwise compare_positions() 不自行產生 UNKNOWN。
- 必須由 explicit external-state failure path 建立。

---

### ReconciliationResult

Existing public fields 保持：

    status
    expected
    actual

新增 backward-compatible field：

    evidence: tuple[str, ...] = ()

Rules：

- immutable。
- extra fields forbid。
- evidence entry trim + nonblank。
- evidence 只保存 comparison / observation evidence；不得承擔 hidden action semantics。
- UNKNOWN_EXTERNAL_STATE 必須至少有一筆 evidence。
- UNKNOWN_EXTERNAL_STATE 不得 fabricated BrokerPositionSnapshot。

compare_positions() 既有 precedence 不變：

    contract
    -> direction
    -> quantity
    -> MATCH

compare_positions() 仍然 pure。

---

### ReconciliationPolicy

Canonical enum：

    STRICT_HALT
    MANUAL_REVIEW
    BROKER_AUTHORITATIVE
    INTERNAL_AUTHORITATIVE

STRICT_HALT：

- any unresolved non-MATCH result -> HALT。

MANUAL_REVIEW：

- any unresolved non-MATCH result -> REVIEW_REQUIRED。

BROKER_AUTHORITATIVE：

- 表示 explicit resolution authority 可以選擇 broker actual。
- 本 GAP 不自動 overwrite expected。
- unresolved mismatch 仍為 REVIEW_REQUIRED。

INTERNAL_AUTHORITATIVE：

- 表示 explicit resolution authority 可以選擇 internal expected。
- 本 GAP 不自動送 corrective order。
- unresolved mismatch 仍為 REVIEW_REQUIRED。

Policy 本身不得：

- mutate AccountPosition。
- mutate BrokerPositionSnapshot。
- submit OrderIntent。
- submit broker order。

---

### ReconciliationCase

Canonical immutable case snapshot：

    case_id: str
    result: ReconciliationResult
    policy: ReconciliationPolicy
    state: ReconciliationCaseState
    resolution_note: str | None

ReconciliationCaseState：

    HALT
    REVIEW_REQUIRED
    RESOLVED

Identity：

- case_id 由 caller 提供。
- trim + nonblank。
- 本 Domain 不 hidden-generate UUID。

Creation：

- MATCH 不建立 ReconciliationCase。
- STRICT_HALT mismatch -> HALT。
- MANUAL_REVIEW mismatch -> REVIEW_REQUIRED。
- BROKER_AUTHORITATIVE mismatch -> REVIEW_REQUIRED。
- INTERNAL_AUTHORITATIVE mismatch -> REVIEW_REQUIRED。

Resolution：

- HALT / REVIEW_REQUIRED 可 pure transition 成 RESOLVED。
- RESOLVED 必須有 nonblank resolution_note。
- resolution 只記錄 domain decision。
- resolution 不等於 overwrite、fill、order 或 broker repair。

Time semantics：

- 本 GAP 不 hidden call now()。
- case/event occurred time 與 persistence audit time 留 K Domain。

---

### UNKNOWN_EXTERNAL_STATE Error Boundary

建立 explicit：

    ExternalStateUnknownError

Rules：

- 只代表 broker observation 無法安全取得或 canonicalize。
- startup orchestration 只可將此 explicit error 轉成 UNKNOWN_EXTERNAL_STATE。
- 不得 catch-all Exception 後假裝 UNKNOWN。
- programming error / unrelated runtime error 必須 propagate。

---

### Collection Identity

Collection reconciliation scope key：

    broker
    account_ref
    instrument_id

Exact position key：

    broker
    account_ref
    instrument_id
    contract_id

Rules：

- 同一 side 不得有 duplicate exact position key。
- duplicate -> explicit ReconciliationCollectionError。
- 不得 arbitrary pair positions。

---

### Deterministic Collection Matching

每個 broker/account/instrument scope：

1. 先配對 exact contract_id。
2. exact pair 使用 compare_positions()。
3. 只剩 expected -> INTERNAL_ONLY。
4. 只剩 actual -> BROKER_ONLY。
5. exactly one expected leftover + one actual leftover -> CONTRACT_MISMATCH pair。
6. 若雙方仍有多筆 unmatched 且無唯一配對 -> ReconciliationCollectionError。

不得：

- 依 list order 猜配對。
- 依 quantity 猜配對。
- 依 direction 猜配對。
- silent drop duplicate。

Output order 必須 deterministic。

---

### ExpectedPositionLoader

Startup expected-state 使用 read-only protocol seam：

    load_positions(
        account: BrokerAccount
    ) -> tuple[AccountPosition, ...]

Rules：

- protocol owner 為 trading.reconciliation。
- 本 GAP 不實作 PostgreSQL repository。
- PostgreSQL / persisted snapshot backend 留 GAP-08。
- loader 不得 mutate expected state。

---

### Broker Observation

Startup actual-state 使用既有：

    BrokerPositionProvider

Rules：

- reconciliation 不擴充 execution Broker port。
- provider 只讀。
- native Shioaji object 不得進 reconciliation domain。

---

### StartupReadinessState

Canonical values：

    READY
    HALT
    REVIEW

READY：

- expected state load succeeded。
- broker observation succeeded。
- collection reconciliation completed。
- all reconciliation results MATCH。
- strategy-state dependency 已明確確認 ready。

HALT：

- STRICT_HALT 遇任何 unresolved non-MATCH。
- strategy-state dependency 尚未 ready。
- explicit safety prerequisite failed。

REVIEW：

- MANUAL_REVIEW unresolved mismatch。
- BROKER_AUTHORITATIVE unresolved mismatch。
- INTERNAL_AUTHORITATIVE unresolved mismatch。
- UNKNOWN_EXTERNAL_STATE under non-STRICT policy。

不得從 HALT / REVIEW silent promotion READY。

---

### StartupReconciliationResult

Immutable result 至少保存：

    policy
    state
    results
    strategy_state_ready

Rules：

- READY 只在 results 全 MATCH 且 strategy_state_ready=True。
- result 不執行 repair。
- result 不寫 persistence。
- result 不啟動 strategy。

---

### Startup Orchestration

Conceptual flow：

    BrokerAccount
    -> ExpectedPositionLoader
    -> BrokerPositionProvider
    -> deterministic collection reconciliation
    -> policy evaluation
    -> strategy-state dependency check
    -> READY / HALT / REVIEW

Explicit ExternalStateUnknownError：

- 轉 UNKNOWN_EXTERNAL_STATE。
- STRICT_HALT -> HALT。
- other policy -> REVIEW。

其他 unexpected exceptions：

- propagate。
- 不 silent downgrade。

---

### Strategy-State Reconstruction Dependency

本 GAP 只建立 readiness dependency。

不實作：

- strategy state persistence。
- strategy state reconstruction algorithm。
- feature-state recovery。

Caller 必須 explicit 提供：

    strategy_state_ready: bool

False：

    HALT

True 且 account reconciliation clean：

    可 READY

真正 recovery/reconstruction 留 GAP-08。

---

### Corrective Action Boundary

即使 GAP-BROKER-001 已完成 explicit OrderIntent：

GAP-RECON-001 仍不得：

- automatic broker repair。
- automatic expected overwrite。
- automatic position adoption。
- automatic corrective OrderIntent。

BROKER_AUTHORITATIVE / INTERNAL_AUTHORITATIVE 只是 resolution authority contract。

未來 corrective execution 必須另有 explicit frozen Work Package。

---

### Compatibility

Existing：

    compare_positions(expected, actual)

以及既有 six ReconciliationStatus values 必須保持 green。

ReconciliationResult 新 evidence field 必須有 default，避免破壞既有 caller。

GAP-ACCOUNT-001 accepted behavior 不得改寫。

---

### Runtime Slice Plan

GAP-RECON-001A — Policy / Result / Case：

    J610
    J620
    J630
    J640
    J650
    J660
    J670
    J680
    J690

完成 001A 後：

- GAP-RECON-001 remains OPEN / PARTIAL。
- 不得開始 GAP-BROKER-002。

GAP-RECON-001B — Collection / Startup Readiness：

    J710
    J720
    J730
    J740
    J750
    J760
    J770
    J780

完成 001B 並 acceptance 後才可關閉 GAP-RECON-001。

---

### Explicit Out of Scope

- J340 expected fill/event projection。
- J810-J830 AccountSnapshot。
- PostgreSQL。
- ReconciliationCase persistence。
- restart persistence recovery。
- strategy reconstruction implementation。
- automatic corrective execution。
- broker native mapping changes。
- strategy changes。
- LIVE authorization。

## GAP-08EFGHI Account Persistence Dependency Freeze

Status：DESIGN_FROZEN。

Implements：

J340 J810 J820 J830。

### Expected Position Projection

Pure projection uses canonical Order + Fill + current AccountPosition。

Rules：

- OPEN on FLAT creates expected position from actual filled quantity。
- OPEN same direction adds actual filled quantity。
- REDUCE subtracts actual filled quantity and must remain positive。
- CLOSE subtracts fills；only exact zero becomes position absence。
- partial CLOSE keeps remaining position。
- opposite direction never silently reverses。
- identity mismatch rejects。

### AccountPositionSnapshot Batch

Persistence snapshot represents a complete expected-position collection for one broker account。

Fields：

    snapshot_id
    broker
    account_ref
    effective_at
    recorded_at
    source_event_id
    positions tuple[AccountPosition, ...]

Empty positions is valid and explicitly means expected FLAT collection。

latest/as_of ordering：

    effective_at
    then recorded_at
    then snapshot_id

as_of compares effective_at <= requested time。

### BrokerPositionObservation Batch

Fields：

    observation_id
    broker
    account_ref
    observed_at
    recorded_at
    positions tuple[BrokerPositionSnapshot, ...]

Empty positions is valid and preserves an observed FLAT account state。

All contained positions must match broker/account and observed_at of the batch。

Persisted broker observations are audit/history；startup actual authority still comes from BrokerPositionProvider query。

### AccountSnapshot

Canonical actual account observation owner：

    trading/account.py

Minimum immutable fields：

    snapshot_id
    broker
    account_ref
    observed_at
    recorded_at
    currency
    cash_balance Decimal optional
    equity Decimal optional
    available_funds Decimal optional
    margin_used Decimal optional

At least one monetary observation must exist。

AccountSnapshot is broker-observed actual evidence；not risk configuration。

Expected position snapshots and broker actual observations use separate repositories/tables and can never overwrite each other。

---

## Domain Acceptance

- J01～J06 全部有 leaf mapping。
- ACTIVE J IDs 完全存在。
- expected / actual / policy / execution authority 不混淆。
- startup readiness 與 pairwise comparison 明確分階段。
