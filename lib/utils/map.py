import math


def create_map_zero(cols: int, rows: int):
    return [[0] * cols for _ in range(rows)]


def euclid_distance(start: list, target: list) -> float:
    return round(math.sqrt((start[0] - target[0]) ** 2 + (start[1] - target[1]) ** 2), 2)


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


def dif_distance_with_target(pos_player: list, pos_enemy: list, target: list) -> float:
    player_distance = euclid_distance(pos_player, target)
    enemy_distance = euclid_distance(pos_enemy, target)
    return round(enemy_distance - player_distance, 2)
