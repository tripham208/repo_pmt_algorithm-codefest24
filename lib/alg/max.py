from copy import deepcopy

from game.match import PLAYER_ID
from lib.alg.val import val
from lib.model.dataclass import *
from lib.model.enum.action import get_move_out_zone
from lib.model.enum.point import StatusPoint
from lib.model.enum.range import WeaponRange
from lib.utils.map import is_zone
from lib.utils.printer import pr_red

H = 5
H_NO_ATTACK = 3


def max_val(base_map: Map, evaluated_map: EvaluatedMap, locker: Locker,
            player: Player, enemy: Player, player_another: Player, enemy_child: Player):
    value = StatusPoint.MIN.value

    pos_list = [player.position]
    act_list = []
    acts = get_move_out_zone(is_zone(pos=player.position, size=[base_map.rows, base_map.cols]))

    point, pos, act = get_max_val(actions=acts, base_map=base_map, evaluated_map=evaluated_map, locker=locker,
                                  player=player, enemy=enemy, player_another=player_another, enemy_child=enemy_child,
                                  level=1, pos_list=pos_list,
                                  act_list=act_list)
    if value < point:
        act_list = act

    return act_list


def get_max_val(actions: list, base_map: Map, evaluated_map: EvaluatedMap, locker: Locker,
                player: Player, enemy: Player, player_another: Player, enemy_child: Player, level: int, pos_list,
                act_list
                ) -> tuple[int, list, list]:
    value = StatusPoint.MIN.value
    new_pos_list = []
    new_act_list = []

    try:
        for action in actions:
            if action == [1, 1]:
                if level <= H:  # H_NO_ATTACK
                    point, tmp_act_list, tmp_pos_list = attack_action(actions=actions, base_map=base_map,
                                                                      evaluated_map=evaluated_map, locker=locker,
                                                                      player=player, enemy=enemy,
                                                                      player_another=player_another,
                                                                      enemy_child=enemy_child, level=1,
                                                                      pos_list=pos_list,
                                                                      act_list=act_list)
                    if value < point:
                        value = point
                        new_pos_list = tmp_act_list
                        new_act_list = tmp_pos_list

            elif action == [0, 0]:
                point = val(base_map=base_map, evaluated_map=evaluated_map, locker=locker,
                            player=player, enemy=enemy, player_another=player_another, enemy_child=enemy_child,
                            pos_list=pos_list)
                if value < point:
                    value = point
                    new_pos_list = deepcopy(pos_list)
                    new_act_list = deepcopy(act_list)
                    new_act_list.append(action)
            else:
                point, tmp_act_list, tmp_pos_list = move_action(actions=actions, base_map=base_map,
                                                                evaluated_map=evaluated_map, locker=locker,
                                                                player=player, enemy=enemy,
                                                                player_another=player_another,
                                                                enemy_child=enemy_child, level=1,
                                                                pos_list=pos_list,
                                                                act_list=act_list, current_action=action)
                if value < point:
                    value = point
                    new_pos_list = tmp_act_list
                    new_act_list = tmp_pos_list

    except Exception as e:
        pr_red(e)
    finally:
        return value, new_act_list, new_pos_list


def gen_bomb(player: Player):
    return {
        {
            "row": player.position[0],
            "col": player.position[1],
            "playerId": PLAYER_ID,
            "power": player.power,
            "remainTime": 2000
        }
    }


