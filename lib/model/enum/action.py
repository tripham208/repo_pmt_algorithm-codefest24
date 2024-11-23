from enum import Enum


# [row,col]

class Face(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    UNKNOWN = 0


class FaceAction(Enum):
    UP = [-1, 0]
    RIGHT = [0, 1]
    DOWN = [1, 0]
    LEFT = [0, -1]
    UP_V2 = [-10, 0]
    RIGHT_V2 = [0, 10]
    DOWN_V2 = [10, 0]
    LEFT_V2 = [0, -10]
    FACES = [[], UP, DOWN, LEFT, RIGHT]
    FACES_V2 = [[], UP_V2, DOWN_V2, LEFT_V2, RIGHT_V2]


class Action(Enum):
    SWITCH_WEAPON = "switch weapon"
    USE_WEAPON = "use weapon"
    MARRY_WIFE = "marry wife"


class NextMoveZone(Enum):
    Z1 = [[0, 1], [1, 0], [0, -1], [-1, 0]]
    Z2 = [[0, -1], [1, 0], [-1, 0], [0, 1]]
    Z3 = [[0, 1], [-1, 0], [0, -1], [1, 0]]
    Z4 = [[0, -1], [-1, 0], [1, 0], [0, 1]]


class NextActionZone(Enum):
    Z1 = [[1, 1], [0, 0], [0, 1], [1, 0], [0, -1], [-1, 0]]
    Z2 = [[1, 1], [0, -1], [1, 0], [-1, 0], [0, 1], [0, 0]]
    Z3 = [[1, 1], [0, 1], [-1, 0], [0, -1], [1, 0], [0, 0]]
    Z4 = [[1, 1], [0, -1], [-1, 0], [1, 0], [0, 1], [0, 0]]


class Attack(Enum):
    WOODEN = [2, 2]
    BOMB = [3, 3]
    HAMMER = [4, 4]
    WIND = [5, 5]
    SWITCH_WEAPON = [6, 6]

    ATTACKS = [WOODEN, BOMB, HAMMER, WIND, SWITCH_WEAPON]
    BASIC_ATTACKS = [WOODEN, BOMB]
    BASIC_ATTACKS_WITH_CHANGE = [WOODEN, BOMB, SWITCH_WEAPON]
    GOD_ATTACKS = [HAMMER, WIND]


def get_move_out_zone(region):
    zone_map = {
        1: NextMoveZone.Z1.value,
        2: NextMoveZone.Z2.value,
        3: NextMoveZone.Z3.value,
        4: NextMoveZone.Z4.value
    }
    return zone_map.get(region, NextMoveZone.Z4.value)


def get_action_zone(region):
    '''
    zone_map = {
        1: NextActionZone.Z1.value,
        2: NextActionZone.Z2.value,
        3: NextActionZone.Z3.value,
        4: NextActionZone.Z4.value
    }
    return zone_map.get(region, NextActionZone.Z4.value)
    '''
    return NextActionZone.Z1.value
