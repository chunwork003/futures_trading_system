from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from backtest.risk import RiskConfig


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class SignalAction(str, Enum):
    ENTER = "ENTER"
    EXIT = "EXIT"
    REVERSE = "REVERSE"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class PositionStatus(str, Enum):
    FLAT = "FLAT"
    LONG = "LONG"
    SHORT = "SHORT"


class ExitReason(str, Enum):
    SL = "SL"
    TP = "TP"
    TRAILING = "TRAILING"
    TIME = "TIME"
    SIGNAL = "SIGNAL"
    END_OF_DATA = "END_OF_DATA"
    MANUAL = "MANUAL"
    FORCED_LIQUIDATION = "FORCED_LIQUIDATION"


class Signal(BaseModel):
    signal_id: str
    timestamp: datetime
    trade_date: date
    symbol: str
    contract: Optional[str] = None
    timeframe: str

    strategy_id: str
    strategy_version: str

    action: SignalAction = SignalAction.ENTER
    direction: Direction

    market_state: Optional[str] = None
    setup: Optional[str] = None
    entry_type: Optional[str] = None

    entry_price: float
    stop_price: Optional[float] = None
    target_price: Optional[float] = None

    quantity: int = Field(default=1, gt=0)
    confidence: Optional[float] = None


class Order(BaseModel):
    order_id: str
    signal_id: str
    timestamp: datetime
    symbol: str
    contract: Optional[str] = None

    direction: Direction
    order_type: OrderType

    quantity: int = Field(gt=0)

    requested_price: Optional[float] = None
    fill_price: Optional[float] = None

    status: OrderStatus = OrderStatus.PENDING

    slippage_points: float = Field(default=0.0, ge=0)
    commission: float = Field(default=0.0, ge=0)


class Fill(BaseModel):
    order_id: str
    timestamp: datetime

    requested_price: float
    price: float

    quantity: int = Field(gt=0)

    commission: float = Field(default=0.0, ge=0)
    slippage_points: float = Field(default=0.0, ge=0)


class Position(BaseModel):
    signal_id: str
    symbol: str
    contract: Optional[str] = None

    strategy_id: str
    strategy_version: str

    market_state: Optional[str] = None
    setup: Optional[str] = None
    entry_type: Optional[str] = None

    direction: Direction
    status: PositionStatus

    quantity: int = Field(gt=0)

    entry_time: datetime
    entry_price: float

    entry_requested_price: Optional[float] = None
    entry_commission: float = Field(default=0.0, ge=0)
    entry_slippage_points: float = Field(default=0.0, ge=0)

    stop_price: Optional[float] = None
    target_price: Optional[float] = None

    highest_price: Optional[float] = None
    lowest_price: Optional[float] = None

    unrealized_pnl: float = 0.0


class Trade(BaseModel):
    trade_id: str
    signal_id: str
    trade_date: date
    symbol: str
    contract: Optional[str] = None
    timeframe: str

    strategy_id: str
    strategy_version: str

    market_state: Optional[str] = None
    setup: Optional[str] = None
    entry_type: Optional[str] = None

    direction: Direction

    entry_time: datetime
    exit_time: datetime

    entry_price: float
    exit_price: float

    stop_price: Optional[float] = None
    target_price: Optional[float] = None

    quantity: int = Field(gt=0)

    gross_pnl: float
    commission: float = 0.0
    slippage_cost: float = 0.0
    net_pnl: float

    risk_points: Optional[float] = None
    pnl_points: Optional[float] = None
    r_multiple: Optional[float] = None

    mae_points: Optional[float] = None
    mfe_points: Optional[float] = None

    holding_minutes: Optional[float] = None

    exit_reason: ExitReason
    result: str


class BacktestConfig(BaseModel):
    initial_capital: float = Field(default=1_000_000, gt=0)

    symbol: str
    timeframe: str = "1m"

    quantity: int = Field(default=1, gt=0)
    multiplier: float = Field(default=200, gt=0)

    commission_per_contract: float = Field(default=0.0, ge=0)
    slippage_points: float = Field(default=0.0, ge=0)

    allow_multiple_positions: bool = False

    intrabar_priority: str = "SL_FIRST"

    end_of_data_exit: bool = True

    risk_config: Optional[RiskConfig] = None