def attack_action(actions: list, base_map: Map, evaluated_map: EvaluatedMap, locker: Locker,
                  player: Player, enemy: Player, player_another: Player, enemy_child: Player, level: int,
                  pos_list: list, act_list: list
                  ) -> tuple[int, list, list]:
    if level == H:
        return StatusPoint.MIN.value, pos_list, act_list
    cur_weapon = player.cur_weapon

    value = StatusPoint.MIN.value
    new_pos_list = pos_list
    new_act_list = act_list

    if cur_weapon == 1:
        for pos_atk in WeaponRange.WOODEN.value:
            pos_w_atk = [sum(i) for i in zip(player.position, pos_atk)]
            if base_map.get_obj_map(pos_w_atk) == 3:
                new_base_map = deepcopy(base_map)
                new_player = deepcopy(player)
                new_pos_list = deepcopy(pos_list)
                new_act_list = deepcopy(act_list)

                new_base_map.set_val_map(pos_w_atk, 0)
                new_base_map.up_point += 100

                #new_pos_list.append(new_player.position)
                new_act_list += [pos_atk, [1, 1]]

                point, tmp_act_list, tmp_pos_list = get_max_val(actions=actions, base_map=new_base_map,
                                                                evaluated_map=evaluated_map, locker=locker,
                                                                player=new_player, enemy=enemy,
                                                                player_another=player_another, enemy_child=enemy_child,
                                                                level=level + 1,
                                                                pos_list=new_pos_list,
                                                                act_list=new_act_list)
                if value < point:
                    value = point
                    new_pos_list = tmp_act_list
                    new_act_list = tmp_pos_list

        if player.has_bomb:
            new_base_map = deepcopy(base_map)
            new_player = deepcopy(player)
            new_pos_list = deepcopy(pos_list)
            new_act_list = deepcopy(act_list)

            new_player.has_bomb = False
            new_base_map.bombs.append(gen_bomb(new_player))

            #new_pos_list.append(new_player.position)
            new_act_list += [[5, 5], [1, 1]]

            point, tmp_act_list, tmp_pos_list = get_max_val(actions=actions, base_map=new_base_map,
                                                            evaluated_map=evaluated_map, locker=locker,
                                                            player=new_player, enemy=enemy,
                                                            player_another=player_another, enemy_child=enemy_child,
                                                            level=level + 1,
                                                            pos_list=new_pos_list,
                                                            act_list=new_act_list)
            if value < point:
                value = point
                new_pos_list = tmp_act_list
                new_act_list = tmp_pos_list

    if cur_weapon == 2:
        if player.has_bomb:
            new_base_map = deepcopy(base_map)
            new_player = deepcopy(player)
            new_pos_list = deepcopy(pos_list)
            new_act_list = deepcopy(act_list)

            new_player.has_bomb = False
            new_base_map.bombs.append(gen_bomb(new_player))

            new_pos_list.append(new_player.position)
            new_act_list.append([1, 1])

            point, tmp_act_list, tmp_pos_list = get_max_val(actions=actions, base_map=new_base_map,
                                                            evaluated_map=evaluated_map, locker=locker,
                                                            player=new_player, enemy=enemy,
                                                            player_another=player_another, enemy_child=enemy_child,
                                                            level=level + 1,
                                                            pos_list=new_pos_list,
                                                            act_list=new_act_list)
            if value < point:
                value = point
                new_pos_list = tmp_act_list
                new_act_list = tmp_pos_list
        # switch weapon
        for pos_atk in WeaponRange.WOODEN.value:
            pos_w_atk = [sum(i) for i in zip(player.position, pos_atk)]
            if base_map.get_obj_map(pos_w_atk) == 3:
                new_base_map = deepcopy(base_map)
                new_player = deepcopy(player)
                new_pos_list = deepcopy(pos_list)
                new_act_list = deepcopy(act_list)

                new_base_map.set_val_map(pos_w_atk, 0)
                new_base_map.up_point += 100

                new_pos_list.append(new_player.position)
                new_act_list += [[5, 5], pos_atk, [1, 1]]

                new_player.cur_weapon = 1

                point, tmp_act_list, tmp_pos_list = get_max_val(actions=actions, base_map=new_base_map,
                                                                evaluated_map=evaluated_map, locker=locker,
                                                                player=new_player, enemy=enemy,
                                                                player_another=player_another, enemy_child=enemy_child,
                                                                level=level + 1,
                                                                pos_list=new_pos_list,
                                                                act_list=new_act_list)
                if value < point:
                    value = point
                    new_pos_list = tmp_act_list
                    new_act_list = tmp_pos_list

    return value, new_act_list, new_pos_list


def can_go_new_pos(new_pos_player, base_map: Map, locker: Locker) -> bool:
    if (new_pos_player in locker.danger_pos_lock_max
            or new_pos_player in locker.pos_lock
            or base_map.map[new_pos_player[0]][new_pos_player[1]] in Objects.MAX_BLOCK.value
    ):
        return False
    return True


def move_action(actions: list, base_map: Map, evaluated_map: EvaluatedMap, locker: Locker,
                player: Player, enemy: Player, player_another: Player, enemy_child: Player, level: int, pos_list,
                act_list, current_action
                ) -> tuple[int, list, list]:
    new_pos_player = [sum(i) for i in zip(player.position, current_action)]

    if (not can_go_new_pos(new_pos_player, base_map, locker)
            or new_pos_player in pos_list):
        return StatusPoint.MIN.value, pos_list, act_list

    new_player = deepcopy(player)
    new_pos_list = deepcopy(pos_list)
    new_act_list = deepcopy(act_list)

    new_player.position = new_pos_player
    new_act_list.append(current_action)
    new_pos_list.append(new_pos_player)

    if level != H:
        return get_max_val(actions=actions, base_map=base_map, evaluated_map=evaluated_map, locker=locker,
                           player=new_player, enemy=enemy, player_another=player_another, enemy_child=enemy_child
                           , level=level + 1,
                           pos_list=new_pos_list,
                           act_list=new_act_list)
    else:
        point = val(base_map=base_map, evaluated_map=evaluated_map, locker=locker,
                    player=player, enemy=enemy, player_another=player_another, enemy_child=enemy_child
                    , pos_list=pos_list)
        return point, new_pos_list, new_act_list
