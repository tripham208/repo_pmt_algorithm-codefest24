from enum import Enum


class Objects(Enum):
    """
    0 - A Road \n
    1 - A Wall (None destructible cell)\n
    2 - A Balk (Destructible cell)\n
    3 - A Brick Wall (Destructible cell by wooden pestle weapon)\n
    5 - A Prison Place \n
    6 - God Badge (used to turn the character into a God)\n

    11 - Bomb \n

    32 - STICKY RICE\n
    33 - Chung Cake\n
    34 - Nine Tusk Elephant\n
    35 - Nine Spur Rooster\n
    36 - Nine Mane Hair Horse\n
    37 - Holy Spirit Stone\n

    custom map\n
    100 : point destructible\n
    """

    MAX_BLOCK = [1, 2, 3, 5]
    BFS_BLOCK = [1, 2, 3, 5]
    NO_DESTROY = [1, 5]
    BOMB_NO_DESTROY = [1, 3, 5]
    BOMB_BREAK = [1, 2, 3, 5]

    A_STAR_PHASE1_LOCK = [1, 2, 5]
    A_STAR_PHASE2_LOCK = [1, 5]
    A_STAR_ENEMY_LOCK = [1, 2, 3, 5]

    MARRY_ITEM = [32, 33, 34, 35, 36]
    DESTRUCTIBLE = [2, 3]
    DESTRUCTIBLE_PHASE1 = [3]
    DESTRUCTIBLE_PHASE2 = [2]

    BALK = 2
    BRICK_WALL = 3

    MOUNTAIN_GOD = 1
    WATER_GOD = 2


class StatusPoint(Enum):
    MIN = -10000000
    # behavior
    PENALTY = -5000

    # position
    BADGE = 2000
    DANGER = -10000
    WARNING = -2000

    # object
    BRICK_WALL = 300
    BALK = 1000

    # bonus
    BOMB_ENEMY = 3000
    GOD_ENEMY = 4000


class Weapon(Enum):
    """
    1:	Wooden pestle \n
    2:	Phach Than (Bomb)

    use god weapon use

    """
    NO = 0
    WOODEN = 1
    BOMB = 2
    HAMMER = 3
    WIND = 4


class MarryItem(Enum):
    RICE = 32
    CAKE = 33
    ELEPHANT = 34
    ROOSTER = 35
    HORSE = 36


class AnotherItem(Enum):
    GOD_BADGE = 6
    SPIRIT_STONE = 37


class Tag(Enum):
    TAG_STOP = [
        "player:stop-moving",
        "bomb:setup",
        "wooden-pestle:setup",
        "player:moving-banned",
    ]

    TAG_REPLAY = [
        "player:outto-wedding-room",
        "player:back-to-playground",
        "player:stun-timeout"
    ]

    BACKLOG = [
        "player:into-wedding-room",
        "bomb:exploded",
        "player:switched-weapon",
        "player:stun-by-weapon",
        "player:transformed"
    ]


class Time(Enum):
    REMAIN_TIME_LOCK = 600
    TIME_UNLOCK = 300

    DELAY = 2000  # TIME basic attack

    HAMMER = 10000
    WIND = 5000

    WOODEN = 2000


class Cell(Enum):
    """
    size cell on map
    """

    TRAINING = 35
    FIGHTING = 55
