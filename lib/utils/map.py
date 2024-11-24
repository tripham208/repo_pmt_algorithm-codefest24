import math

from lib.model.enum.action import Face, FaceAction, Attack


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


def get_face(old, new):
    if old[0] == new[0]:
        if old[1] > new[1]:
            return Face.LEFT.value
        elif old[1] < new[1]:
            return Face.RIGHT.value
        else:
            return Face.UNKNOWN.value
    elif old[1] == new[1]:
        if old[0] > new[0]:
            return Face.UP.value
        elif old[0] < new[0]:
            return Face.DOWN.value


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


def get_info_action(act_list) -> dict:
    output = {
        "attack": [],
        "switch": False,
        "reface": False,
        "god_attack": [],
    }
    index = 0
    for act in act_list:
        if act in FaceAction.FACES_V2.value:
            output["reface"] = True
            index += 1
            break
        if act in Attack.BASIC_ATTACKS.value:
            output["attack"] = act
            index += 1
        elif act == Attack.SWITCH_WEAPON.value:
            output["switch"] = True
        elif len(act) > 2:
            pass
        elif act != [0, 0]:
            index += 1
    output["drop"] = index
    return output

