import math
from copy import deepcopy

from lib.model.enum.action import FaceAction, Attack


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


def find_index(matrix, target):
    badges = []
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            if value == target:
                badges.append([i, j])
    return badges


def next_pos(start: list, action: list) -> list:
    return [sum(i) for i in zip(start, action)]


def get_face_act_v2(act):
    match act:
        case [-1, 0]:
            return FaceAction.UP_V2.value
        case [0, 1]:
            return FaceAction.RIGHT_V2.value
        case [1, 0]:
            return FaceAction.DOWN_V2.value
        case [0, -1]:
            return FaceAction.LEFT_V2.value


def check_have_attack(act_list) -> bool:
    for act in act_list:
        if act in Attack.ATTACKS.value:
            return True
    return False


def deepcopy_env(base_map, pos_list, act_list):
    return deepcopy(base_map), deepcopy(pos_list), deepcopy(act_list)


def prepare_action(act_list) -> (dict, list):
    info = {
        "attack": [],
        "switch": False,
        "reface": False,
        "god_attack": None,
        "use_god_attack": False,
        "drop": 0,
    }
    for idx, act in enumerate(act_list, start=1):
        match idx, act:
            case _, act if act in FaceAction.FACE_ACTION_V2.value:
                info["reface"] = True
                info["drop"] += 1
                break
            case _, Attack.WOODEN.value:
                info["attack"] = act
                info["drop"] += 1
                if 1 < idx < len(act_list) and not info["reface"] and act_list[idx] == act_list[idx - 2]:
                    break
                else:
                    act_list[idx - 1] = [22, 22]
            case _, Attack.BOMB.value:
                info["attack"] = act
                info["drop"] += 1
            case idx, Attack.HAMMER.value if idx == 1:  # hammer
                info["god_attack"] = act
                info["use_god_attack"] = True
            case _, Attack.HAMMER.value:
                info["god_attack"] = act
                break
            case _, Attack.SWITCH_WEAPON.value:  # switch weapon
                info["switch"] = True
            case _, act if act != [0, 0]:
                info["drop"] += 1
    return info, act_list


def sync_env():
    pass
