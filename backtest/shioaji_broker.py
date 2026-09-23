from __future__ import annotations

from typing import Any

import shioaji as sj

from backtest.broker import Broker
from backtest.execution_result import OrderSubmission
from backtest.models import Fill, Order
from backtest.shioaji_contracts import resolve_future_contract
from backtest.shioaji_fill import merge_fills, to_fills
from backtest.shioaji_mapping import to_order_status, to_shioaji_order


class ShioajiBroker(Broker):
    def __init__(self, api: sj.Shioaji, account: Any = None) -> None:
        self.api = api
        self.account = account
        self._orders: dict[str, Order] = {}
        self._trades: dict[str, Any] = {}
        self._delivered_fill_seqs: dict[str, set[str]] = {}

    def submit_order(self, order: Order) -> OrderSubmission:
        contracts = self.api.Contracts
        contract = resolve_future_contract(
            contracts,
            order.contract or "",
        )

        octype = (
            sj.FuturesOCType.New
            if order.order_id.startswith("ENTRY-")
            else sj.FuturesOCType.Cover
        )

        shioaji_order = to_shioaji_order(
            order,
            octype,
        )

        trade = self.api.place_order(
            contract,
            shioaji_order,
        )

        mapped_status = to_order_status(trade.status.status)

        submitted_order = order.model_copy(
            update={"status": mapped_status}
        )

        self._orders[order.order_id] = submitted_order
        self._trades[order.order_id] = trade

        fills = to_fills(
            order_id=order.order_id,
            deals=trade.status.deals,
            requested_price=order.requested_price or 0.0,
            commission=order.commission,
            slippage_points=order.slippage_points,
        )

        delivered_seqs = self._delivered_fill_seqs.setdefault(
            order.order_id,
            set(),
        )
        delivered_seqs.update(
            deal.seq
            for deal in trade.status.deals
        )

        if fills:
            filled_order = submitted_order.model_copy(
                update={
                    "status": mapped_status,
                    "fill_price": merge_fills(fills).price,
                }
            )
            self._orders[order.order_id] = filled_order
            submitted_order = filled_order

        return OrderSubmission(
            order=submitted_order,
            fills=fills,
        )

    def get_order(self, order_id: str) -> Order | None:
        order = self._orders.get(order_id)

        if order is None:
            return None

        trade = self._trades.get(order_id)

        if trade is None:
            return order

        self.api.update_status(trade=trade)

        mapped_status = to_order_status(
            trade.status.status
        )

        fills = to_fills(
            order_id=order_id,
            deals=trade.status.deals,
            requested_price=order.requested_price or 0.0,
            commission=order.commission,
            slippage_points=order.slippage_points,
        )

        update_data = {
            "status": mapped_status,
        }

        if fills:
            update_data["fill_price"] = merge_fills(fills).price

        updated_order = order.model_copy(
            update=update_data
        )

        self._orders[order_id] = updated_order

        return updated_order

    def get_fills(self, order_id: str) -> list[Fill]:
        order = self._orders.get(order_id)
        trade = self._trades.get(order_id)

        if order is None or trade is None:
            return []

        self.api.update_status(trade=trade)

        delivered_seqs = self._delivered_fill_seqs.setdefault(
            order_id,
            set(),
        )

        new_deals = [
            deal
            for deal in trade.status.deals
            if deal.seq not in delivered_seqs
        ]

        fills = to_fills(
            order_id=order_id,
            deals=new_deals,
            requested_price=order.requested_price or 0.0,
            commission=order.commission,
            slippage_points=order.slippage_points,
        )

        delivered_seqs.update(
            deal.seq
            for deal in new_deals
        )

        return fills

    def cancel_order(self, order_id: str) -> Order:
        order = self._orders.get(order_id)

        if order is None:
            raise ValueError(f"Unknown order_id: {order_id}")

        trade = self._trades.get(order_id)

        if trade is None:
            raise ValueError(f"Unknown trade for order_id: {order_id}")

        self.api.cancel_order(trade)
        self.api.update_status(trade=trade)

        mapped_status = to_order_status(
            trade.status.status
        )

        fills = to_fills(
            order_id=order_id,
            deals=trade.status.deals,
            requested_price=order.requested_price or 0.0,
            commission=order.commission,
            slippage_points=order.slippage_points,
        )

        update_data = {
            "status": mapped_status,
        }

        if fills:
            update_data["fill_price"] = merge_fills(fills).price

        updated_order = order.model_copy(
            update=update_data
        )

        self._orders[order_id] = updated_order

        return updated_order
