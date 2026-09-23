from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backtest.market_data_models import MarketBar
from backtest.models import Direction, Order, Signal, SignalAction
from backtest.order_factory import OrderFactory
from backtest.polling import PollingConfig
from backtest.polling_loop import PollingLoop
from backtest.polling_result import PollingResult
from backtest.paper_trading import PaperTradingEngine


@dataclass
class PaperRunnerResult:
    signals: list[Signal]
    orders: list[Order]
    positions: list[Any]
    realized_pnl: list[float]


class PaperTradingRunner:
    def __init__(
        self,
        market_data: Any,
        strategy: Any,
        trading_engine: PaperTradingEngine,
    ) -> None:
        self.market_data = market_data
        self.strategy = strategy
        self.trading_engine = trading_engine

    def process_latest(self) -> PaperRunnerResult:
        for order_id in list(self.trading_engine.pending_orders):
            self.trading_engine.sync_pending_order(order_id)

        row: MarketBar = self.market_data.get_next()

        bar = {
            "timestamp": row.timestamp,
            "trade_date": row.trade_date,
            "symbol": row.symbol,
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume,
            "amount": row.amount,
            "tick_count": row.tick_count,
            "timeframe": row.timeframe,
            "exchange": row.exchange,
            "contract": row.contract,
            "session": row.session,
            "source": row.source,
            **row.data,
        }

        orders: list[Order] = []
        positions: list[Any] = []
        realized_pnl: list[float] = []

        exit_reason, exit_price = (
            self.trading_engine.position_manager.update_bar(
                timestamp=row.timestamp,
                open_price=row.open,
                high_price=row.high,
                low_price=row.low,
                close_price=row.close,
            )
        )

        if (
            exit_reason is not None
            and exit_price is not None
            and self.trading_engine.position_manager.current_position
            is not None
        ):
            position = (
                self.trading_engine.position_manager.current_position
            )

            exit_signal = Signal(
                signal_id=f"EXIT-{position.signal_id}-{row.timestamp.isoformat()}",
                timestamp=row.timestamp,
                trade_date=row.trade_date,
                strategy_id=position.strategy_id,
                strategy_version=position.strategy_version,
                symbol=position.symbol,
                contract=position.contract,
                timeframe=row.timeframe or "1m",
                action=SignalAction.EXIT,
                direction=position.direction,
                quantity=position.quantity,
                entry_type=position.entry_type,
                entry_price=position.entry_price,
                stop_price=position.stop_price,
                target_price=position.target_price,
                market_state=position.market_state,
                setup=position.setup,
            )

            order = OrderFactory.create_exit_order(
                signal=exit_signal,
                timestamp=row.timestamp,
                requested_price=exit_price,
                quantity=position.quantity,
            )

            pnl = self.trading_engine.close_position(order)
            orders.append(order)
            if pnl is not None:
                realized_pnl = [pnl]
            else:
                realized_pnl = []

        else:
            realized_pnl = []

        signals = self.strategy.on_bar(bar)

        for signal in signals:
            if signal.action == SignalAction.ENTER:
                order = OrderFactory.create_entry_order(
                    signal=signal,
                    timestamp=row.timestamp,
                    requested_price=row.close,
                )
                position = self.trading_engine.open_position(
                    signal=signal,
                    order=order,
                )
                orders.append(order)
                positions.append(position)

            elif signal.action == SignalAction.EXIT:
                position = self.trading_engine.position_manager.current_position
                if position is None:
                    continue

                order = OrderFactory.create_exit_order(
                    signal=signal,
                    timestamp=row.timestamp,
                    requested_price=row.close,
                    quantity=position.quantity,
                )
                pnl = self.trading_engine.close_position(order)
                orders.append(order)
                realized_pnl.append(pnl)

        return PaperRunnerResult(
            signals=signals,
            orders=orders,
            positions=positions,
            realized_pnl=realized_pnl,
        )

    def run(
        self,
        config: PollingConfig | None = None,
        max_iterations: int | None = None,
    ) -> PollingResult:
        loop = PollingLoop(
            callback=self.process_latest,
            config=config,
        )
        return loop.run(max_iterations=max_iterations)
