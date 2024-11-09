import math


def create_map_zero(cols: int, rows: int):
    return [[0] * cols for _ in range(rows)]


def euclid_distance(start: list, target: list) -> float:
    return math.sqrt((start[0] - target[0]) ** 2 + (start[1] - target[1]) ** 2)


def is_zone(pos: list, size: list) -> int:
    """

    :param pos:
    :param size:
    :return: zone     1,2 /3,4
    """
    p1, p2 = size[0] // 2, size[1] // 2

    if pos[0] < p1:
        return 1 if pos[1] < p2 else 2
    else:
        return 3 if pos[1] < p2 else 4
