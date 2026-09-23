from enum import Enum


class DecisionAction(str, Enum):
    HOLD = "HOLD"
    ADD = "ADD"
    REDUCE = "REDUCE"
    EXIT = "EXIT"
    ENTER = "ENTER"
