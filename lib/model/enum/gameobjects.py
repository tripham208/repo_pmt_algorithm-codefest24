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
    """

    MAX_BLOCK = [1, 2, 3, 5]
    BFS_BLOCK = [1, 2, 3, 5]
    NO_DESTROY = [1, 5]

    MARRY_ITEM = [32, 33, 34, 35, 36, 37]
    DESTRUCTIBLE = [2, 3]


class Weapon(Enum):
    """
    1:	Wooden pestle \n
    2:	Phach Than (Bomb)

    use god weapon use

    """
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
    TAG_STOP = ["player:stop-moving", "player:moving-banned", "bomb:setup"]


class Time(Enum):
    REMAIN_TIME_LOCK = 600
    TIME_UNLOCK = 300
