from __future__ import annotations

from abc import ABC, abstractmethod

from backtest.execution_result import OrderSubmission
from backtest.models import Fill, Order
from trading.execution import OrderIntent


class Broker(ABC):
    @abstractmethod
    def submit_order(
        self,
        order: Order,
        *,
        intent: OrderIntent | None = None,
    ) -> OrderSubmission:
        """Submit an order and return its submission result."""
        raise NotImplementedError

    @abstractmethod
    def get_order(self, order_id: str) -> Order | None:
        """Return an order by ID, or None when it does not exist."""
        raise NotImplementedError

    @abstractmethod
    def get_fills(self, order_id: str) -> list[Fill]:
        """Return fills recorded for an order."""
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str) -> Order:
        """Cancel a pending order and return its updated state."""
        raise NotImplementedError
