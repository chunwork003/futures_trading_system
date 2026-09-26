import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from persistence.execution import order_event_as_trading_event
from trading.execution import (
    OrderEvent,
    OrderStatus,
    validate_order_event_transition,
)


OCCURRED_LOCAL = datetime(
    2026,
    9,
    25,
    9,
    0,
    0,
    tzinfo=timezone(timedelta(hours=8)),
)

RECEIVED_LOCAL = datetime(
    2026,
    9,
    24,
    21,
    0,
    3,
    tzinfo=timezone(timedelta(hours=-4)),
)

OCCURRED_UTC = datetime(
    2026,
    9,
    25,
    1,
    0,
    0,
    tzinfo=timezone.utc,
)

RECEIVED_UTC = datetime(
    2026,
    9,
    25,
    1,
    0,
    3,
    tzinfo=timezone.utc,
)


def _event(**updates: object) -> OrderEvent:
    values: dict[str, object] = {
        "event_id": "EV-0",
        "order_id": "ORD-1",
        "correlation_id": "CORR-1",
        "causation_id": "INT-1",
        "idempotency_key": "KEY-0",
        "sequence": 0,
        "previous_status": None,
        "status": OrderStatus.PENDING,
        "occurred_at": OCCURRED_LOCAL,
        "received_at": RECEIVED_LOCAL,
    }

    values.update(updates)

    return OrderEvent(**values)


@pytest.mark.parametrize(
    "field",
    ["occurred_at", "received_at"],
)
def test_order_event_requires_both_time_evidence_fields(
    field: str,
) -> None:
    values = _event().model_dump()
    values.pop(field)

    with pytest.raises(ValidationError):
        OrderEvent(**values)


@pytest.mark.parametrize(
    "field",
    ["occurred_at", "received_at"],
)
def test_order_event_rejects_naive_time_evidence(
    field: str,
) -> None:
    values = _event().model_dump()
    values[field] = datetime(2026, 9, 25, 1, 0)

    with pytest.raises(
        ValidationError,
        match="timezone-aware",
    ):
        OrderEvent(**values)


def test_order_event_normalizes_time_evidence_independently() -> None:
    event = _event()

    assert event.occurred_at == OCCURRED_UTC
    assert event.received_at == RECEIVED_UTC
    assert event.occurred_at != event.received_at


def test_mapping_preserves_exact_distinct_time_evidence() -> None:
    event = _event()

    mapped = order_event_as_trading_event(event)

    assert mapped.occurred_at == event.occurred_at
    assert mapped.received_at == event.received_at
    assert mapped.occurred_at != mapped.received_at


def test_received_at_may_precede_occurred_at() -> None:
    event = _event(
        occurred_at=datetime(
            2026,
            9,
            25,
            2,
            0,
            tzinfo=timezone.utc,
        ),
        received_at=datetime(
            2026,
            9,
            25,
            1,
            59,
            tzinfo=timezone.utc,
        ),
    )

    assert event.received_at < event.occurred_at

    validate_order_event_transition(None, event)


def test_sequence_remains_authority_despite_reverse_timestamp_order() -> None:
    previous = _event(
        occurred_at=datetime(
            2026,
            9,
            25,
            5,
            0,
            tzinfo=timezone.utc,
        ),
        received_at=datetime(
            2026,
            9,
            25,
            5,
            1,
            tzinfo=timezone.utc,
        ),
    )

    current = _event(
        event_id="EV-1",
        causation_id="EV-0",
        idempotency_key="KEY-1",
        sequence=1,
        previous_status=OrderStatus.PENDING,
        status=OrderStatus.SUBMITTED,
        occurred_at=datetime(
            2026,
            9,
            25,
            1,
            0,
            tzinfo=timezone.utc,
        ),
        received_at=datetime(
            2026,
            9,
            25,
            0,
            59,
            tzinfo=timezone.utc,
        ),
    )

    assert current.occurred_at < previous.occurred_at
    assert current.received_at < previous.received_at

    validate_order_event_transition(previous, current)


def test_mapping_has_no_occurred_to_received_fallback() -> None:
    tree = ast.parse(
        Path("persistence/execution.py").read_text(
            encoding="utf-8-sig"
        )
    )

    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "order_event_as_trading_event"
    )

    trading_event_call = next(
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "TradingEvent"
    )

    keywords = {
        keyword.arg: keyword.value
        for keyword in trading_event_call.keywords
        if keyword.arg is not None
    }

    occurred = keywords["occurred_at"]
    received = keywords["received_at"]

    assert isinstance(occurred, ast.Attribute)
    assert isinstance(occurred.value, ast.Name)
    assert occurred.value.id == "event"
    assert occurred.attr == "occurred_at"

    assert isinstance(received, ast.Attribute)
    assert isinstance(received.value, ast.Name)
    assert received.value.id == "event"
    assert received.attr == "received_at"


def test_c22_has_no_system_clock_fabrication() -> None:
    for path in (
        "trading/execution.py",
        "persistence/execution.py",
    ):
        tree = ast.parse(
            Path(path).read_text(encoding="utf-8-sig"),
            filename=path,
        )

        fabricated: list[str] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            func = node.func

            if (
                isinstance(func, ast.Attribute)
                and func.attr in {"now", "utcnow"}
                and isinstance(func.value, ast.Name)
                and func.value.id == "datetime"
            ):
                fabricated.append(
                    f"datetime.{func.attr}"
                )

        assert fabricated == [], (
            f"{path} fabricates canonical time evidence: "
            f"{fabricated}"
        )


def test_c22_does_not_absorb_market_observation_authority() -> None:
    for path in (
        "trading/execution.py",
        "persistence/execution.py",
    ):
        tree = ast.parse(
            Path(path).read_text(encoding="utf-8-sig"),
            filename=path,
        )

        symbols: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.ClassDef,
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                symbols.add(node.name)

            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    symbols.add(alias.asname or alias.name)

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    symbols.add(
                        alias.asname
                        or alias.name.rsplit(".", 1)[-1]
                    )

        assert not any(
            symbol.startswith("MarketObservation")
            for symbol in symbols
        )
