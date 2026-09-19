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
- Margin model
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
