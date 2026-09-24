# F — Backtest / Research

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

提供 deterministic historical replay、模擬 execution、position/trade accounting、performance、optimization、OOS、walk-forward 與 Monte Carlo research。

Backtest 是 canonical trading contracts 的 historical consumer，不是 live canonical owner。

主要 current package：

- `backtest/`
- `analysis/`

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| F100 | Historical Replay | deterministic clock / next-bar execution |
| F200 | Execution Simulation | historical order/fill semantics |
| F300 | Position / Trade Accounting | position lifecycle / PnL / equity |
| F400 | Cost / Slippage | commission / slippage / transaction cost |
| F500 | Performance Analysis | trade statistics / return / drawdown |
| F600 | Optimization | parameter search / sensitivity / stability |
| F700 | OOS / Walk Forward | train/test windows / out-of-sample validation |
| F800 | Monte Carlo | trade-path uncertainty simulation |
| F900 | Research Comparison / Reporting | result comparison / report projection |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| F110 | Deterministic Historical Clock | historical bar order / time progression deterministic | ACCEPTED | 3 | F01 |
| F120 | Next-Bar Execution Semantics | signal 不能同 bar 偷看未來成交 | ACCEPTED | 4 | F01 |
| F130 | Deterministic Reset | repeated run 不受前次 mutable state 污染 | ACCEPTED | 3 | F01 |
| F140 | End-of-Data Handling | dataset 結束 position lifecycle 明確 | ACCEPTED | 2 | F01,F03 |
| F210 | Historical Order Projection | strategy signal/decision 轉為 historical execution request | ACCEPTED | 3 | F02,F03 |
| F220 | Fill Simulation | deterministic historical fill generation | ACCEPTED | 3 | F02 |
| F230 | Stop / Target Execution | SL / TP historical execution semantics | ACCEPTED | 4 | F03 |
| F240 | Partial / Async Lifecycle Compatibility | execution lifecycle 與現有 broker/paper semantics 相容 | ACCEPTED | 4 | F03 |
| F250 | LONG / SHORT Lifecycle | long / short entry / exit symmetry | ACCEPTED | 4 | F03 |
| F260 | Forced Liquidation / End Exit | forced/end exit 明確 reason | ACCEPTED | 3 | F03 |
| F310 | Historical Position Projection | position entry / exit / quantity / direction | ACCEPTED | 3 | F03,F04 |
| F320 | Trade Projection | completed economic trade representation | ACCEPTED | 3 | F03 |
| F330 | Equity Curve | trade/fill outcome → historical equity projection | ACCEPTED | 3 | F04 |
| F340 | Drawdown Projection | peak/equity → drawdown / drawdown pct | ACCEPTED | 3 | F04 |
| F350 | Historical Portfolio | backtest portfolio 是 research projection，不是 broker truth | DESIGN_FROZEN | 4 | F04 |
| F410 | Commission Model | per-order/per-contract commission accounting | ACCEPTED | 2 | F02 |
| F420 | Slippage Model | requested vs simulated fill price cost | ACCEPTED | 2 | F02 |
| F430 | Cost Attribution | commission / slippage 可計入 trade/equity | ACCEPTED | 3 | F02,F04 |
| F510 | Trade Statistics | trade count / win rate / average trade 等 | ACCEPTED | 2 | F05 |
| F520 | Profit Factor / Expectancy | performance quality metrics | ACCEPTED | 2 | F05 |
| F530 | Return Metrics | final return / period return correctness | IMPLEMENTED | 3 | F05 |
| F540 | Risk-Adjusted Metrics | Sharpe / related metric final validation | DESIGNED | 3 | F05 |
| F550 | Drawdown Metrics | absolute / percentage drawdown report | ACCEPTED | 2 | F05 |
| F610 | Parameter Optimization | bounded parameter search | ACCEPTED | 3 | F06 |
| F620 | Optimization Constraints | trades / PF / DD 等 acceptance constraints | ACCEPTED | 2 | F06 |
| F630 | Parameter Sensitivity | nearby parameter robustness analysis | ACCEPTED | 3 | F06 |
| F640 | Parameter Stability | parameter region stability analysis | ACCEPTED | 3 | F06 |
| F650 | Baseline Comparison | optimized result 與 baseline 可比較 | ACCEPTED | 2 | F06 |
| F710 | Walk-Forward Window Generation | deterministic train/test windows | ACCEPTED | 3 | F07 |
| F720 | Walk-Forward Optimization | train select / test evaluate | ACCEPTED | 4 | F07 |
| F730 | OOS Aggregation | 多 window out-of-sample result aggregation | ACCEPTED | 3 | F07 |
| F740 | OOS Consistency | positive/non-negative window consistency | ACCEPTED | 2 | F07 |
| F750 | Parameter Selection Frequency | selected parameter across OOS windows 可分析 | ACCEPTED | 2 | F07 |
| F810 | Monte Carlo Shuffle | trade ordering uncertainty simulation | ACCEPTED | 3 | F08 |
| F820 | Monte Carlo Bootstrap | resampled trade distribution simulation | ACCEPTED | 3 | F08 |
| F830 | Monte Carlo Deterministic Seed | same seed / input 可重現 | ACCEPTED | 2 | F08 |
| F840 | Monte Carlo Distribution Report | percentile / probability / drawdown distribution | ACCEPTED | 3 | F08 |
| F910 | Strategy / Parameter Comparison | research result cross-run comparison | ACCEPTED | 2 | F06,F08 |
| F920 | Result Serialization | result/report 可轉成 stable structured output | IMPLEMENTED | 2 | F05,F07,F08 |
| F930 | Research Provenance Hook | future report 可連 git/config/data/feature version | DESIGNED | 3 | F05,F06 |

