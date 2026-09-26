from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import re
from typing import Final


IDENTITY_SCHEMA_VERSION: Final[int] = 1
CONTENT_SCHEMA_VERSION: Final[int] = 1

_CONTENT_FRAME_HEADER: Final[bytes] = b"market-observation-content-v1\n"
_REVISION_FRAME_HEADER: Final[bytes] = b"market-observation-revision-id-v1\n"
_CANONICAL_NULL: Final[str] = "null"

_TIMEFRAME_PATTERN = re.compile(r"^([0-9]+)\s*([smhd])$", re.IGNORECASE)
_FINGERPRINT_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_REVISION_ID_PATTERN = re.compile(r"^mor1_[0-9a-f]{64}$")


class MarketObservationContractError(ValueError):
    """Canonical 市場觀測 identity/content 違反已凍結的 domain contract。"""


def _require_positive_int(value: object, field_name: str) -> int:
    """Canonical identity 整數必須為真正的正整數，不接受 bool 或 float。"""

    if type(value) is not int or value <= 0:
        raise MarketObservationContractError(
            f"{field_name} must be a positive integer"
        )
    return value


def _normalize_exact_decimal(
    value: object,
    field_name: str,
) -> Decimal:
    """將 exact decimal evidence 正規化；禁止 binary float 進入 identity。"""

    if isinstance(value, bool) or isinstance(value, float):
        raise MarketObservationContractError(
            f"{field_name} must use exact decimal semantics"
        )

    if isinstance(value, Decimal):
        candidate = value
    elif type(value) is int:
        candidate = Decimal(value)
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise MarketObservationContractError(
                f"{field_name} must not be blank"
            )
        try:
            candidate = Decimal(text)
        except InvalidOperation as error:
            raise MarketObservationContractError(
                f"{field_name} must be an exact decimal"
            ) from error
    else:
        raise MarketObservationContractError(
            f"{field_name} must be Decimal, integer, or exact decimal string"
        )

    if not candidate.is_finite():
        raise MarketObservationContractError(
            f"{field_name} must be finite"
        )

    # -0、-0.0 與 +0 為同一 exact semantic value。
    if candidate == 0:
        return Decimal(0)

    return candidate


def _decimal_lexical(
    value: object,
    field_name: str,
) -> str:
    """產生不含 exponent/trailing-zero 的 canonical fixed-point 字串。"""

    candidate = _normalize_exact_decimal(value, field_name)

    if candidate == 0:
        return "0"

    text = format(candidate, "f")

    if "." in text:
        text = text.rstrip("0").rstrip(".")

    return text


def _normalize_count(
    value: object,
    field_name: str,
) -> int:
    """Volume/count evidence 必須是非負 exact integer。"""

    if type(value) is not int or value < 0:
        raise MarketObservationContractError(
            f"{field_name} must be a non-negative integer"
        )
    return value


def _normalize_optional_count(
    value: object | None,
    field_name: str,
) -> int | None:
    if value is None:
        return None
    return _normalize_count(value, field_name)


def _normalize_trade_date(value: object) -> date:
    """Trade date 必須是純 date，不接受 datetime 偷渡 calendar semantics。"""

    if type(value) is not date:
        raise MarketObservationContractError(
            "trade_date must be a date"
        )
    return value


def _normalize_session_ref(value: object | None) -> str | None:
    """Optional canonical session reference；有值時不可為空白。"""

    if value is None:
        return None

    if not isinstance(value, str):
        raise MarketObservationContractError(
            "session_ref must be a string or None"
        )

    normalized = value.strip()

    if not normalized:
        raise MarketObservationContractError(
            "session_ref must not be blank"
        )

    return normalized


def normalize_market_observation_timeframe(value: object) -> str:
    """正規化固定 duration timeframe，但不把 24h 推論成 calendar 1d。"""

    if not isinstance(value, str):
        raise MarketObservationContractError(
            "timeframe must be a string"
        )

    normalized = value.strip().lower()
    match = _TIMEFRAME_PATTERN.fullmatch(normalized)

    if match is None:
        raise MarketObservationContractError(
            "timeframe must be a positive integer duration using s/m/h/d"
        )

    quantity = int(match.group(1))
    unit = match.group(2).lower()

    if quantity <= 0:
        raise MarketObservationContractError(
            "timeframe quantity must be positive"
        )

    # 只在 fixed-duration s/m/h 家族中做確定性的整除正規化。
    # 刻意不跨入 d，避免把 24h 靜默等同 calendar/session 1d。
    if unit == "s":
        if quantity % 3600 == 0:
            return f"{quantity // 3600}h"
        if quantity % 60 == 0:
            return f"{quantity // 60}m"
        return f"{quantity}s"

    if unit == "m":
        if quantity % 60 == 0:
            return f"{quantity // 60}h"
        return f"{quantity}m"

    if unit == "h":
        return f"{quantity}h"

    return f"{quantity}d"


