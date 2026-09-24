import pytest

from backtest.fixed_quantity_sizing import FixedQuantitySizing
from backtest.position_sizing_registry import PositionSizingRegistry


def test_position_sizing_registry_register_and_get():
    registry = PositionSizingRegistry()
    strategy = FixedQuantitySizing(quantity=2)

    registry.register("fixed_quantity", strategy)

    assert registry.get("fixed_quantity") is strategy


def test_position_sizing_registry_lists_names():
    registry = PositionSizingRegistry()

    registry.register(
        "fixed_quantity",
        FixedQuantitySizing(quantity=2),
    )

    assert registry.names() == ("fixed_quantity",)


def test_position_sizing_registry_rejects_duplicate_name():
    registry = PositionSizingRegistry()

    registry.register(
        "fixed_quantity",
        FixedQuantitySizing(quantity=2),
    )

    with pytest.raises(ValueError):
        registry.register(
            "fixed_quantity",
            FixedQuantitySizing(quantity=3),
        )


def test_position_sizing_registry_rejects_empty_name():
    registry = PositionSizingRegistry()

    with pytest.raises(ValueError):
        registry.register(
            "",
            FixedQuantitySizing(quantity=2),
        )


def test_position_sizing_registry_rejects_unknown_strategy():
    registry = PositionSizingRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")
