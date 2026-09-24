from __future__ import annotations

from enum import Enum


class DirectionChangeState(str, Enum):
    NO_CHANGE = "NO_CHANGE"
    EXIT_REQUIRED = "EXIT_REQUIRED"
    WAITING_FOR_FLAT = "WAITING_FOR_FLAT"
    RE_EVALUATE = "RE_EVALUATE"
    ENTER_NEW_DIRECTION = "ENTER_NEW_DIRECTION"
