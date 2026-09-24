# G — Decision / Risk

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

將各 Strategy 的 logical intent / virtual position 統合成 account-level target，再經 position sizing、capital management 與 portfolio risk 產生可稽核的 RiskDecision。

此 Domain 決定 expected target / permission。

此 Domain 不直接呼叫 broker。

主要 current runtime：

- `backtest/decision*.py`
- `backtest/strategy_position.py`
- `backtest/strategy_conflict_policy.py`
- `backtest/strategy_attribution.py`
- `backtest/target_position.py`
- `backtest/position_sizing*.py`
- `backtest/*risk*.py`
- `backtest/*capital*.py`

Target ownership：

    trading/decision/
    trading/risk/

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| G100 | Strategy Intent | strategy logical requested change |
| G200 | Strategy Virtual Position | per-strategy logical exposure |
| G300 | Conflict Resolution | long/short strategy conflict policy |
| G400 | Target Account Position | final desired account exposure |
| G500 | Attribution / Netting | target provenance / strategy contribution |
| G600 | Position Sizing | quantity calculation |
| G700 | Capital Management | capital reference / allocation / protection |
| G800 | Pre-Trade Risk | margin / exposure / entry permission |
| G900 | Runtime Risk / RiskDecision | auditable risk outcome / runtime guard input |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| G110 | Strategy Intent Contract | Strategy 只表達 logical desired action，不直接下 broker order | DESIGN_FROZEN | 4 | G01,G02 |
| G120 | Intent Identity / Provenance | intent 可追到 strategy / version / context | DESIGNED | 3 | G01,G08 |
| G130 | Intent Direction / Quantity Semantics | logical direction / desired quantity 明確 | DESIGN_FROZEN | 3 | G01 |
| G210 | StrategyVirtualPosition | 個別 strategy logical position | ACCEPTED | 4 | G01 |
| G220 | Virtual Position Identity | strategy + symbol + contract + direction identity | ACCEPTED | 3 | G01 |
| G230 | Virtual Position Priority | strategy conflict resolution 可使用 explicit priority | ACCEPTED | 2 | G01,G02 |
| G240 | Virtual / Physical Separation | StrategyPosition 不等於 account physical position | DESIGN_FROZEN | 4 | G01 |
| G310 | Conflict Detection | 同一 account target scope 出現 opposite directions 時明確偵測 | ACCEPTED | 3 | G02 |
| G320 | Conflict Policy Contract | conflict policy 為 explicit strategy decision contract | ACCEPTED | 3 | G02 |
| G330 | Conflict Resolution Determinism | 相同 inputs / policy 產生相同 selected direction | ACCEPTED | 3 | G02 |
| G340 | No-Policy Conflict Failure | conflict 無 policy 時明確失敗，不 silent net | ACCEPTED | 3 | G02 |
| G410 | TargetAccountPosition | Multi-Strategy Decision 最終 expected physical target | ACCEPTED | 4 | G03 |
| G420 | Target Identity | symbol / listed contract / direction / quantity | ACCEPTED | 3 | G03 |
| G430 | Target Aggregation | 同方向 strategy quantity 統合 | ACCEPTED | 3 | G03,G04 |
| G440 | HOLD / ADD / REDUCE / EXIT / ENTER | current expected vs target 的決策動作 | ACCEPTED | 4 | G03,G05 |
| G450 | Direction Change Decision Invariant | opposite target 必須先 EXIT，再等待 FLAT，再重新評估 | DESIGN_FROZEN | 5 | G05 |
| G460 | No Silent Reverse | decision layer 不直接產生 simultaneous close/open reversal | DESIGN_FROZEN | 5 | G05 |
| G510 | StrategyAttribution | target quantity 可追到 strategy contribution | ACCEPTED | 3 | G04 |
| G520 | Attribution Quantity Integrity | attribution quantity 與 selected contribution 一致 | ACCEPTED | 3 | G04 |
| G530 | Netting Boundary | strategy logical netting 與 broker/account physical state 分離 | DESIGN_FROZEN | 4 | G04 |
| G610 | PositionSizingInput | equity / price / stop / multiplier / risk budget input contract | ACCEPTED | 3 | G07 |
| G620 | Fixed Quantity Sizing | fixed quantity sizing policy | ACCEPTED | 2 | G07 |
| G630 | Fixed Risk Sizing | equity × risk budget / per-contract loss sizing | ACCEPTED | 3 | G07 |
| G640 | Per-Contract Risk Sizing | explicit contract risk-based quantity | ACCEPTED | 2 | G07 |
| G650 | Stop-Based Sizing | stop distance / multiplier 驅動 sizing | ACCEPTED | 3 | G07 |
| G660 | Sizing Registry / Selection | sizing strategy 可註冊與選擇 | ACCEPTED | 2 | G07 |
| G710 | Capital Reference Strategy | capital calculation/reference 可替換 | ACCEPTED | 3 | G07 |
| G720 | Fixed-Ratio Capital Management | profit/loss/equity state 驅動 position capital | ACCEPTED | 3 | G07 |
| G730 | Capital Drawdown Handling | capital protection / drawdown policy | ACCEPTED | 3 | G07 |
| G740 | Capital Source Boundary | V1 CapitalSource = MANUAL，cross-strategy borrowing OFF | DESIGN_FROZEN | 4 | G07 |
| G810 | PortfolioRiskManager | margin / exposure / capital risk foundation | ACCEPTED | 4 | G06 |
| G820 | Initial Margin Gate | entry quantity 必須符合 initial margin constraint | ACCEPTED | 3 | G06 |
| G830 | Maintenance Margin Check | maintenance threshold 可觸發 liquidation requirement | ACCEPTED | 3 | G06 |
| G840 | Max Contracts | position quantity 上限 | ACCEPTED | 2 | G06 |
| G850 | Margin Utilization | margin / equity utilization constraint | ACCEPTED | 3 | G06 |
| G860 | Position Exposure | price × quantity × multiplier exposure calculation | ACCEPTED | 2 | G06 |
| G870 | Canonical Margin Consumer | risk 可使用 D500 canonical effective-dated margin | ACCEPTED | 4 | G06 |
| G880 | RiskConfig Override Precedence | explicit scenario override → canonical schedule → explicit no-margin → error | DESIGN_FROZEN | 4 | G06 |
| G910 | RiskDecision Model | allow / reject / reduce / reason 的 canonical auditable result | DESIGNED | 4 | G08 |
| G920 | Risk Reason / Evidence | risk outcome 保存 constraint / input evidence | DESIGNED | 3 | G08 |
| G930 | Risk Provenance | RiskDecision 可連 strategy / target / config / margin source | DESIGNED | 4 | G08 |
| G940 | Runtime Risk Input Boundary | live runtime guards 消費 canonical risk/account/reconciliation state | DESIGNED | 4 | G08 |
| G950 | Risk Persistence Boundary | RiskDecision future 交 K Domain 保存，不由 G 直接寫 DB | DESIGN_FROZEN | 3 | G08 |

