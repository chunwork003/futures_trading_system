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