---

## CURRENT / TARGET / MIGRATION

CURRENT：

BacktestEngine、execution、portfolio、optimization、walk-forward、OOS、Monte Carlo 已有成熟 implementation 與 regression。

TARGET：

backtest 只保留 historical deterministic simulation / research responsibility。

Canonical Order / Fill / Account / Decision 等跨 runtime contract 長期由 trading core 擁有。

MIGRATION：

- 不重寫 BacktestEngine。
- 不一次搬移所有 backtest models。
- canonical trading contract 有實際 consumer 後逐 slice compatibility migration。
- historical behavior 必須保持 targeted + full regression。

---

## Connections

| From | To | Contract |
|---|---|---|
| B500 | F100 | canonical historical dataset |
| C/D | F100 | calendar / contract / specification |
| E | F100/F200 | features / strategy outputs |
| G | F200 | decision / sizing / risk result |
| F200 | F300 | simulated fills |
| F300 | F500 | trades / equity |
| F500 | F600/F700/F800 | evaluation metrics |
| F900 | M400 | future research/backtest service result |

---

## Authority

- historical replay semantics：F Domain。
- backtest portfolio/equity：historical projection only。
- live AccountPosition：J Domain。
- canonical execution models：target H Domain。
- operational persistence：K Domain。

---

## Technical Sources

- SRC-PYDANTIC-001。
- SRC-POLARS-001。
- SRC-PYTEST-001。
- SRC-ADR-001。

---

## Key Invariants

- next-bar semantics 不得被 optimization / strategy 改寫。
- same input/config/seed 必須 deterministic。
- historical portfolio 不等於 live broker account truth。
- trade result 不反向成為 fill/order authority。
- parameter optimization 不得使用 OOS future information。
- walk-forward timestamps 必須 strictly increasing。
- Monte Carlo seed 必須可重現。

---

## Remaining Work

- F530/F540 final Return / Sharpe validation。
- F930 provenance integration 在 persistence/service phase 補強。
- advanced execution model 屬 Simulation Domain，不應塞回 baseline Paper/Backtest。

---

## Domain Acceptance

- F01～F08 全部有 leaf mapping。
- replay / execution / accounting / analytics / optimization responsibility 分離。
- mature backtest behavior 明確標為 preserve。
- future canonical ownership migration 不觸發 big-bang rewrite。