---

## CURRENT / TARGET / MIGRATION

CURRENT：

- MultiStrategyDecisionLayer 已存在。
- StrategyVirtualPosition 已存在。
- TargetAccountPosition 已存在。
- HOLD / ADD / REDUCE / EXIT / ENTER 已有 decision foundation。
- multiple sizing strategies 已存在。
- PortfolioRiskManager 已存在。
- canonical RiskDecision 尚未完整。
- 多數 runtime model 歷史上位於 `backtest/`。

TARGET：

- canonical Decision / Risk ownership 移至 `trading/decision` / `trading/risk`。
- StrategyIntent、StrategyPosition、TargetAccountPosition、RiskDecision 為 broker-neutral。
- Decision / Risk 不依賴 Shioaji。

MIGRATION：

- 不為 Blueprint 做 big-bang move。
- existing backtest imports 保持 compatibility。
- 每個 consumer slice 有實際需求時才移入 canonical trading owner。

---

## Connections

| From | To | Contract |
|---|---|---|
| E500/E600 | G100/G200 | strategy intent / virtual position |
| G200 | G300 | logical strategy positions |
| G300/G500 | G400 | resolved target + attribution |
| G400 | G600/G700/G800 | target / sizing / capital / risk inputs |
| D100/D500 | G600/G800 | multiplier / margin specification |
| G800/G900 | H200 | accepted risk decision + execution intent input |
| G900 | K800 | future risk provenance persistence |
| J/L | G940 | account / reconciliation / runtime safety inputs |

---

## Authority

- StrategyPosition：strategy logical exposure。
- TargetAccountPosition：desired physical account target。
- RiskDecision：risk permission / rejection / evidence。
- AccountPosition：不是 G authority。
- BrokerPositionSnapshot：不是 G authority。
- Order / Fill：不是 G authority。

---

## Key Invariants

- StrategyPosition != TargetAccountPosition != AccountPosition != BrokerPositionSnapshot。
- Strategy 不直接決定 broker physical position。
- Decision Layer 才統合 strategy conflict。
- opposite direction 必須 EXIT → confirmed FLAT → re-evaluate → ENTER。
- missing canonical margin 不得 silent 變成 zero。
- research float allowed；future operational money boundary 使用 Decimal / NUMERIC。
- risk result 不直接呼叫 broker。

---

## Internal Sources

- SRC-ADR-001。
- SRC-ARCH-001。
- SRC-BLUEPRINT-001。

---

## Current GAP Mapping

- G910-G950 → GAP-PERSIST-001 / future canonical RiskDecision work。
- operational account-aware runtime risk → GAP-LIVE-001。
- ownership migration → GAP-ARCH-001 / GAP-ARCH-002 bounded slices。

---

## Domain Acceptance

- G01～G08 全部有 leaf mapping。
- strategy / target / expected account / broker actual boundaries 不混淆。
- sizing / capital / risk 各自責任明確。
- wait-for-flat rule 有唯一 decision invariant。
