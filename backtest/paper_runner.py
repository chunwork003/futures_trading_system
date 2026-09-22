from __future__ import annotations

from dataclasses import dataclass

from backtest.market_data import MarketDataProvider
from backtest.models import Order, Position, Signal, SignalAction
from backtest.order_factory import OrderFactory
from backtest.paper_trading import PaperTradingEngine
from strategies.base import Strategy


@dataclass
class PaperRunnerResult:
    signals: list[Signal]
    orders: list[Order]
    positions: list[Position]
    realized_pnl: list[float]


class PaperTradingRunner:
    def __init__(
        self,
        market_data: MarketDataProvider,
        strategy: Strategy,
        trading_engine: PaperTradingEngine,
    ) -> None:
        self.market_data = market_data
        self.strategy = strategy
        self.trading_engine = trading_engine

    def process_latest(self) -> PaperRunnerResult:
        row = self.market_data.get_next()
        signals = self.strategy.on_bar(row)

        orders: list[Order] = []
        positions: list[Position] = []
        realized_pnl: list[float] = []

        for signal in signals:
            if signal.action == SignalAction.ENTER:
                order = OrderFactory.create_entry_order(
                    signal=signal,
                    timestamp=row["timestamp"],
                    requested_price=row["close"],
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
                    timestamp=row["timestamp"],
                    requested_price=row["close"],
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
