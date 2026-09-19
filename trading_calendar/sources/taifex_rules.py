from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True)
class TAIFEXSessionRule:
    effective_from: date
    effective_to: date | None

    day_open: time
    day_close: time

    night_enabled: bool
    night_open: time | None
    night_close: time | None


TAIFEX_RULES = [
    TAIFEXSessionRule(
        effective_from=date(2001, 1, 1),
        effective_to=date(2017, 5, 14),

        day_open=time(8, 45),
        day_close=time(13, 45),

        night_enabled=False,
        night_open=None,
        night_close=None,
    ),

    TAIFEXSessionRule(
        effective_from=date(2017, 5, 15),
        effective_to=None,

        day_open=time(8, 45),
        day_close=time(13, 45),

        night_enabled=True,
        night_open=time(15, 0),
        night_close=time(5, 0),
    ),
]


def get_session_rule(
    trade_date: date,
) -> TAIFEXSessionRule:

    for rule in TAIFEX_RULES:

        if trade_date < rule.effective_from:
            continue

        if (
            rule.effective_to is not None
            and trade_date > rule.effective_to
        ):
            continue

        return rule

    raise ValueError(
        f"No TAIFEX session rule for {trade_date}"
    )