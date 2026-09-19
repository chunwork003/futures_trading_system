from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from backtest.models import Trade


@dataclass(frozen=True)
class EquityPoint:
    trade_id: str
    exit_time: object
    net_pnl: float
    equity: float
    peak_equity: float
    drawdown: float
    drawdown_pct: float


@dataclass(frozen=True)
class DistributionStats:
    count: int
    average: float | None
    median: float | None
    minimum: float | None
    maximum: float | None


@dataclass(frozen=True)
class RDistribution:
    count: int
    average_r: float | None
    median_r: float | None
    min_r: float | None
    max_r: float | None

    positive_r_count: int
    negative_r_count: int
    zero_r_count: int

    r_1_or_more_count: int
    r_2_or_more_count: int
    r_3_or_more_count: int

    minus_1_or_less_count: int


@dataclass(frozen=True)
class MetricGroup:
    dimension: str
    value: str
    metrics: "BacktestMetrics"


@dataclass(frozen=True)
class MultiMetricGroup:
    dimensions: dict[str, str]
    metrics: "BacktestMetrics"
    sample_count: int
    sample_status: str


@dataclass(frozen=True)
class BacktestMetrics:
    trade_count: int
    win_count: int
    loss_count: int
    breakeven_count: int

    win_rate: float

    gross_profit: float
    gross_loss: float
    net_pnl: float

    average_win: float
    average_loss: float

    profit_factor: float | None
    expectancy: float

    max_drawdown: float
    max_drawdown_pct: float

    max_consecutive_losses: int

    average_r: float | None
    average_mae: float | None
    average_mfe: float | None
    average_holding_minutes: float | None

    r_distribution: RDistribution
    mae_distribution: DistributionStats
    mfe_distribution: DistributionStats


