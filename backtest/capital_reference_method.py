from enum import Enum


class CapitalReferenceMethod(str, Enum):
    INITIAL = "INITIAL"
    MOVING_PEAK = "MOVING_PEAK"
    MOVING_AVERAGE = "MOVING_AVERAGE"
    PREVIOUS_PERIOD = "PREVIOUS_PERIOD"
