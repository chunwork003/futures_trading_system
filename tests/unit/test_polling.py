import pytest

from backtest.polling import PollingConfig


def test_polling_config_defaults_to_30_seconds():
    config = PollingConfig()

    assert config.interval_seconds == 30.0


def test_polling_config_accepts_custom_interval():
    config = PollingConfig(interval_seconds=10.0)

    assert config.interval_seconds == 10.0


def test_polling_config_rejects_zero():
    with pytest.raises(ValueError, match="greater than 0"):
        PollingConfig(interval_seconds=0)


def test_polling_config_rejects_negative():
    with pytest.raises(ValueError, match="greater than 0"):
        PollingConfig(interval_seconds=-1)
