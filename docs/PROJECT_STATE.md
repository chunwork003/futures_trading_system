# Project State

## Current Phase

P12 Trading Core

Current development status:

- GAP-03 Execution Lifecycle: Completed
- G-5 Multi-Strategy Decision Architecture: Completed
- GAP-06 Position Sizing / Capital Allocation: Completed
- GAP-07 Contract / Futures Specification: Pending

## Current Commit

b0465407c4fe72cd46a186e4bdd21c13393b8145

Commit:

feat(risk): add position sizing comparison

HEAD and origin/master are synchronized.

## Test Status

GAP-06 targeted regression:

96 passed

Full regression:

611 passed

## Completed Major Development

### P1 Backtest Foundation

Completed capabilities include:

- Signal domain
- Strategy execution
- Portfolio accounting
- Backtest foundation
- Execution / Position integration
- Portfolio integration
- Deterministic regression coverage
- Next-bar execution
- Actual fill price accounting
- Commission
- Slippage
- LONG / SHORT
- Stop loss
- Take profit
- Intrabar priority
- Signal exit
- End-of-data exit
- Realized PnL
- Unrealized PnL
- Equity curve
- Drawdown
- Trade statistics

Return and Sharpe finalization remain deferred until after P12.

### P10 Multi-Strategy Backtest

Completed:

- Strategy Registry
- MultiStrategyRunner
- MultiStrategyBacktestRunner
- Multi-strategy backtest integration
- Actual TXF 1m regression coverage

### P11 Portfolio Risk

Completed:

- RiskConfig
- RiskState
- PortfolioRiskManager
- Initial margin
- Maintenance margin
- Maximum contracts
- Maximum margin utilization
- Available capital
- Position exposure
- Entry risk rejection
- Forced liquidation
- Multi-strategy risk integration

### P12-01 Broker Domain

Completed:

- Broker abstraction
- OrderSubmission
- submit_order
- get_order
- get_fills
- cancel_order
- SUBMITTED order status
- PARTIALLY_FILLED order status

### P12-02 Paper Trading Core

Completed trading flow:

Signal
-> Order
-> Broker
-> Fill
-> PositionManager
-> Portfolio
-> Risk

Supports asynchronous order lifecycle integration.

### P12-03 Market Data / Polling

Completed:

- MarketDataProvider
- Canonical MarketBar
- PaperMarketDataProvider
- PaperTradingRunner
- PollingConfig
- PollingLoop
- PollingResult

Canonical MarketBar currently includes:

- timestamp
- trade_date
- symbol
- OHLC
- volume
- amount
- tick_count
- timeframe
- exchange
- contract
- session
- source
- extension data

### P12-04 Shioaji Broker Adapter

Completed:

- Shioaji broker adapter
- Contract resolution
- Core / Shioaji enum mapping
- Order submission
- Order status synchronization
- Fill conversion
- Fill deduplication using Shioaji deal sequence
- Cancellation
- Async fill retrieval
- Fill price synchronization

Current Shioaji version used during implementation:

1.7.6

## GAP-03 Execution Lifecycle

Status: Completed.

Completed:

- A Pending Order Sync
- B1 Shioaji Fill Deduplication
- B2 Partial Fill Accumulation
- C Terminal Order Handling
- D Async Exit
- E PaperRunner Integration
- F Full Lifecycle Integration
- G-1 SHORT Basic Lifecycle
- G-2 SHORT Partial Entry
- G-3 SHORT Partial Exit
- G-4 SHORT Stop Loss / Take Profit

Paper trading supports:

- Pending entry
- Partial entry
- Multiple fills
- Pending exit
- Partial exit
- Terminal cancellation
- Terminal rejection
- LONG lifecycle
- SHORT lifecycle
- SHORT SL / TP

## G-5 Multi-Strategy Decision Architecture

Status: Completed.

Architecture:

Strategy Position
!=
Target Account Position
!=
Account Position
!=
Broker Position

Strategies maintain logically independent positions.

The Multi-Strategy Decision Layer determines the physical account target.

Completed:

1. Strategy Virtual Position Model
2. Multi-Strategy Decision Layer
3. HOLD / ADD / REDUCE / EXIT / ENTER
4. Strategy Conflict Resolution
5. Target Account Position
6. Strategy Attribution
7. Netting / Order Aggregation
8. Global Risk Constraint
9. Direction Change Lifecycle

Direction changes use:

EXIT
-> confirm FLAT
-> re-evaluate strategies
-> determine new target
-> ENTER

Direct LONG -> SHORT or SHORT -> LONG reversal is not the intended lifecycle.

## GAP-06 Position Sizing / Capital Allocation

