# Project Roadmap

## Phase 1 — Backtest Core

### P1-01 EMA + Signal
Status: COMPLETE

完成：

- EMA
- Signal model
- Signal generation

### P1-02 Strategy
Status: COMPLETE

完成：

- Strategy abstraction
- Strategy execution flow

### P1-03 Portfolio
Status: COMPLETE

完成：

- Portfolio module
- Initial capital
- Realized PnL
- Unrealized PnL
- Commission
- Equity
- Long / Short accounting

### P1-04-A Backtest Foundation
Status: COMPLETE

### P1-04-B Execution / Position Integration
Status: COMPLETE

完成：

- ExecutionEngine
- CostCalculator
- PositionManager
- SL / TP
- Next-bar execution

### P1-04-C Portfolio Integration
Status: COMPLETE

完成：

- BacktestEngine integrated with Portfolio
- Actual fill price used for accounting
- Trade PnL and Portfolio PnL consistency

### P1-04-D Determinism / Regression
Status: COMPLETE

完成：

- Same Engine repeated run
- Different Engine instances
- Trade field determinism
- Portfolio state determinism
- Input-change regression test

Current test count:

118 passed

---

# P1-05 Equity + Performance Metrics

Status: NEXT

Planned:

1. Equity curve
2. Drawdown
3. Peak equity
4. Maximum drawdown
5. Return
6. Win rate
7. Average win
8. Average loss
9. Profit factor
10. Expectancy
11. Sharpe ratio
12. Trade statistics

P1-05 must be based on existing Trade / Portfolio results and should not modify the established execution semantics.

---

# P1-06 Integration

Planned:

- End-to-end data → strategy → backtest flow
- Integration tests
- Representative dataset

# P1-07 Regression

Planned:

- Full regression suite
- Edge cases
- Deterministic baseline
- Performance regression

---

# Later Phases

## Research

- Strategy comparison
- Parameter analysis
- Market regime analysis
- MAE / MFE analysis
- R-multiple analysis

## Validation

- Walk-Forward
- Out-of-Sample
- Monte Carlo
- Parameter stability

## Production

- Real-time data
- Order management
- Broker integration
- Position synchronization
- Risk management
- Live monitoring

Production/live trading must not be implemented before the research and backtest layers are sufficiently validated.
