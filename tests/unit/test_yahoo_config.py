import pytest

from ingestion.yahoo_config import (
    YAHOO_INTERVAL_POLICIES,
    get_interval_policy,
    get_symbol_config,
)


def test_yahoo_1m_policy():
    policy = get_interval_policy("1m")

    assert policy.interval == "1m"
    assert policy.max_intraday_days == 60


def test_yahoo_5m_policy():
    policy = get_interval_policy("5m")

    assert policy.interval == "5m"
    assert policy.max_intraday_days == 60


def test_yahoo_15m_policy():
    policy = get_interval_policy("15m")

    assert policy.interval == "15m"
    assert policy.max_intraday_days == 60


def test_yahoo_1h_policy():
    policy = get_interval_policy("1h")

    assert policy.interval == "1h"
    assert policy.max_intraday_days == 730


def test_yahoo_daily_policy():
    policy = get_interval_policy("1d")

    assert policy.interval == "1d"
    assert policy.max_intraday_days is None


def test_txf_yahoo_mapping_requires_verified_ticker():
    with pytest.raises(ValueError, match="No verified Yahoo Finance mapping"):
        get_symbol_config("TXF")


def test_twii_yahoo_mapping():
    config = get_symbol_config("TWII")

    assert config.canonical_symbol == "TWII"
    assert config.yahoo_symbol == "^TWII"
    assert config.instrument_type == "index"
    assert config.comparison_eligible is False


def test_interval_policy_registry():
    assert "1m" in YAHOO_INTERVAL_POLICIES
    assert "5m" in YAHOO_INTERVAL_POLICIES
    assert "15m" in YAHOO_INTERVAL_POLICIES
    assert "1h" in YAHOO_INTERVAL_POLICIES
    assert "1d" in YAHOO_INTERVAL_POLICIES