Status: Completed.

### Position Sizing Domain

Completed:

- PositionSizingInput
- PositionSizingStrategy interface
- FixedQuantitySizing
- FixedAmountSizing
- FixedRiskSizing
- StopBasedRiskSizing
- PerContractRiskSizing

### Capital Position Management

Completed:

- CapitalReferenceMethod
- CapitalReferenceStrategy
- MovingPeakCapitalReference
- MovingAverageCapitalReference
- PreviousPeriodCapitalReference
- CapitalProtectionReference
- Capital drawdown calculation
- FixedRatioRiskLevel
- FixedRatioRiskThresholds
- FixedRatioRiskMultipliers
- FixedRatioParameters
- FixedRatioCapitalPositionInput
- FixedRatioCapitalPositionStrategy

### Registries

Completed:

- PositionSizingRegistry
- Default PositionSizingRegistry
- CapitalPositionManagementRegistry
- Default CapitalPositionManagementRegistry

### Backtest Integration

Completed:

- BacktestSizingAdapter
- Signal position sizing
- PositionSizingInput builder
- BacktestConfig risk_budget
- Optional PositionSizingStrategy integration in BacktestEngine
- Zero sizing result prevents entry
- Existing engine behavior preserved when no sizing strategy is supplied

### Sizing Comparison

Completed:

- SizingComparisonResult
- SizingComparisonRunner
- Same-market multi-sizing execution
- Different sizing quantity comparison
- Net PnL comparison
- Final equity comparison
- Maximum drawdown output

Validated comparison example:

- Fixed Quantity: 1 contract
- Fixed Risk: 5 contracts
- Position sizing differences correctly produce different PnL and final equity

GAP-06 targeted regression:

96 passed

Full project regression:

611 passed

## Known Technical Follow-ups

These are recorded but intentionally not mixed into GAP-06 completion.

### Position Sizing Input Builder

Current builder requires signal.stop_price for every sizing strategy.

Fixed Quantity and Fixed Amount conceptually do not require stop distance.

This should be refined separately if necessary.

### Capital Strategy Interface

FixedRatioCapitalPositionStrategy and PositionSizingStrategy currently represent separate sizing / capital-management abstractions.

Their long-term integration boundary should be reviewed separately instead of being changed during GAP-06 completion.

### Previous Period Capital Reference

The current "days" behavior represents previous N equity observations rather than calendar-day sampling.

Calendar-period semantics should be reviewed if required later.

## Remaining P12 Development Order

Development order is fixed as follows:

1. GAP-07 Contract / Futures Specification
2. Broker Account / Position Sync
3. GAP-08 Trading State Persistence & Recovery
4. GAP-09 Incremental Feature / Market State Engine
5. P12 Full Integration Validation

## GAP-07 Contract / Futures Specification

Status: Pending.

Purpose:

Centralize futures contract information currently distributed across configuration and broker layers.

Expected domain includes:

- Symbol
- Contract
- Exchange
- Multiplier
- Tick size
- Tick value
- Initial margin
- Maintenance margin
- Trading session metadata
- Contract-specific execution metadata

Exact model should be designed only after GAP-07 pre-check.

## Broker Account / Position Sync

Status: Pending.

Required before real broker operation.

Expected responsibilities:

- Broker account synchronization
- Broker position synchronization
- Core AccountPosition reconciliation
- Startup consistency check
- Broker / local position mismatch detection

## GAP-08 Trading State Persistence & Recovery

Status: Pending.

Existing database and storage infrastructure primarily stores market / backtest data.

Trading-state persistence remains separate work.

Expected responsibilities:

- Order persistence
- Fill persistence
- Position persistence
- Account / Equity persistence
- Trading event persistence
- Restart recovery
- Broker reconciliation after restart

## GAP-09 Incremental Feature / Market State Engine

Status: Pending.

Historical strategies currently can calculate features from full historical data.

Paper / live trading receives market bars incrementally.

Future engine should maintain required market state and calculate strategy features incrementally before strategy evaluation.

## Performance / Analysis Finalization

Status: Deferred until after P12.

Remaining:

- Return
- Sharpe Ratio
- Full Analysis / Performance validation
- Position sizing performance comparison using final metrics

## Repository Rules

- Use master as the primary branch.
- Do not rewrite Git history.
- Do not amend historical commits.
- Do not force push.
- Keep tests green.
- Develop one independent feature at a time.
- Pre-check before modification.
- Run targeted regression after modification.
- Run full regression before completion.
- Commit and push only after tests pass.
- Do not mix unrelated GAP items.
- Keep GAP ordering synchronized after every completed stage.
- Do not stage or modify data/ unless explicitly required.
