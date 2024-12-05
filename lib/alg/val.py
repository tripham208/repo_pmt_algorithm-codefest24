from game.match import PLAYER_ID
from lib.model.dataclass import *
from lib.model.enum.action import FaceAction, Action
from lib.model.enum.gameobjects import StatusPoint
from lib.model.enum.range import BombRange
from lib.utils.map import euclid_distance
from lib.utils.point import get_point_match_step_spoil, get_point_match_step_bomb


def gen_bomb(player: Player):
    return {
        "row": player.position[0],
        "col": player.position[1],
        "playerId": PLAYER_ID,
        "power": player.power,
        "remainTime": 2000,
    }


def gen_hammer(pos):
    return {
        "destination": {
            "col": pos[1],
            "row": pos[0],
        }
    }


def is_not_in_corner(pos, pos_danger: list, base_map: Map) -> bool:
    for action in Action.MOVE.value:
        fake_position = [sum(i) for i in zip(pos, action)]
        if fake_position not in pos_danger and base_map.get_obj_map(fake_position) == 0:
            return True
    return False


def calculate_bombs(base_map: Map, player: Player):
    point = 0
    pos_danger = []
    pos_warning = []
    pos_all = []
    for bomb in base_map.bombs:
        power = bomb.get("power", 0)

        bomb_range = BombRange[f'LV{power}'].value
        pos_danger += [[bomb["row"], bomb["col"]]]  # todo neu impl tu sat
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
                            dis += euclid_distance(player.position, pos) # bonus near pos will des
                    break
                elif base_map.get_obj_map(pos) in Objects.BOMB_NO_DESTROY.value:
                    break
                if is_warning:
                    pos_warning.append(pos)
                else:
                    pos_danger.append(pos)
                pos_all.append(pos)
        if new:
            point += 1000 - (dis * 100)

    return point, pos_danger, pos_warning, pos_all


def check_spoil_near(base_map: Map, player: Player) -> int:
    spoil_near = 0
    for spoil in base_map.get_pos_spoils:
        if euclid_distance(player.position, spoil) < 3:
            spoil_near += 1
    return spoil_near


def calculate_pos_ally(player: Player, another_player: Player) -> int:
    point = 0
    dis = euclid_distance(player.position, another_player.position)
    if dis <= 3:
        point = -1000
    elif dis <= 5:
        point = -500
    elif dis <= 7:
        point = -100

    return point


def calculate_pos_enemy(base_map: Map, player: Player, enemy: Player, enemy_child: Player) -> int:
    pass


def val(base_map: Map, evaluated_map: EvaluatedMap, locker: Locker,
        player: Player, enemy: Player, player_another: Player, enemy_child: Player, pos_list: list,
        act_list: list) -> int:
    evaluated_map_point = evaluated_map.get_evaluated_map(pos_player=player.position, pos_enemy=enemy.position,
                                                          pos_enemy_child=enemy_child.position,
                                                          pos_player_child=player_another.position)
    value = evaluated_map_point
    value += base_map.up_point
    point, pos_danger, pos_warning, pos_all = calculate_bombs(base_map, player)
    value += point
    bonus = 0
    bonus_badge = 0  # [[9, 19], [9, 22]]
    deny_bomb = 0
    if not player.has_transform and base_map.badges is not None:
        for badge in base_map.badges:
            if badge == pos_list[-1]:
                print(len(pos_list))
                bonus_badge = StatusPoint.BADGE.value - ((len(pos_list) - 1) * 400)
    # print(player)
    # print(value)
    # print(pos_danger)
    # print(pos_warning)
    if base_map.bombs:
        if player.position in pos_danger:
            value += StatusPoint.DANGER.value
        if player_another.position in pos_danger:
            value += StatusPoint.DANGER.value
        if player.position in pos_warning:
            value += StatusPoint.WARNING.value
        if player_another.position in pos_warning:
            value += StatusPoint.DANGER.value
        if enemy.has_transform:  # todo: unlock bomb enemy
            if enemy.position in pos_danger or enemy.position in pos_warning:
                value += StatusPoint.BOMB_ENEMY.value
            if enemy_child.position in pos_danger or enemy_child.position in pos_warning:
                value += StatusPoint.BOMB_ENEMY.value
        else:
            if enemy.position in pos_danger or enemy.position in pos_warning:
                value -= StatusPoint.BOMB_ENEMY.value
        # bonus - optimize step in bomb range

        if pos_list:
            for idx, x in enumerate(pos_list, start=1):
                if x in pos_danger:
                    deny_bomb += get_point_match_step_bomb(idx)
                if x in pos_warning:
                    deny_bomb += get_point_match_step_bomb(idx) / 2
    # bonus - optimize step pick spoil

    if pos_list:
        for idx, x in enumerate(pos_list, start=1):
            if x in base_map.get_pos_spoils:
                bonus += get_point_match_step_spoil(idx)
                bonus += 200

    bonus += check_spoil_near(base_map, player) * 100

    for i in act_list:
        if i in FaceAction.FACE_ACTION_V2.value:
            bonus -= 200
    value += bonus
    value += bonus_badge # badge
    value += deny_bomb # work in bomb
    value += calculate_pos_ally(player, player_another)
    if value > 100:
        value += 100 - len(act_list) * 10 # len step

    if not is_not_in_corner(player.position, pos_all, base_map):
        value -= 1000
    # if player_another.position != [0, 0]:
    #     if calculate_pos(player_another.position, pos_danger, base_map):
    #         value -= 500

    god_pos = base_map.get_pos_hammers
    god_pos += base_map.get_pos_winds
    # print(god_pos)
    if player.position in god_pos:
        value += StatusPoint.DANGER.value
    if player_another.position in god_pos:
        value += StatusPoint.DANGER.value
    if enemy.has_transform:
        if enemy.position in god_pos:
            value += StatusPoint.GOD_ENEMY.value
        if enemy_child.position in god_pos:
            value += StatusPoint.GOD_ENEMY.value
    else:
        if enemy.position in god_pos:
            value -= StatusPoint.BOMB_ENEMY.value
        if enemy_child.position in god_pos:
            value -= StatusPoint.BOMB_ENEMY.value

    # print(f"75 val:eval map {evaluated_map_point} base map: {base_map.up_point} bomb: {point} bonus: {bonus} badge {bonus_badge} deny_bomb {deny_bomb} => {value}")

    return value
