from __future__ import annotations

from typing import Iterable

from backtest.cost import CostCalculator, CostConfig
from backtest.execution import ExecutionEngine
from backtest.models import (
    BacktestConfig,
    Direction,
    ExitReason,
    Order,
    OrderStatus,
    OrderType,
    Signal,
    SignalAction,
    Trade,
)
from backtest.position import PositionManager


class BacktestEngine:
    def __init__(
        self,
        config: BacktestConfig,
    ):
        self.config = config

        self.cost_calculator = CostCalculator(
            CostConfig(
                commission_per_contract=config.commission_per_contract,
                slippage_points=config.slippage_points,
            )
        )

        self.execution = ExecutionEngine(
            self.cost_calculator
        )

        self.position_manager = PositionManager(
            intrabar_priority=config.intrabar_priority
        )

        self.trades: list[Trade] = []
        self.pending_entry_signal: Signal | None = None
        self.pending_exit_signal: Signal | None = None

    def run(
        self,
        bars: Iterable[dict],
        signals: Iterable[Signal],
    ) -> list[Trade]:

        bars_list = list(bars)
        signals_list = list(signals)

        if not bars_list:
            return []

        signal_map = {
            signal.timestamp: signal
            for signal in signals_list
        }

        self.trades = []
        self.pending_entry_signal = None
        self.pending_exit_signal = None
        self.position_manager.close_position()

        for row in bars_list:

            timestamp = row["timestamp"]

            # -------------------------------------------------
            # 1. Execute pending EXIT at current bar OPEN
            # -------------------------------------------------
            if self.pending_exit_signal is not None:

                if not self.position_manager.is_flat:

                    self._close_trade(
                        row=row,
                        exit_reason=ExitReason.SIGNAL,
                        exit_price=row["open"],
                    )

                self.pending_exit_signal = None

            # -------------------------------------------------
            # 2. Execute pending ENTRY at current bar OPEN
            # -------------------------------------------------
            if (
                self.pending_entry_signal is not None
                and self.position_manager.is_flat
            ):

                self._open_trade(
                    signal=self.pending_entry_signal,
                    row=row,
                )

                self.pending_entry_signal = None

            # -------------------------------------------------
            # 3. Check existing position against current bar
            # -------------------------------------------------
            if not self.position_manager.is_flat:

                exit_reason, exit_price = (
                    self.position_manager.update_bar(
                        timestamp=timestamp,
                        open_price=row["open"],
                        high_price=row["high"],
                        low_price=row["low"],
                        close_price=row["close"],
                    )
                )

                if (
                    exit_reason is not None
                    and exit_price is not None
                ):
                    self._close_trade(
                        row=row,
                        exit_reason=exit_reason,
                        exit_price=exit_price,
                    )

            # -------------------------------------------------
            # 4. Generate signal for NEXT BAR
            # -------------------------------------------------
            if timestamp not in signal_map:
                continue

            signal = signal_map[timestamp]

            if signal.symbol != self.config.symbol:
                continue

            # -------------------------------------------------
            # 4A. EXIT signal
            # -------------------------------------------------
            if signal.action == SignalAction.EXIT:

                if not self.position_manager.is_flat:

                    self.pending_exit_signal = signal

                continue

            # -------------------------------------------------
            # 4B. ENTER signal
            # -------------------------------------------------
            if signal.action == SignalAction.ENTER:

                if (
                    self.position_manager.is_flat
                    and self.pending_entry_signal is None
                    and self.pending_exit_signal is None
                ):
                    self.pending_entry_signal = signal

                continue

            # -------------------------------------------------
            # 4C. REVERSE
            # -------------------------------------------------
            if signal.action == SignalAction.REVERSE:

                # REVERSE will be implemented explicitly
                # in a later engine phase.
                continue

        # -----------------------------------------------------
        # 5. End-of-data exit
        # -----------------------------------------------------
        if (
            self.config.end_of_data_exit
            and not self.position_manager.is_flat
        ):
            last_row = bars_list[-1]

            self._close_trade(
                row=last_row,
                exit_reason=ExitReason.END_OF_DATA,
                exit_price=last_row["close"],
            )

        return self.trades

    def _open_trade(
        self,
        signal: Signal,
        row: dict,
    ) -> None:

        entry_order = Order(
            order_id=(
                f"ENTRY-{signal.signal_id}"
            ),
            signal_id=signal.signal_id,
            timestamp=row["timestamp"],
            symbol=signal.symbol,
            contract=signal.contract,
            direction=signal.direction,
            order_type=OrderType.MARKET,
            quantity=signal.quantity,
            requested_price=row["open"],
            status=OrderStatus.PENDING,
        )

        entry_fill = self.execution.execute_market_order(
            order=entry_order,
            market_price=row["open"],
            is_entry=True,
        )

        self.position_manager.open_position(
            signal=signal,
            fill=entry_fill,
        )

    def _close_trade(
        self,
        row: dict,
        exit_reason: ExitReason,
        exit_price: float,
    ) -> None:

        position = (
            self.position_manager.current_position
        )

        if position is None:
            return

        exit_order = Order(
            order_id=(
                f"EXIT-{position.signal_id}-"
                f"{len(self.trades) + 1:06d}"
            ),
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

        # -----------------------------------------------------
        # PnL based on actual fill prices
        # -----------------------------------------------------
        if position.direction == Direction.LONG:
            pnl_points = (
                exit_fill.price
                - position.entry_price
            )
        else:
            pnl_points = (
                position.entry_price
                - exit_fill.price
            )

        gross_pnl = (
            pnl_points
            * position.quantity
            * self.config.multiplier
        )

        commission = (
            position.entry_commission
            + exit_fill.commission
        )

        slippage_cost = (
            (
                position.entry_slippage_points
                + exit_fill.slippage_points
            )
            * position.quantity
            * self.config.multiplier
        )

        # IMPORTANT:
        # Slippage is already reflected in actual fill prices.
        # Therefore do NOT subtract slippage_cost again.
        net_pnl = gross_pnl - commission

        # -----------------------------------------------------
        # Risk
        # -----------------------------------------------------
        risk_points = None

        if position.stop_price is not None:
            risk_points = abs(
                position.entry_price
                - position.stop_price
            )

        # -----------------------------------------------------
        # Realized R
        # -----------------------------------------------------
        r_multiple = None

        if (
            risk_points is not None
            and risk_points > 0
        ):
            r_multiple = (
                pnl_points
                / risk_points
            )

        # -----------------------------------------------------
        # MAE / MFE
        # -----------------------------------------------------
        mae_points = None
        mfe_points = None

        if position.direction == Direction.LONG:

            if position.lowest_price is not None:
                mae_points = (
                    position.lowest_price
                    - position.entry_price
                )

            if position.highest_price is not None:
                mfe_points = (
                    position.highest_price
                    - position.entry_price
                )

        elif position.direction == Direction.SHORT:

            if position.highest_price is not None:
                mae_points = (
                    position.entry_price
                    - position.highest_price
                )

            if position.lowest_price is not None:
                mfe_points = (
                    position.entry_price
                    - position.lowest_price
                )

        # -----------------------------------------------------
        # Holding time
        # -----------------------------------------------------
        holding_minutes = (
            row["timestamp"]
            - position.entry_time
        ).total_seconds() / 60

        # -----------------------------------------------------
        # Result
        # -----------------------------------------------------
        if net_pnl > 0:
            result = "WIN"
        elif net_pnl < 0:
            result = "LOSS"
        else:
            result = "BREAKEVEN"

        # -----------------------------------------------------
        # Trade record
        # -----------------------------------------------------
        trade = Trade(
            trade_id=(
                f"TRADE-{len(self.trades) + 1:06d}"
            ),
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
