from copy import deepcopy

from game.match import PLAYER_ID
from lib.alg.astar import a_star_optimized
from lib.model.dataclass import *
from lib.model.enum.action import FaceAction, Action
from lib.model.enum.gameobjects import StatusPoint
from lib.model.enum.range import BombRange
from lib.utils.map import euclid_distance, next_pos
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


def is_in_corner(pos, pos_danger: list, base_map: Map) -> bool:
    for action in Action.MOVE.value:
        fake_position = next_pos(pos, action)
        if fake_position not in pos_danger and base_map.get_obj_map(fake_position) == 0:
            return False
    return True


def calculate_bombs(base_map: Map, player: Player, locker: Locker, share_env: ShareEnv):
    point = 0
    pos_dict = base_map.get_pos_bomb
    # todo neu impl tu sat
    for bomb in base_map.bombs:

        new = bomb.get("remainTime", 0) == 2000
        if not new:
            continue

        power = bomb.get("power", 0)
        bomb_range = BombRange[f'LV{power}'].value
        bomb_pos = [bomb["row"], bomb["col"]]
        pos_dict["danger"].append(bomb_pos)
        dis = 0

        for i in bomb_range:
            for j in i:
                pos = [bomb["row"] + j[0], bomb["col"] + j[1]]
                if base_map.get_obj_map(pos) == 2:
                    if bomb.get("playerId")[0:10] in PLAYER_ID:  # todo impl 2 player ko bomb cung ô
                        if pos not in share_env.targeted_boxes:
                            pos_dict["destroy"].append(pos)
                            point += StatusPoint.BALK.value
                            dis += euclid_distance(player.position, pos)  # bonus near pos will des
                    break
                elif base_map.get_obj_map(pos) in Objects.BOMB_NO_DESTROY.value:
                    break
                pos_dict["new"].append(pos)
                pos_dict["all"].append(pos)
        point += 1000 - (dis * 100)
        if player.position in pos_dict["new"]:
            point -= 500 - (euclid_distance(player.position, bomb_pos) * 100)

    return point, pos_dict


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
    elif dis <= 0:
        point = -500
    elif dis <= 0:
        point = -100

    return point


def calculate_pos_enemy(base_map: Map, evaluated_map: EvaluatedMap, locker: Locker, player: Player, enemy: Player,
                        enemy_child: Player) -> int:
    if not player.is_child:
        locker = deepcopy(locker)
        locker.a_star_lock = Objects.A_STAR_ENEMY_LOCK.value
        if euclid_distance(player.position, enemy.position) < 7:
            act_list, pos_list = a_star_optimized(
                start=player.position, locker=locker, base_map=base_map, target=enemy.position
            )
            if len(act_list) > 10 or len(pos_list) == 0:
                return 200
            else:
                return - 200
    return 0


def val(base_map: Map, evaluated_map: EvaluatedMap, locker: Locker,
        player: Player, enemy: Player, player_another: Player, enemy_child: Player,
        pos_list: list, act_list: list, share_env: ShareEnv):
    evaluated_map_point = evaluated_map.get_evaluated_map(pos_player=player.position, pos_enemy=enemy.position,
                                                          pos_enemy_child=enemy_child.position)
    value = evaluated_map_point
    value += base_map.up_point
    point, pos_dict = calculate_bombs(base_map, player, locker, share_env)
    value += point
    bonus = 0
    bonus_badge = 0  # [[9, 19], [9, 22]]
    deny_bomb = 0
    if not player.has_transform and base_map.badges is not None:
        for badge in base_map.badges:
            if badge == pos_list[-1]:
                bonus_badge = StatusPoint.BADGE.value - ((len(pos_list) - 1) * 400)
    # print(player)
    # print(value)
    # print(pos_danger)
    # print(pos_warning)
    if base_map.bombs:
        if player.position in pos_dict["danger"]:
            value += StatusPoint.DANGER.value
        if player_another.position in pos_dict["danger"]:
            value += StatusPoint.DANGER.value
        if player.position in pos_dict["warning"]:
            value += StatusPoint.WARNING.value
        if player_another.position in pos_dict["warning"]:
            value += StatusPoint.DANGER.value
        if enemy.has_transform and False:  # todo: unlock bomb enemy
            if enemy.position in pos_dict["all"]:
                value += StatusPoint.BOMB_ENEMY.value
            if enemy_child.position in pos_dict["all"]:
                value += StatusPoint.BOMB_ENEMY.value
        else:
            if enemy.position in pos_dict["all"]:
                value -= StatusPoint.BOMB_ENEMY.value
        # bonus - optimize step in bomb range

        if pos_list:
            for idx, x in enumerate(pos_list, start=1):
                if x in pos_dict["danger"]:  # - by bomb pos
                    deny_bomb += get_point_match_step_bomb(idx)
                if x in pos_dict["warning"] and x not in pos_dict["new"]:
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
    value += bonus_badge  # badge
    value += deny_bomb  # work in bomb
    # value += calculate_pos_ally(player, player_another) #TODO : distance 2 bot
    # todo check
    # if enemy.transform_type == 2 and (player.transform_type == 1 or player_another.transform_type == 1):
    #     value += calculate_pos_enemy(base_map, evaluated_map, locker, player, enemy, enemy_child)
    #     print("180 enable")
    if value > 500:
        value += 100 - len(act_list) * 10  # len step

    if is_in_corner(player.position, pos_dict["all"], base_map):
        value -= 750
    if (
            euclid_distance(player.position, player_another.position) <= 3
            and player_another.position != [0, 0]
            and not is_in_corner(player_another.position, pos_dict["all"], base_map)
    ):
        value -= 500
    # if player_another.position != [0, 0]:
    #     if calculate_pos(player_another.position, pos_danger, base_map):
    #         value -= 500

    god_pos = base_map.get_pos_god_weapon
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

    print(f"75 val:eval map {evaluated_map_point} base map: {base_map.up_point} bomb: {point} bonus: {bonus} badge {bonus_badge} deny_bomb {deny_bomb} => {value}")

    return value, pos_dict["destroy"]
