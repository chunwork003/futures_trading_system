# Futures Trading System Architecture

## 1. Project Goal

建立可長期演進的台灣期貨量化交易研究與回測系統。

核心流程：

Data
→ Cleaning
→ Trading Calendar
→ 1m Bars
→ Features
→ Strategy
→ Signal
→ Backtest
→ Order
→ Execution
→ Position
→ Portfolio
→ Trade
→ Metrics
→ Research
→ Walk-Forward / OOS
→ Monte Carlo
→ Live Trading

## 2. Supported Products

目前規劃：

- TX：臺股期貨
- MTX：小型臺指期貨
- TMF：微型臺指期貨
- TWII：臺灣加權指數

## 3. Technology Stack

- Python
- Polars
- Parquet
- DuckDB
- Pydantic
- pytest

## 4. Main Layers

### Data Layer

負責：

- 原始資料取得
- 清洗
- 欄位標準化
- Trading Calendar
- Contract Calendar
- 1m Bar 建立
- Parquet 儲存
- DuckDB 查詢

### Domain Layer

定義：

- Instrument
- Contract
- Tick
- Bar
- Signal
- Position
- Trade

### Strategy Layer

負責：

- Feature
- Strategy
- Signal generation
- Strategy versioning

### Backtest Layer

核心元件：

- BacktestEngine
- ExecutionEngine
- CostCalculator
- PositionManager
- Portfolio
- Trade

### Analysis Layer

未來負責：

- Equity Curve
- Performance Metrics
- Trade Analysis
- Drawdown
- Sharpe
- Expectancy
- MAE / MFE
- R-Multiple
- Strategy comparison
- Walk-Forward
- OOS
- Monte Carlo

## 5. Design Principles

1. Data 與 Strategy 分離
2. Signal 與 Execution 分離
3. Requested Price 與 Actual Fill Price 分離
4. Portfolio accounting 與 Trade record 分離
5. Backtest 結果必須可重現
6. 所有核心功能必須有 regression tests
7. 不提前加入尚未驗證的複雜功能
8. Git history 不任意重寫

## 6. Current Backtest Model

目前採用 next-bar execution：

Signal at T
→ pending signal
→ execute at T+1 OPEN

Actual fill price 必須經過 ExecutionEngine / CostCalculator。

Slippage 反映於實際成交價，不應在 Trade PnL 再重複扣除。

## 7. Current Position Model

目前 BacktestEngine：

- 單一持倉
- Long / Short
- next-bar market execution
- SL / TP
- intrabar priority
- EOD exit
- signal exit
- Portfolio Risk Model
- Initial margin
- Maintenance margin
- Max contracts
- Margin utilization
- Entry risk check
- Forced liquidation

尚未支援：

- Multiple positions
- Partial exit
- REVERSE
- Live execution
