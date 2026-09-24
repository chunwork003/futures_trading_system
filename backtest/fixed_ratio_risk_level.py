from enum import Enum


class FixedRatioRiskLevel(str, Enum):
    NORMAL = "NORMAL"
    LEVEL_1 = "LEVEL_1"
    LEVEL_2 = "LEVEL_2"
    LEVEL_3 = "LEVEL_3"
