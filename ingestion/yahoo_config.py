from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class YahooSymbolConfig:
    canonical_symbol: str
    yahoo_symbol: str
    instrument_type: str
    comparison_eligible: bool
    timezone: str


# Only verified Yahoo Finance mappings belong here.
#
# TWII:
#   Yahoo symbol: ^TWII
#   Purpose: reference/index data only
#
# TXF:
#   No verified Yahoo Finance futures ticker.
#   Therefore TXF is intentionally NOT mapped to a guessed Yahoo symbol.
YAHOO_SYMBOLS = {
    "TWII": YahooSymbolConfig(
        canonical_symbol="TWII",
        yahoo_symbol="^TWII",
        instrument_type="index",
        comparison_eligible=False,
        timezone="Asia/Taipei",
    ),
}


@dataclass(frozen=True)
class YahooIntervalPolicy:
    interval: str
    max_intraday_days: Optional[int]

    # Backward-compatible alias for code that uses the shorter name.
    @property
    def max_days(self) -> Optional[int]:
        return self.max_intraday_days


YAHOO_INTERVAL_POLICIES = {
    "1m": YahooIntervalPolicy("1m", 60),
    "2m": YahooIntervalPolicy("2m", 60),
    "5m": YahooIntervalPolicy("5m", 60),
    "15m": YahooIntervalPolicy("15m", 60),
    "30m": YahooIntervalPolicy("30m", 60),
    "90m": YahooIntervalPolicy("90m", 60),
    "60m": YahooIntervalPolicy("60m", 730),
    "1h": YahooIntervalPolicy("1h", 730),
    "1d": YahooIntervalPolicy("1d", None),
    "5d": YahooIntervalPolicy("5d", None),
    "1wk": YahooIntervalPolicy("1wk", None),
    "1mo": YahooIntervalPolicy("1mo", None),
    "3mo": YahooIntervalPolicy("3mo", None),
}


def get_symbol_config(symbol: str) -> YahooSymbolConfig:
    try:
        return YAHOO_SYMBOLS[symbol]
    except KeyError as exc:
        raise ValueError(
            f"No verified Yahoo Finance mapping for symbol: {symbol}"
        ) from exc


def get_interval_policy(interval: str) -> YahooIntervalPolicy:
    try:
        return YAHOO_INTERVAL_POLICIES[interval]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported Yahoo interval: {interval}"
        ) from exc


def is_comparison_eligible(symbol: str) -> bool:
    return get_symbol_config(symbol).comparison_eligible
