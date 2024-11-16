from enum import Enum


# [row,col]

class Face(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class FaceAction(Enum):
    UP = [-1, 0]
    RIGHT = [0, 1]
    DOWN = [1, 0]
    LEFT = [0, -1]


class Action(Enum):
    SWITCH_WEAPON = "SWITCH_WEAPON"
    USE_WEAPON = "USE_WEAPON"
    MARRY_WIFE = "MARRY_WIFE"


class NextMoveZone(Enum):
    Z1 = [[0, 1], [1, 0], [0, -1], [-1, 0]]
    Z2 = [[0, -1], [1, 0], [-1, 0], [0, 1]]
    Z3 = [[0, 1], [-1, 0], [0, -1], [1, 0]]
    Z4 = [[0, -1], [-1, 0], [1, 0], [0, 1]]


class NextActionZone(Enum):
    Z1 = [[1, 1], [0, 1], [1, 0], [0, -1], [-1, 0], [0, 0]]
    Z2 = [[1, 1], [0, -1], [1, 0], [-1, 0], [0, 1], [0, 0]]
    Z3 = [[1, 1], [0, 1], [-1, 0], [0, -1], [1, 0], [0, 0]]
    Z4 = [[1, 1], [0, -1], [-1, 0], [1, 0], [0, 1], [0, 0]]


class Attack(Enum):
    SWITCH_WEAPON = [5, 5]
    WOODEN = [1, 1]
    BOMB = [1, 1]
    GOD_WEAPON = [3, 3]


def get_move_out_zone(region):
    zone_map = {
        1: NextMoveZone.Z1.value,
        2: NextMoveZone.Z2.value,
        3: NextMoveZone.Z3.value,
        4: NextMoveZone.Z4.value
    }
    return zone_map.get(region, NextMoveZone.Z4.value)
