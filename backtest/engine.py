from __future__ import annotations

from datetime import date
from typing import Iterable

from analysis.equity import EquityCurve
from backtest.cost import CostCalculator, CostConfig
from backtest.execution import ExecutionEngine
from backtest.order_factory import OrderFactory
from backtest.models import (
    BacktestConfig, Direction, ExitReason, Order, OrderStatus,
    OrderType, Signal, SignalAction, Trade,
)
from backtest.position import PositionManager
from backtest.position_sizing import PositionSizingStrategy
from backtest.position_sizing_input_builder import build_position_sizing_input
from backtest.portfolio import Portfolio
from backtest.risk import PortfolioRiskManager, RiskConfig
from backtest.specification_resolution import (
    BacktestSpecificationResolver,
    ResolvedMargins,
    ResolvedMultiplier,
    ResolvedParameterSource,
)
from domain.instruments import InstrumentSpec
from domain.margins import MarginScheduleResolver


class BacktestEngine:
    def __init__(
        self,
        config: BacktestConfig,
        position_sizing_strategy: PositionSizingStrategy | None = None,
        *,
        resolved_multiplier: ResolvedMultiplier | None = None,
        resolved_margins: ResolvedMargins | None = None,
    ):
        runtime_updates: dict[str, object] = {}
        if resolved_multiplier is None:
            self.resolved_multiplier = ResolvedMultiplier(
                value=float(config.multiplier),
                source=ResolvedParameterSource.LEGACY_CONFIG,
            )
        else:
            self.resolved_multiplier = resolved_multiplier
            runtime_updates["multiplier"] = resolved_multiplier.value

        legacy_risk_config = config.risk_config or RiskConfig()
        if resolved_margins is None:
            self.resolved_margins = ResolvedMargins(
                initial_margin_per_contract=(
                    legacy_risk_config.initial_margin_per_contract
                ),
                maintenance_margin_per_contract=(
                    legacy_risk_config.maintenance_margin_per_contract
                ),
                source=ResolvedParameterSource.LEGACY_CONFIG,
            )
        else:
            self.resolved_margins = resolved_margins
            runtime_updates["risk_config"] = RiskConfig(
                initial_margin_per_contract=(
                    resolved_margins.initial_margin_per_contract
                ),
                maintenance_margin_per_contract=(
                    resolved_margins.maintenance_margin_per_contract
                ),
                max_contracts=legacy_risk_config.max_contracts,
                max_margin_utilization=(
                    legacy_risk_config.max_margin_utilization
                ),
            )

        self.config = (
            config.model_copy(update=runtime_updates)
            if runtime_updates
            else config
        )
        self.position_sizing_strategy = position_sizing_strategy
        self.cost_calculator = CostCalculator(
            CostConfig(
                commission_per_contract=self.config.commission_per_contract,
                slippage_points=self.config.slippage_points,
            )
        )
        self.execution = ExecutionEngine(self.cost_calculator)
        self.position_manager = PositionManager(
            intrabar_priority=self.config.intrabar_priority
        )
        self.portfolio = Portfolio(
            initial_capital=self.config.initial_capital,
            multiplier=self.config.multiplier,
        )
        self.risk_manager = PortfolioRiskManager(
            self.config.risk_config or RiskConfig()
        )
        self.equity_curve = EquityCurve()
        self.trades: list[Trade] = []
        self.pending_entry_signal: Signal | None = None
        self.pending_exit_signal: Signal | None = None

    @classmethod
    def from_instrument_spec(
        cls,
        config: BacktestConfig,
        instrument_spec: InstrumentSpec,
        position_sizing_strategy: PositionSizingStrategy | None = None,
        *,
        multiplier_override: float | None = None,
    ) -> "BacktestEngine":
        """由 explicit override 或 canonical spec 建立單一 run-time multiplier。"""
        resolved_multiplier = BacktestSpecificationResolver.resolve_multiplier(
            explicit_override=multiplier_override,
            instrument_spec=instrument_spec,
        )
        return cls(
            config=config,
            position_sizing_strategy=position_sizing_strategy,
            resolved_multiplier=resolved_multiplier,
        )

    @classmethod
    def from_specifications(
        cls,
        config: BacktestConfig,
        instrument_spec: InstrumentSpec,
        *,
        as_of_date: date,
        margin_resolver: MarginScheduleResolver | None = None,
        contract_id: int | None = None,
        multiplier_override: float | None = None,
        no_margin_mode: bool = False,
        position_sizing_strategy: PositionSizingStrategy | None = None,
    ) -> "BacktestEngine":
        """以明確日期解析 canonical multiplier 與 margin，建立 deterministic runtime。"""
        resolved_multiplier = BacktestSpecificationResolver.resolve_multiplier(
            explicit_override=multiplier_override,
            instrument_spec=instrument_spec,
        )
        resolved_margins = BacktestSpecificationResolver.resolve_margins(
            explicit_override=config.risk_config,
            margin_resolver=margin_resolver,
            instrument_id=instrument_spec.instrument_id,
            contract_id=contract_id,
            as_of_date=as_of_date,
            no_margin_mode=no_margin_mode,
        )
        return cls(
            config=config,
            position_sizing_strategy=position_sizing_strategy,
            resolved_multiplier=resolved_multiplier,
            resolved_margins=resolved_margins,
        )

    def run(self, bars: Iterable[dict], signals: Iterable[Signal]) -> list[Trade]:
        bars_list = list(bars)
        signals_list = list(signals)
        if not bars_list:
            return []
        signal_map = {signal.timestamp: signal for signal in signals_list}
        self.trades = []
        self.pending_entry_signal = None
        self.pending_exit_signal = None
        self.equity_curve.reset()
        self.position_manager.close_position()
        self.portfolio.reset()
        for row in bars_list:
            timestamp = row["timestamp"]
            if self.pending_exit_signal is not None:
                if not self.position_manager.is_flat:
                    self._close_trade(row=row, exit_reason=ExitReason.SIGNAL, exit_price=row["open"])
                self.pending_exit_signal = None
            if self.pending_entry_signal is not None and self.position_manager.is_flat:
                self._open_trade(signal=self.pending_entry_signal, row=row)
                self.pending_entry_signal = None
            if not self.position_manager.is_flat:
                exit_reason, exit_price = self.position_manager.update_bar(
                    timestamp=timestamp,
                    open_price=row["open"],
                    high_price=row["high"],
                    low_price=row["low"],
                    close_price=row["close"],
                )
                if exit_reason is not None and exit_price is not None:
                    self._close_trade(row=row, exit_reason=exit_reason, exit_price=exit_price)
                else:
                    self.portfolio.mark_to_market(row["close"])
                    if self.risk_manager.should_force_liquidate(
                        equity=self.portfolio.equity,
                        quantity=self.position_manager.current_position.quantity,
                    ):
                        self._close_trade(
                            row=row,
                            exit_reason=ExitReason.FORCED_LIQUIDATION,
                            exit_price=row["close"],
                        )
            self.equity_curve.add_snapshot(
                timestamp=timestamp,
                equity=self.portfolio.equity,
                realized_pnl=self.portfolio.realized_pnl,
                unrealized_pnl=self.portfolio.unrealized_pnl,
            )
            if timestamp not in signal_map:
                continue
            signal = signal_map[timestamp]
            if signal.symbol != self.config.symbol:
                continue
            if signal.action == SignalAction.EXIT:
                if not self.position_manager.is_flat:
                    self.pending_exit_signal = signal
                continue
            if signal.action == SignalAction.ENTER:
                if (
                    self.position_manager.is_flat
                    and self.pending_entry_signal is None
                    and self.pending_exit_signal is None
                ):
                    if self.position_sizing_strategy is not None:
                        sizing_input = build_position_sizing_input(
                            config=self.config,
                            signal=signal,
                            equity=self.portfolio.equity,
                        )

                        quantity = self.position_sizing_strategy.calculate(
                            sizing_input
                        )

                        if quantity <= 0:
                            continue

                        signal = signal.model_copy(
                            update={"quantity": quantity}
                        )

                    self.pending_entry_signal = signal
                continue
            if signal.action == SignalAction.REVERSE:
                continue
        if self.config.end_of_data_exit and not self.position_manager.is_flat:
            last_row = bars_list[-1]
            self._close_trade(
                row=last_row,
                exit_reason=ExitReason.END_OF_DATA,
                exit_price=last_row["close"],
            )
        if self.equity_curve.snapshots:
            self.equity_curve.snapshots.pop()
            last_row = bars_list[-1]
            self.equity_curve.add_snapshot(
                timestamp=last_row["timestamp"],
                equity=self.portfolio.equity,
                realized_pnl=self.portfolio.realized_pnl,
                unrealized_pnl=self.portfolio.unrealized_pnl,
            )
        return self.trades

    def _open_trade(self, signal: Signal, row: dict) -> None:
        if not self.risk_manager.can_open(
            equity=self.portfolio.equity,
            quantity=signal.quantity,
        ):
            return

        entry_order = OrderFactory.create_entry_order(
            signal=signal,
            timestamp=row["timestamp"],
            requested_price=row["open"],
        )
        entry_fill = self.execution.execute_market_order(
            order=entry_order,
            market_price=row["open"],
            is_entry=True,
        )
        self.position_manager.open_position(signal=signal, fill=entry_fill)
        self.portfolio.open_position(
            direction=signal.direction.value,
            entry_price=entry_fill.price,
            quantity=entry_fill.quantity,
            commission=entry_fill.commission,
        )

    def _close_trade(self, row: dict, exit_reason: ExitReason, exit_price: float) -> None:
        position = self.position_manager.current_position
        if position is None:
            return
        exit_order = Order(
            order_id=f"EXIT-{position.signal_id}-{len(self.trades) + 1:06d}",
            signal_id=position.signal_id,
            timestamp=row["timestamp"],
            symbol=position.symbol,
            contract=position.contract,
            direction=position.direction,
            order_type=OrderType.MARKET,
            quantity=position.quantity,
            requested_price=exit_price,
            status=OrderStatus.PENDING,
        )
        exit_fill = self.execution.execute_market_order(
            order=exit_order,
            market_price=exit_price,
            is_entry=False,
        )
        self.portfolio.close_position(
            exit_price=exit_fill.price,
            commission=exit_fill.commission,
        )
        if position.direction == Direction.LONG:
            pnl_points = exit_fill.price - position.entry_price
        else:
            pnl_points = position.entry_price - exit_fill.price
        gross_pnl = pnl_points * position.quantity * self.config.multiplier
        commission = position.entry_commission + exit_fill.commission
        slippage_cost = (
            (position.entry_slippage_points + exit_fill.slippage_points)
            * position.quantity
            * self.config.multiplier
        )
        net_pnl = gross_pnl - commission
        risk_points = None
        if position.stop_price is not None:
            risk_points = abs(position.entry_price - position.stop_price)
        r_multiple = None
        if risk_points is not None and risk_points > 0:
            r_multiple = pnl_points / risk_points
        mae_points = None
        mfe_points = None
        if position.direction == Direction.LONG:
            if position.lowest_price is not None:
                mae_points = position.lowest_price - position.entry_price
            if position.highest_price is not None:
                mfe_points = position.highest_price - position.entry_price
        elif position.direction == Direction.SHORT:
            if position.highest_price is not None:
                mae_points = position.entry_price - position.highest_price
            if position.lowest_price is not None:
                mfe_points = position.entry_price - position.lowest_price
        holding_minutes = (
            row["timestamp"] - position.entry_time
        ).total_seconds() / 60
        if net_pnl > 0:
            result = "WIN"
        elif net_pnl < 0:
            result = "LOSS"
        else:
            result = "BREAKEVEN"
        trade = Trade(
            trade_id=f"TRADE-{len(self.trades) + 1:06d}",
            signal_id=position.signal_id,
            trade_date=row["trade_date"],
            symbol=position.symbol,
            contract=position.contract,
            timeframe=self.config.timeframe,
            strategy_id=position.strategy_id,
            strategy_version=position.strategy_version,
            market_state=position.market_state,
            setup=position.setup,
            entry_type=position.entry_type,
            direction=position.direction,
            entry_time=position.entry_time,
            exit_time=row["timestamp"],
            entry_price=position.entry_price,
            exit_price=exit_fill.price,
            stop_price=position.stop_price,
            target_price=position.target_price,
            quantity=position.quantity,
            gross_pnl=gross_pnl,
            commission=commission,
            slippage_cost=slippage_cost,
            net_pnl=net_pnl,
            risk_points=risk_points,
            pnl_points=pnl_points,
            r_multiple=r_multiple,
            mae_points=mae_points,
            mfe_points=mfe_points,
            holding_minutes=holding_minutes,
            exit_reason=exit_reason,
            result=result,
        )
        self.trades.append(trade)
        self.position_manager.close_position()
