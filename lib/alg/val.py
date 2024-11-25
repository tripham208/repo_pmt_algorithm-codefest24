from game.match import PLAYER_ID
from lib.model.dataclass import *
from lib.model.enum.action import FaceAction
from lib.model.enum.gameobjects import StatusPoint
from lib.model.enum.range import BombRange
from lib.utils.map import euclid_distance
from lib.utils.point import get_point_match_step_spoil, get_point_match_step_bomb


def calculate_bombs(base_map: Map, player: Player):
    point = 0
    pos_danger = []
    pos_warning = []
    for bomb in base_map.bombs:
        power = bomb.get("power", 0)

        bomb_range = BombRange[f'LV{power}'].value
        pos_danger += [[bomb["row"], bomb["col"]]]
        is_warning = bomb.get("remainTime", 0) > 1000
        will_destroy = bomb.get("remainTime", 0) < 500
        new = bomb.get("remainTime", 0) == 2000
        dis = 0

        for i in bomb_range:
            for j in i:
                pos = [bomb["row"] + j[0], bomb["col"] + j[1]]
                if base_map.get_obj_map(pos) == 2:
                    if bomb.get("playerId") in PLAYER_ID:
                        if not will_destroy:
                            point += 500
                        if new:
                            dis += euclid_distance(player.position, pos)
                    break
                elif base_map.get_obj_map(pos) in Objects.BOMB_NO_DESTROY.value:
                    break
                if is_warning:
                    pos_warning.append(pos)
                else:
                    pos_danger.append(pos)
        if new:
            point += 1000 - (dis * 100)

    return point, pos_danger, pos_warning

def calculate_hammer(base_map: Map) -> list:
    pos_danger = []
    pos_warning = []
    if base_map.hammers is not None:
        for hammer in base_map.hammers:
            pass
    return pos_danger

def calculate_wind(base_map: Map) -> list:
    pos_danger = []
    if base_map.winds is not None:
        for wind in base_map.winds:
            pass
    return pos_danger


def val(base_map: Map, evaluated_map: EvaluatedMap, locker: Locker,
        player: Player, enemy: Player, player_another: Player, enemy_child: Player, pos_list: list,
        act_list: list) -> int:
    evaluated_map_point = evaluated_map.get_evaluated_map(pos_player=player.position, pos_enemy=enemy.position,
                                                          pos_enemy_child=enemy_child.position,
                                                          pos_player_child=player_another.position)
    value = evaluated_map_point
    value += base_map.up_point
    point, pos_danger, pos_warning = calculate_bombs(base_map, player)
    value += point
    bonus = 0
    bonus_badge = 0  # [[9, 19], [9, 22]]
    if not player.has_transform and base_map.badges is not None:
        for badge in base_map.badges:
            if badge == pos_list[-1]:
                print(len(pos_list))
                bonus_badge = StatusPoint.BADGE.value - ((len(pos_list) - 1) * 400)

    if base_map.bombs:
        if player.position in pos_danger:
            value += StatusPoint.DANGER.value
        if player_another.position in pos_danger:
            value += StatusPoint.DANGER.value
        if player.position in pos_warning:
            value += StatusPoint.WARNING.value
        if player_another.position in pos_warning:
            value += StatusPoint.WARNING.value
        if enemy.has_transform and False:  # todo: unlock bomb enemy
            if (enemy.position in pos_danger or enemy.position in pos_warning) and not enemy.is_stun:
                value += StatusPoint.BOMB_ENEMY.value
            if (enemy_child.position in pos_danger or enemy_child.position in pos_warning) and not enemy_child.is_stun:
                value += StatusPoint.BOMB_ENEMY.value
        else:
            if (enemy.position in pos_danger or enemy.position in pos_warning) and not enemy.is_stun:
                value -= StatusPoint.BOMB_ENEMY.value
            if (enemy_child.position in pos_danger or enemy_child.position in pos_warning) and not enemy_child.is_stun:
                value -= StatusPoint.BOMB_ENEMY.value
        # bonus - optimize step in bomb range
        if pos_list:
            for idx, x in enumerate(pos_list, start=1):
                if x in pos_danger:
                    bonus += get_point_match_step_bomb(idx)
                if x in pos_warning:
                    bonus += get_point_match_step_bomb(idx)/2
    # bonus - optimize step pick spoil

    if pos_list:
        for idx, x in enumerate(pos_list, start=1):
            if x in base_map.get_pos_spoils:
                bonus += get_point_match_step_spoil(idx)
                bonus += 200

    for i in act_list:
        if i in FaceAction.FACES_V2.value:
            bonus -= 100
    value += bonus
    value += bonus_badge
    #print(f"75 val:eval map {evaluated_map_point} base map: {base_map.up_point} bomb: {point} bonus: {bonus} {bonus_badge}", )
    #todo enable god attack
    return value
