<!-- AUTHORITATIVE-DOC-NOTICE -->

> **Documentation Status**
>
> 本文件是 Supplemental BacktestEngine Design Notes。
> 部分 Current Limitations 已被後續 implementation 取代。
>
> Current capability status：
>
> - `docs/V1_CAPABILITY_MAP.md`
>
> Current architecture：
>
> - `docs/ARCHITECTURE.md`
>
> 本文件保留 backtest semantics 說明，但不得作為整體系統 current-state authority。

---
# Backtest Engine

## Execution Model

BacktestEngine processes bars sequentially.

For each bar:

1. Execute pending EXIT at current OPEN.
2. Execute pending ENTRY at current OPEN.
3. Check the existing position against the current bar.
4. Generate the signal for the NEXT BAR.

At the end of the data:

5. Optional end-of-data exit.

## Signal Timing

A signal generated at timestamp T is not executed at the same bar.

Signal at T
-> pending signal
-> execution at T+1 OPEN

This prevents accidental same-bar look-ahead.

## Execution

Market orders are executed through:

- ExecutionEngine
- CostCalculator

Costs include:

- Commission
- Slippage

## Actual Fill Price

The actual fill price is authoritative for:

- Position entry and exit
- Portfolio accounting
- Trade PnL

Requested price and actual fill price must not be treated as identical.

## Slippage

Slippage is incorporated into the actual fill price.

Trade PnL must not subtract the same slippage a second time.

## PositionManager

PositionManager manages:

- Current position
- Long / Short
- Stop loss
- Take profit
- Intrabar processing
- SL / TP priority

Current default:

SL_FIRST

## Portfolio

Portfolio currently tracks:

- Initial capital
- Realized PnL
- Unrealized PnL
- Commission
- Equity
- Current position

The current Portfolio model supports one position at a time.

## Trade

Completed trades record:

- Entry
- Exit
- Direction
- Quantity
- Gross PnL
- Commission
- Net PnL
- Risk points
- PnL points
- R multiple
- MAE
- MFE
- Holding time
- Exit reason
- Result

## End-of-Data Exit

When enabled, an open position is closed at the final bar close.

Exit reason:

END_OF_DATA

## Determinism

BacktestEngine.run() resets:

- Trades
- Pending signals
- PositionManager
- Portfolio

Repeated execution with identical inputs must produce identical results.

This behavior is protected by regression tests.

## Current Limitations

Not implemented:

- REVERSE
- Multiple positions
- Partial exits
- Live trading
- Broker execution
- Advanced margin / portfolio risk features
- Advanced cash management
- Advanced slippage models

## Position Sizing Integration

BacktestEngine supports an optional PositionSizingStrategy.

Entry processing flow:

Signal ENTER
-> build PositionSizingInput
-> PositionSizingStrategy.calculate()
-> update Signal.quantity
-> PortfolioRiskManager.can_open()
-> pending entry
-> next-bar execution

PositionSizingInput currently contains:

- equity
- price
- stop_price
- multiplier
- risk_budget

If the calculated quantity is zero or less, the entry is skipped.

If no PositionSizingStrategy is supplied, the engine preserves the original signal quantity and existing execution behavior.

Supported sizing implementations currently include:

- FixedQuantitySizing
- FixedAmountSizing
- FixedRiskSizing
- StopBasedRiskSizing
- PerContractRiskSizing

SizingComparisonRunner can execute identical bars and signals through multiple sizing strategies and return:

- Total trades
- Net PnL
- Maximum drawdown
- Final equity

Return and Sharpe are intentionally deferred until the post-P12 performance-analysis stage.