def _normalize_aware_utc(value: object) -> datetime:
    """Canonical observation time 必須 timezone-aware 並正規化為 UTC。"""

    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise MarketObservationContractError(
            "interval_start_at must be timezone-aware"
        )

    return value.astimezone(timezone.utc)


def _utc_lexical(value: datetime) -> str:
    """固定六位 microsecond + Z 的 UTC identity lexical form。"""

    normalized = _normalize_aware_utc(value)

    return normalized.strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )


def _frame_bytes(
    header: bytes,
    fields: tuple[tuple[str, str], ...],
) -> bytes:
    """依 frozen byte framing contract 建立 deterministic UTF-8 bytes。"""

    chunks = [header]

    for field_name, value in fields:
        name_bytes = field_name.encode("ascii")
        value_bytes = value.encode("utf-8")

        chunks.append(
            name_bytes
            + b":"
            + str(len(value_bytes)).encode("ascii")
            + b":"
            + value_bytes
            + b"\n"
        )

    return b"".join(chunks)


@dataclass(frozen=True, slots=True, init=False)
class MarketObservationLogicalKey:
    """市場觀測時間 locus；payload 修訂不改變此 logical identity。"""

    instrument_id: int
    contract_id: int | None
    timeframe: str
    interval_start_at: datetime

    def __init__(
        self,
        *,
        instrument_id: int,
        contract_id: int | None,
        timeframe: str,
        interval_start_at: datetime,
        requires_contract_id: bool,
    ) -> None:
        if type(requires_contract_id) is not bool:
            raise MarketObservationContractError(
                "requires_contract_id must be bool"
            )

        normalized_instrument_id = _require_positive_int(
            instrument_id,
            "instrument_id",
        )

        normalized_contract_id: int | None

        if contract_id is None:
            if requires_contract_id:
                raise MarketObservationContractError(
                    "contract_id is required for listed-contract observation"
                )
            normalized_contract_id = None
        else:
            normalized_contract_id = _require_positive_int(
                contract_id,
                "contract_id",
            )

        object.__setattr__(
            self,
            "instrument_id",
            normalized_instrument_id,
        )
        object.__setattr__(
            self,
            "contract_id",
            normalized_contract_id,
        )
        object.__setattr__(
            self,
            "timeframe",
            normalize_market_observation_timeframe(timeframe),
        )
        object.__setattr__(
            self,
            "interval_start_at",
            _normalize_aware_utc(interval_start_at),
        )

    @property
    def interval_start_at_lexical(self) -> str:
        """供跨語言 golden vector 驗證的 canonical UTC lexical form。"""

        return _utc_lexical(self.interval_start_at)


@dataclass(frozen=True, slots=True)
class MarketObservationContentFingerprint:
    """Opaque lowercase SHA-256 content fingerprint。"""

    value: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.value, str)
            or _FINGERPRINT_PATTERN.fullmatch(self.value) is None
        ):
            raise MarketObservationContractError(
                "content fingerprint must be 64 lowercase SHA-256 hex characters"
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class MarketObservationRevisionId:
    """Opaque revision-specific deterministic observation reference。"""

    value: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.value, str)
            or _REVISION_ID_PATTERN.fullmatch(self.value) is None
        ):
            raise MarketObservationContractError(
                "revision ID must use mor1_<64 lowercase SHA-256 hex>"
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CanonicalMarketObservationContent:
    """Strategy-visible market/classification evidence 的 canonical value。"""

    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    amount: Decimal | None
    trade_count: int | None
    tick_count: int | None
    trade_date: date
    session_ref: str | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "open",
            _normalize_exact_decimal(self.open, "open"),
        )
        object.__setattr__(
            self,
            "high",
            _normalize_exact_decimal(self.high, "high"),
        )
        object.__setattr__(
            self,
            "low",
            _normalize_exact_decimal(self.low, "low"),
        )
        object.__setattr__(
            self,
            "close",
            _normalize_exact_decimal(self.close, "close"),
        )
        object.__setattr__(
            self,
            "volume",
            _normalize_count(self.volume, "volume"),
        )

        if self.amount is not None:
            object.__setattr__(
                self,
                "amount",
                _normalize_exact_decimal(
                    self.amount,
                    "amount",
                ),
            )

        object.__setattr__(
            self,
            "trade_count",
            _normalize_optional_count(
                self.trade_count,
                "trade_count",
            ),
        )
        object.__setattr__(
            self,
            "tick_count",
            _normalize_optional_count(
                self.tick_count,
                "tick_count",
            ),
        )
        object.__setattr__(
            self,
            "trade_date",
            _normalize_trade_date(self.trade_date),
        )
        object.__setattr__(
            self,
            "session_ref",
            _normalize_session_ref(self.session_ref),
        )

    @property
    def content_schema_version(self) -> int:
        return CONTENT_SCHEMA_VERSION

    def _canonical_fields(self) -> tuple[tuple[str, str], ...]:
        return (
            (
                "content_schema_version",
                str(CONTENT_SCHEMA_VERSION),
            ),
            ("open", _decimal_lexical(self.open, "open")),
            ("high", _decimal_lexical(self.high, "high")),
            ("low", _decimal_lexical(self.low, "low")),
            ("close", _decimal_lexical(self.close, "close")),
            ("volume", str(self.volume)),
            (
                "amount",
                _CANONICAL_NULL
                if self.amount is None
                else _decimal_lexical(self.amount, "amount"),
            ),
            (
                "trade_count",
                _CANONICAL_NULL
                if self.trade_count is None
                else str(self.trade_count),
            ),
            (
                "tick_count",
                _CANONICAL_NULL
                if self.tick_count is None
                else str(self.tick_count),
            ),
            ("trade_date", self.trade_date.isoformat()),
            (
                "session_ref",
                _CANONICAL_NULL
                if self.session_ref is None
                else self.session_ref,
            ),
        )

    @property
    def content_fingerprint(
        self,
    ) -> MarketObservationContentFingerprint:
        """以 explicit versioned frame 產生 deterministic content identity。"""

        digest = sha256(
            _frame_bytes(
                _CONTENT_FRAME_HEADER,
                self._canonical_fields(),
            )
        ).hexdigest()

        return MarketObservationContentFingerprint(digest)


