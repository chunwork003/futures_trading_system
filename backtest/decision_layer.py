from __future__ import annotations

from collections.abc import Iterable

from backtest.models import Direction
from backtest.strategy_attribution import StrategyAttribution
from backtest.strategy_conflict_policy import StrategyConflictPolicy
from backtest.strategy_position import StrategyVirtualPosition
from backtest.target_position import TargetAccountPosition


class MultiStrategyDecisionLayer:
    def __init__(
        self,
        conflict_policy: StrategyConflictPolicy | None = None,
    ) -> None:
        self.conflict_policy = conflict_policy

    def decide(
        self,
        positions: Iterable[StrategyVirtualPosition],
    ) -> TargetAccountPosition:
        positions = list(positions)

        if not positions:
            raise ValueError("at least one strategy position is required")

        first = positions[0]

        for position in positions[1:]:
            if position.symbol != first.symbol:
                raise ValueError(
                    "all strategy positions must use the same symbol"
                )

            if position.contract != first.contract:
                raise ValueError(
                    "all strategy positions must use the same contract"
                )

        directions = {position.direction for position in positions}

        if len(directions) > 1:
            if self.conflict_policy is None:
                raise ValueError(
                    "conflicting strategy directions require conflict resolution"
                )

            direction = self.conflict_policy.resolve(positions)

            selected = [
                position
                for position in positions
                if position.direction == direction
            ]

            quantity = sum(
                position.quantity
                for position in selected
            )

            attributions = [
                StrategyAttribution(
                    strategy_id=position.strategy_id,
                    symbol=position.symbol,
                    contract=position.contract,
                    direction=position.direction,
                    quantity=position.quantity,
                )
                for position in selected
            ]

            return TargetAccountPosition(
                symbol=first.symbol,
                contract=first.contract,
                direction=direction,
                quantity=quantity,
                attributions=attributions,
            )

        attributions = [
            StrategyAttribution(
                strategy_id=position.strategy_id,
                symbol=position.symbol,
                contract=position.contract,
                direction=position.direction,
                quantity=position.quantity,
            )
            for position in positions
        ]

        return TargetAccountPosition(
            symbol=first.symbol,
            contract=first.contract,
            direction=first.direction,
            quantity=sum(position.quantity for position in positions),
            attributions=attributions,
        )
