from __future__ import annotations

from abc import ABC, abstractmethod

from backtest.models import Fill, Order


class Broker(ABC):
    @abstractmethod
    def submit_order(self, order: Order) -> Fill:
        """Submit an order and return its fill result."""
        raise NotImplementedError

    @abstractmethod
    def get_order(self, order_id: str) -> Order | None:
        """Return an order by ID, or None when it does not exist."""
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str) -> Order:
        """Cancel a pending order and return its updated state."""
        raise NotImplementedError
