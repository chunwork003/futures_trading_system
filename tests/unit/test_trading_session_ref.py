import pytest
from pydantic import ValidationError

from domain.trading_session import TradingSessionRef


def make_session_ref(**overrides: str) -> TradingSessionRef:
    values = {
        "session_ref": "TAIFEX-FUTURES",
        "exchange": "TAIFEX",
        "timezone": "Asia/Taipei",
        "rule_version": "TAIFEX-FUTURES-2026-V1",
    }
    values.update(overrides)
    return TradingSessionRef(**values)


def test_valid_trading_session_reference():
    reference = make_session_ref(exchange=" taifex ")

    assert reference.session_ref == "TAIFEX-FUTURES"
    assert reference.exchange == "TAIFEX"
    assert reference.timezone == "Asia/Taipei"
    assert reference.rule_version == "TAIFEX-FUTURES-2026-V1"


@pytest.mark.parametrize("field", ["session_ref", "exchange", "rule_version"])
def test_trading_session_reference_rejects_blank_identity_fields(field: str):
    with pytest.raises(ValidationError):
        make_session_ref(**{field: "   "})


def test_trading_session_reference_accepts_asia_taipei():
    reference = make_session_ref(timezone="Asia/Taipei")

    assert reference.timezone == "Asia/Taipei"


@pytest.mark.parametrize("timezone", ["", "   ", "Taiwan/Not-A-Timezone"])
def test_trading_session_reference_rejects_invalid_iana_timezone(timezone: str):
    with pytest.raises(ValidationError):
        make_session_ref(timezone=timezone)
