# Project State

## Current Phase

P1-05

## Completed

- P1-01 EMA + Signal
- P1-02 Strategy
- P1-03 Portfolio
- P1-04-A Backtest foundation
- P1-04-B Execution / Position integration
- P1-04-C Portfolio integration
- P1-04-D Determinism / Regression tests

## Current Commit

8297008

Commit:

test(backtest): restore determinism regression coverage

## Test Status

Full test suite:

118 passed

Determinism test:

5 passed

## Backtest Engine

Current capabilities:

- Next-bar execution
- Actual fill price
- Commission
- Slippage
- Long / Short
- Stop loss
- Take profit
- Intrabar priority
- Signal exit
- End-of-data exit
- Portfolio accounting
- Realized PnL
- Unrealized PnL
- Equity
- Deterministic repeated execution
- Regression tests

## Current Execution Semantics

Signal generated at T:

-> pending signal

-> execute at T+1 OPEN

Actual fill price is used for accounting and Trade PnL.

Slippage is already reflected in actual fill price and must not be double-counted.

## Known Limitations

Not implemented:

- REVERSE
- Multiple positions
- Partial exits
- Live trading
- Broker integration
- Advanced margin / portfolio risk features
- Advanced cash management

These are intentionally deferred.

## Next Development Target

P1-05 Equity + Performance Metrics

Initial target:

1. Equity curve
2. Peak equity
3. Drawdown
4. Maximum drawdown
5. Return
6. Win rate
7. Average win
8. Average loss
9. Profit factor
10. Expectancy
11. Sharpe ratio
12. Trade statistics

P1-05 should consume existing Trade / Portfolio outputs and should not change current execution semantics.

## Repository Rules

- Do not rewrite Git history.
- Do not amend historical commits.
- Do not force push.
- Keep tests green.
- Make small, reviewable commits.

## P12 / GAP Development Tracking

### GAP-03 Execution Lifecycle

- A Pending Order Sync: Completed
- B1 Shioaji Fill Deduplication: Completed
- B2 Partial Fill Accumulation: Completed
- C Terminal Order Handling: Completed
- D Async Exit: Completed
- E PaperRunner Integration: Completed
- F Full Lifecycle Integration: Completed
- G-1 SHORT Basic Lifecycle: Completed
- G-2 SHORT Partial Entry: Completed
- G-3 SHORT Partial Exit: Completed
- G-4 SHORT Stop Loss / Take Profit: Completed

### G-5 Multi-Strategy Decision Architecture

Status: Design confirmed, implementation pending.

Architecture direction:

- Strategy positions are logically independent.
- Portfolio / Account position represents the physical account position.
- Broker position represents the actual broker-side position.
- Multi-Strategy Decision Layer determines the final account target position.
- Strategy signals must not directly determine the final account position.

Planned responsibilities:

1. Strategy Virtual Position Model
2. Multi-Strategy Decision Layer
3. HOLD / ADD / REDUCE / EXIT / ENTER
4. Strategy Conflict Resolution
5. Target Account Position
6. Strategy Attribution
7. Netting / Order Aggregation
8. Global Risk Constraint
9. Direction Change Lifecycle

Direction change rule:

EXIT
-> confirm FLAT
-> re-evaluate strategies
-> determine new target
-> ENTER

Direct LONG -> SHORT or SHORT -> LONG reversal is not the intended lifecycle.

### Later Development Order

After G-5 design / implementation:

1. GAP-06 Position Sizing / Capital Allocation
2. GAP-07 Contract / Futures Specification
3. Broker Account / Position Sync
4. GAP-08 Trading State Persistence & Recovery
5. GAP-09 Incremental Feature / Market State Engine
