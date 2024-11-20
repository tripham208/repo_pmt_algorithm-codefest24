from enum import Enum


class StatusPoint(Enum):
    MIN = -10000000
    DANGER = -10000
    WARNING = -1000
    DESTROY = 500
    PENALTY = -5000
    BADGE = 500
