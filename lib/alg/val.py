from game.match import PLAYER_ID
from lib.model.dataclass import *
from lib.model.enum.action import FaceAction
from lib.model.enum.point import StatusPoint
from lib.model.enum.range import BombRange
from lib.utils.point import get_point_match_step_spoil, get_point_match_step_bomb


def calculate_bombs(base_map: Map):
    point = 0
    pos_danger = []
    pos_warning = []
    for bomb in base_map.bombs:
        power = bomb.get("power", 0)
        bomb_range = BombRange[f'LV{power}'].value
        pos_danger += [[bomb["row"], bomb["col"]]]
        is_warning = bomb.get("remainTime", 0) > 1000

        for i in bomb_range:
            for j in i:
                pos = [[bomb["row"] + j[0]], [bomb["col"] + j[1]]]
                if base_map.get_obj_map(pos) == 2:
                    if bomb.get("playerId") in PLAYER_ID:
                        point += 500
                    break
                elif base_map.get_obj_map(pos) in Objects.BOMB_NO_DESTROY.value:
                    break
                if is_warning:
                    pos_warning.append(pos)
                else:
                    pos_danger.append(pos)

    return point, pos_danger, pos_warning


def val(base_map: Map, evaluated_map: EvaluatedMap, locker: Locker,
        player: Player, enemy: Player, player_another: Player, enemy_child: Player, pos_list, act_list) -> int:
    value = evaluated_map.get_evaluated_map(pos_player=player.position, pos_enemy=enemy.position,
                                            pos_enemy_child=enemy_child.position,
                                            pos_player_child=player_another.position)
    value += base_map.up_point
    point, pos_danger, pos_warning = calculate_bombs(base_map)
    value += point
    if base_map.bombs:
        if player.position in pos_danger:
            value += StatusPoint.DANGER.value
        if player_another.position in pos_danger:
            value += StatusPoint.DANGER.value
        if player.position in pos_warning:
            value += StatusPoint.WARNING.value
        if player_another.position in pos_warning:
            value += StatusPoint.WARNING.value
        if (enemy.position in pos_danger or enemy.position in pos_warning) and not enemy.is_tsun:
            value += 1000
        if (enemy_child.position in pos_danger or enemy_child.position in pos_warning) and not enemy_child.is_tsun:
            value += 1000
        # bonus - optimize step in bomb range
        if pos_list:
            for idx, x in enumerate(pos_list, start=1):
                if x in pos_danger:
                    value += get_point_match_step_bomb(idx)
    # bonus - optimize step pick spoil
    if pos_list:
        for idx, x in enumerate(pos_list, start=1):
            if x in base_map.get_pos_spoils:
                value += get_point_match_step_spoil(idx)
                value += 200
    for i in act_list:
        if i in FaceAction.FACES_V2.value:
            value -= 100

    return value