def canonicalize_market_observation_content(
    *,
    open: Decimal | int | str,
    high: Decimal | int | str,
    low: Decimal | int | str,
    close: Decimal | int | str,
    volume: int,
    amount: Decimal | int | str | None,
    trade_count: int | None,
    tick_count: int | None,
    trade_date: date,
    session_ref: str | None,
) -> CanonicalMarketObservationContent:
    """Canonical content 單一入口；source adapter 不得自行定義 fingerprint。"""

    return CanonicalMarketObservationContent(
        open=_normalize_exact_decimal(open, "open"),
        high=_normalize_exact_decimal(high, "high"),
        low=_normalize_exact_decimal(low, "low"),
        close=_normalize_exact_decimal(close, "close"),
        volume=_normalize_count(volume, "volume"),
        amount=(
            None
            if amount is None
            else _normalize_exact_decimal(amount, "amount")
        ),
        trade_count=_normalize_optional_count(
            trade_count,
            "trade_count",
        ),
        tick_count=_normalize_optional_count(
            tick_count,
            "tick_count",
        ),
        trade_date=_normalize_trade_date(trade_date),
        session_ref=_normalize_session_ref(session_ref),
    )


def canonicalize_market_observation_logical_key(
    *,
    instrument_id: int,
    contract_id: int | None,
    timeframe: str,
    interval_start_at: datetime,
    requires_contract_id: bool,
) -> MarketObservationLogicalKey:
    """建立 canonical logical key；listed-contract requirement 必須顯式傳入。"""

    return MarketObservationLogicalKey(
        instrument_id=instrument_id,
        contract_id=contract_id,
        timeframe=timeframe,
        interval_start_at=interval_start_at,
        requires_contract_id=requires_contract_id,
    )


def build_market_observation_revision_id(
    *,
    logical_key: MarketObservationLogicalKey,
    content_fingerprint: MarketObservationContentFingerprint,
) -> MarketObservationRevisionId:
    """由 logical identity + exact content fingerprint 建立 opaque mor1 ID。"""

    if not isinstance(
        logical_key,
        MarketObservationLogicalKey,
    ):
        raise MarketObservationContractError(
            "logical_key must be MarketObservationLogicalKey"
        )

    if not isinstance(
        content_fingerprint,
        MarketObservationContentFingerprint,
    ):
        raise MarketObservationContractError(
            "content_fingerprint must be MarketObservationContentFingerprint"
        )

    fields = (
        (
            "identity_schema_version",
            str(IDENTITY_SCHEMA_VERSION),
        ),
        (
            "instrument_id",
            str(logical_key.instrument_id),
        ),
        (
            "contract_id",
            _CANONICAL_NULL
            if logical_key.contract_id is None
            else str(logical_key.contract_id),
        ),
        (
            "timeframe",
            logical_key.timeframe,
        ),
        (
            "interval_start_at",
            logical_key.interval_start_at_lexical,
        ),
        (
            "content_schema_version",
            str(CONTENT_SCHEMA_VERSION),
        ),
        (
            "content_fingerprint",
            content_fingerprint.value,
        ),
    )

    digest = sha256(
        _frame_bytes(
            _REVISION_FRAME_HEADER,
            fields,
        )
    ).hexdigest()

    return MarketObservationRevisionId(
        f"mor1_{digest}"
    )


__all__ = [
    "CONTENT_SCHEMA_VERSION",
    "IDENTITY_SCHEMA_VERSION",
    "CanonicalMarketObservationContent",
    "MarketObservationContentFingerprint",
    "MarketObservationContractError",
    "MarketObservationLogicalKey",
    "MarketObservationRevisionId",
    "build_market_observation_revision_id",
    "canonicalize_market_observation_content",
    "canonicalize_market_observation_logical_key",
    "normalize_market_observation_timeframe",
]