class MetricsCalculator:

    GROUPABLE_FIELDS = {
        "strategy_id",
        "strategy_version",
        "market_state",
        "setup",
        "entry_type",
        "direction",
        "exit_reason",
        "symbol",
    }

    def calculate_grouped(
        self,
        trades: Iterable[Trade],
        initial_capital: float,
        dimension: str,
    ) -> list[MetricGroup]:

        if dimension not in self.GROUPABLE_FIELDS:
            raise ValueError(
                f"Unsupported grouping dimension: {dimension}"
            )

        trade_list = list(trades)

        groups: dict[str, list[Trade]] = {}

        for trade in trade_list:
            value = getattr(trade, dimension)

            if value is None:
                value = "UNKNOWN"
            else:
                value = str(value)

            groups.setdefault(value, []).append(trade)

        result: list[MetricGroup] = []

        for value in sorted(groups):
            group_trades = groups[value]

            metrics = self.calculate(
                trades=group_trades,
                initial_capital=initial_capital,
            )

            result.append(
                MetricGroup(
                    dimension=dimension,
                    value=value,
                    metrics=metrics,
                )
            )

        return result

    def calculate_multi_grouped(
        self,
        trades: Iterable[Trade],
        initial_capital: float,
        dimensions: list[str],
        minimum_samples: int = 30,
    ) -> list[MultiMetricGroup]:

        if not dimensions:
            raise ValueError(
                "dimensions must not be empty"
            )

        if minimum_samples <= 0:
            raise ValueError(
                "minimum_samples must be > 0"
            )

        invalid_dimensions = [
            dimension
            for dimension in dimensions
            if dimension not in self.GROUPABLE_FIELDS
        ]

        if invalid_dimensions:
            raise ValueError(
                "Unsupported grouping dimensions: "
                + ", ".join(invalid_dimensions)
            )

        if len(set(dimensions)) != len(dimensions):
            raise ValueError(
                "dimensions must not contain duplicates"
            )

        trade_list = list(trades)

        groups: dict[tuple[str, ...], list[Trade]] = {}

        for trade in trade_list:
            key_values: list[str] = []

            for dimension in dimensions:
                value = getattr(trade, dimension)

                if value is None:
                    value = "UNKNOWN"
                else:
                    value = str(value)

                key_values.append(value)

            key = tuple(key_values)

            groups.setdefault(
                key,
                [],
            ).append(trade)

        result: list[MultiMetricGroup] = []

        for key in sorted(groups):
            group_trades = groups[key]

            sample_count = len(group_trades)

            if sample_count >= minimum_samples:
                sample_status = "SUFFICIENT"
            else:
                sample_status = "LOW_SAMPLE"

            group_dimensions = {
                dimension: value
                for dimension, value
                in zip(dimensions, key)
            }

            metrics = self.calculate(
                trades=group_trades,
                initial_capital=initial_capital,
            )

            result.append(
                MultiMetricGroup(
                    dimensions=group_dimensions,
                    metrics=metrics,
                    sample_count=sample_count,
                    sample_status=sample_status,
                )
            )

        return result

    def calculate(
        self,
        trades: Iterable[Trade],
        initial_capital: float,
    ) -> BacktestMetrics:

        if initial_capital <= 0:
            raise ValueError(
                "initial_capital must be > 0"
            )

        trade_list = sorted(
            list(trades),
            key=lambda trade: trade.exit_time,
        )

        if not trade_list:
            empty_r_distribution = RDistribution(
                count=0,
                average_r=None,
                median_r=None,
                min_r=None,
                max_r=None,
                positive_r_count=0,
                negative_r_count=0,
                zero_r_count=0,
                r_1_or_more_count=0,
                r_2_or_more_count=0,
                r_3_or_more_count=0,
                minus_1_or_less_count=0,
            )

            return BacktestMetrics(
                trade_count=0,
                win_count=0,
                loss_count=0,
                breakeven_count=0,
                win_rate=0.0,
                gross_profit=0.0,
                gross_loss=0.0,
                net_pnl=0.0,
                average_win=0.0,
                average_loss=0.0,
                profit_factor=None,
                expectancy=0.0,
                max_drawdown=0.0,
                max_drawdown_pct=0.0,
                max_consecutive_losses=0,
                average_r=None,
                average_mae=None,
                average_mfe=None,
                average_holding_minutes=None,
                r_distribution=empty_r_distribution,
                mae_distribution=self._empty_distribution(),
                mfe_distribution=self._empty_distribution(),
            )

        trade_count = len(trade_list)

        wins = [
            trade.net_pnl
            for trade in trade_list
            if trade.net_pnl > 0
        ]

        losses = [
            trade.net_pnl
            for trade in trade_list
            if trade.net_pnl < 0
        ]

        breakevens = [
            trade
            for trade in trade_list
            if trade.net_pnl == 0
        ]

        win_count = len(wins)
        loss_count = len(losses)
        breakeven_count = len(breakevens)

        win_rate = (
            win_count / trade_count
            if trade_count > 0
            else 0.0
        )

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))

        net_pnl = sum(
            trade.net_pnl
            for trade in trade_list
        )

        average_win = (
            gross_profit / win_count
            if win_count > 0
            else 0.0
        )

        average_loss = (
            gross_loss / loss_count
            if loss_count > 0
            else 0.0
        )

        if gross_loss > 0:
            profit_factor = (
                gross_profit / gross_loss
            )
        else:
            profit_factor = None

        expectancy = net_pnl / trade_count

        (
            max_drawdown,
            max_drawdown_pct,
        ) = self._calculate_drawdown(
            trade_list=trade_list,
            initial_capital=initial_capital,
        )

        max_consecutive_losses = (
            self._calculate_max_consecutive_losses(
                trade_list
            )
        )

        average_r = self._average_optional(
            trade.r_multiple
            for trade in trade_list
        )

        average_mae = self._average_optional(
            trade.mae_points
            for trade in trade_list
        )

        average_mfe = self._average_optional(
            trade.mfe_points
            for trade in trade_list
        )

        average_holding_minutes = (
            self._average_optional(
                trade.holding_minutes
                for trade in trade_list
            )
        )

        r_distribution = (
            self._calculate_r_distribution(
                trade_list
            )
        )

        mae_distribution = self._calculate_distribution(
            trade.mae_points
            for trade in trade_list
        )

        mfe_distribution = self._calculate_distribution(
            trade.mfe_points
            for trade in trade_list
        )

        return BacktestMetrics(
            trade_count=trade_count,
            win_count=win_count,
            loss_count=loss_count,
            breakeven_count=breakeven_count,
            win_rate=win_rate,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            net_pnl=net_pnl,
            average_win=average_win,
            average_loss=average_loss,
            profit_factor=profit_factor,
            expectancy=expectancy,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
            max_consecutive_losses=max_consecutive_losses,
            average_r=average_r,
            average_mae=average_mae,
            average_mfe=average_mfe,
            average_holding_minutes=average_holding_minutes,
            r_distribution=r_distribution,
            mae_distribution=mae_distribution,
            mfe_distribution=mfe_distribution,
        )

    def build_equity_curve(
        self,
        trades: Iterable[Trade],
        initial_capital: float,
    ) -> list[EquityPoint]:

        if initial_capital <= 0:
            raise ValueError(
                "initial_capital must be > 0"
            )

        trade_list = sorted(
            list(trades),
            key=lambda trade: trade.exit_time,
        )

        equity = initial_capital
        peak_equity = initial_capital

        curve: list[EquityPoint] = []

        for trade in trade_list:
            equity += trade.net_pnl

            peak_equity = max(
                peak_equity,
                equity,
            )

            drawdown = peak_equity - equity

            drawdown_pct = (
                drawdown / peak_equity
                if peak_equity > 0
                else 0.0
            )

            curve.append(
                EquityPoint(
                    trade_id=trade.trade_id,
                    exit_time=trade.exit_time,
                    net_pnl=trade.net_pnl,
                    equity=equity,
                    peak_equity=peak_equity,
                    drawdown=drawdown,
                    drawdown_pct=drawdown_pct,
                )
            )

        return curve

    @staticmethod
    def _calculate_drawdown(
        trade_list: list[Trade],
        initial_capital: float,
    ) -> tuple[float, float]:

        equity = initial_capital
        peak_equity = initial_capital

        max_drawdown = 0.0
        max_drawdown_pct = 0.0

        for trade in trade_list:
            equity += trade.net_pnl

            if equity > peak_equity:
                peak_equity = equity

            drawdown = peak_equity - equity

            drawdown_pct = (
                drawdown / peak_equity
                if peak_equity > 0
                else 0.0
            )

            max_drawdown = max(
                max_drawdown,
                drawdown,
            )

            max_drawdown_pct = max(
                max_drawdown_pct,
                drawdown_pct,
            )

        return max_drawdown, max_drawdown_pct

    @staticmethod
    def _calculate_max_consecutive_losses(
        trade_list: list[Trade],
    ) -> int:

        current = 0
        maximum = 0

        for trade in trade_list:
            if trade.net_pnl < 0:
                current += 1
                maximum = max(
                    maximum,
                    current,
                )
            else:
                current = 0

        return maximum

    @staticmethod
    def _empty_distribution() -> DistributionStats:
        return DistributionStats(
            count=0,
            average=None,
            median=None,
            minimum=None,
            maximum=None,
        )

    @staticmethod
    def _calculate_distribution(
        values: Iterable[float | None],
    ) -> DistributionStats:

        valid_values = sorted(
            value
            for value in values
            if value is not None
        )

        if not valid_values:
            return MetricsCalculator._empty_distribution()

        count = len(valid_values)

        average = sum(valid_values) / count

        if count % 2 == 1:
            median = valid_values[count // 2]
        else:
            middle = count // 2
            median = (
                valid_values[middle - 1]
                + valid_values[middle]
            ) / 2

        return DistributionStats(
            count=count,
            average=average,
            median=median,
            minimum=min(valid_values),
            maximum=max(valid_values),
        )

    @staticmethod
    def _calculate_r_distribution(
        trade_list: list[Trade],
    ) -> RDistribution:

        values = sorted(
            trade.r_multiple
            for trade in trade_list
            if trade.r_multiple is not None
        )

        if not values:
            return RDistribution(
                count=0,
                average_r=None,
                median_r=None,
                min_r=None,
                max_r=None,
                positive_r_count=0,
                negative_r_count=0,
                zero_r_count=0,
                r_1_or_more_count=0,
                r_2_or_more_count=0,
                r_3_or_more_count=0,
                minus_1_or_less_count=0,
            )

        count = len(values)

        average_r = sum(values) / count

        if count % 2 == 1:
            median_r = values[count // 2]
        else:
            middle = count // 2
            median_r = (
                values[middle - 1]
                + values[middle]
            ) / 2

        return RDistribution(
            count=count,
            average_r=average_r,
            median_r=median_r,
            min_r=min(values),
            max_r=max(values),
            positive_r_count=sum(
                1 for value in values
                if value > 0
            ),
            negative_r_count=sum(
                1 for value in values
                if value < 0
            ),
            zero_r_count=sum(
                1 for value in values
                if value == 0
            ),
            r_1_or_more_count=sum(
                1 for value in values
                if value >= 1
            ),
            r_2_or_more_count=sum(
                1 for value in values
                if value >= 2
            ),
            r_3_or_more_count=sum(
                1 for value in values
                if value >= 3
            ),
            minus_1_or_less_count=sum(
                1 for value in values
                if value <= -1
            ),
        )

    @staticmethod
    def _average_optional(
        values: Iterable[float | None],
    ) -> float | None:

        valid_values = [
            value
            for value in values
            if value is not None
        ]

        if not valid_values:
            return None

        return sum(valid_values) / len(valid_values)
