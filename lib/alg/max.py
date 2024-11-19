from copy import deepcopy

from game.match import PLAYER_ID
from lib.alg.val import val
from lib.model.dataclass import *
from lib.model.enum.action import get_action_zone, Face, FaceAction, Attack
from lib.model.enum.point import StatusPoint
from lib.model.enum.range import WeaponRange
from lib.utils.map import is_zone, get_face, get_face_act_v2
from lib.utils.printer import pr_red, pr_green

H = 5
H_NO_ATTACK_BOMB = 3


def max_val(base_map: Map, evaluated_map: EvaluatedMap, locker: Locker,
            player: Player, enemy: Player, player_another: Player, enemy_child: Player):
    value = StatusPoint.MIN.value

    pos_list = [player.position]
    act_list = []
    acts = get_action_zone(is_zone(pos=player.position, size=[base_map.rows, base_map.cols]))  # change

    point, act, pos = get_max_val(actions=acts, base_map=base_map, evaluated_map=evaluated_map, locker=locker,
                                  player=player, enemy=enemy, player_another=player_another, enemy_child=enemy_child,
                                  level=1, pos_list=pos_list,
                                  act_list=act_list)
    if value < point:
        act_list = act
        pos_list = pos

    pr_red(f"end max_val:{point}", act_list)
    return act_list


def get_max_val(actions: list, base_map: Map, evaluated_map: EvaluatedMap, locker: Locker,
                player: Player, enemy: Player, player_another: Player, enemy_child: Player, level: int, pos_list,
                act_list
                ) -> tuple[int, list, list]:
    value = StatusPoint.MIN.value
    new_pos_list = []
    new_act_list = []
    print(f"40 get_max_val level:{level}")

    try:
        for action in actions:
            if action == [1, 1]:
                if level <= H:  # H_NO_ATTACK
                    point, tmp_act_list, tmp_pos_list = attack_action(actions=actions, base_map=base_map,
                                                                      evaluated_map=evaluated_map, locker=locker,
                                                                      player=player, enemy=enemy,
                                                                      player_another=player_another,
                                                                      enemy_child=enemy_child, level=level,
                                                                      pos_list=pos_list,
                                                                      act_list=act_list)
                    print(f"55 act:{action} level:{level}\033[91m point: {point}\033[00m", value, tmp_act_list,
                          tmp_pos_list)
                    if value < point:
                        value = point
                        new_pos_list = new_pos_list
                        new_act_list = tmp_act_list

            elif action == [0, 0]:
                point = val(base_map=base_map, evaluated_map=evaluated_map, locker=locker,
                            player=player, enemy=enemy, player_another=player_another, enemy_child=enemy_child,
                            pos_list=pos_list,act_list=act_list)
                print(f"65 action:{action} level:{level}\033[91m point: {point}\033[00m", value, act_list, pos_list)
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
                                                                enemy_child=enemy_child, level=level,
                                                                pos_list=pos_list,
                                                                act_list=act_list, current_action=action)
                print(f"75 action:{action} level:{level}\033[91m point: {point}\033[00m", value, tmp_act_list,
                      tmp_pos_list)
                if value < point:
                    value = point
                    new_pos_list = new_pos_list
                    new_act_list = tmp_act_list
            print(f"80 return max_val level:{level}\033[91m value: {value}\033[00m", new_act_list)

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
    cur_weapon = player.cur_weapon

    value = StatusPoint.MIN.value
    new_pos_list = pos_list
    new_act_list = act_list
    # todo: handle expect pos/ face
    face = Face.UNKNOWN.value

    pr_green(f"115 level:{level} attack")
    if cur_weapon == 1:
        if Attack.WOODEN.value in act_list:
            pass
        else:
            if len(pos_list) >= 2:
                copy_list = [pos for pos in pos_list if pos not in Attack.ATTACKS.value]

                if len(copy_list) >= 2:
                    face = get_face(copy_list[-2], copy_list[-1])

                    print(f"130 level:{level} attack new {face} by {copy_list[-2], copy_list[-1]}")
            else:
                if locker.expect_pos is not  None and locker.expect_pos == player.position:
                    face = locker.expect_face
                    print(f"130 level:{level} expect_face attack {face}")
                else:
                    print(f"130 level:{level} expect_face attack UNKNOW")
            if face == Face.UNKNOWN.value:
                print(f"130 level:{level} attack UNKNOW return")
                return value, new_act_list, new_pos_list

            for act_atk in WeaponRange.WOODEN.value:
                pos_w_atk = [sum(i) for i in zip(player.position, act_atk)]
                if base_map.get_obj_map(pos_w_atk) == 3:
                    new_base_map = deepcopy(base_map)
                    new_player = deepcopy(player)
                    new_pos_list = deepcopy(pos_list)
                    new_act_list = deepcopy(act_list)

                    new_base_map.set_val_map(pos_w_atk, 0)
                    new_base_map.up_point += 300
                    # todo : bị break khi send direction dùng búa

                    # new_pos_list.append(new_player.position)
                    if FaceAction.FACES.value[face] == act_atk:
                        new_act_list.append(Attack.WOODEN.value)
                    else:
                        new_act_list += [get_face_act_v2(act_atk), Attack.WOODEN.value]

                    point, tmp_act_list, tmp_pos_list = get_max_val(actions=actions, base_map=new_base_map,
                                                                    evaluated_map=evaluated_map, locker=locker,
                                                                    player=new_player, enemy=enemy,
                                                                    player_another=player_another, enemy_child=enemy_child,
                                                                    level=level + 1,
                                                                    pos_list=new_pos_list,
                                                                    act_list=new_act_list)

                    print(f"140 attack:{cur_weapon} level:{level}", new_act_list, new_pos_list)
                    if value < point:
                        value = point
                        new_pos_list = new_pos_list
                        new_act_list = tmp_act_list
                        locker.expect_pos = player.position
                        locker.expect_face = FaceAction.FACES.value.index(act_atk)

                        pr_red(f"set expect pos {locker.expect_pos} expect face {locker.expect_face}" )
                        #todo : set o day bi change


        if player.has_bomb and level <= H_NO_ATTACK_BOMB:
            new_base_map = deepcopy(base_map)
            new_player = deepcopy(player)
            new_pos_list = deepcopy(pos_list)
            new_act_list = deepcopy(act_list)

            new_player.has_bomb = False
            new_base_map.bombs.append(gen_bomb(new_player))

            # new_pos_list.append(new_player.position)
            new_act_list += [Attack.SWITCH_WEAPON.value, Attack.BOMB.value]

            point, tmp_act_list, tmp_pos_list = get_max_val(actions=actions, base_map=new_base_map,
                                                            evaluated_map=evaluated_map, locker=locker,
                                                            player=new_player, enemy=enemy,
                                                            player_another=player_another, enemy_child=enemy_child,
                                                            level=level + 1,
                                                            pos_list=new_pos_list,
                                                            act_list=new_act_list)
            if value < point:
                value = point
                new_pos_list = new_pos_list
                new_act_list = tmp_act_list
            print(f"170 attack:{cur_weapon} level:{level}", new_act_list, new_pos_list)

    if cur_weapon == 2:
        if player.has_bomb and level <= H_NO_ATTACK_BOMB:
            new_base_map = deepcopy(base_map)
            new_player = deepcopy(player)
            new_pos_list = deepcopy(pos_list)
            new_act_list = deepcopy(act_list)

            new_player.has_bomb = False
            new_base_map.bombs.append(gen_bomb(new_player))

            new_pos_list.append(new_player.position)
            new_act_list.append(Attack.BOMB.value)

            point, tmp_act_list, tmp_pos_list = get_max_val(actions=actions, base_map=new_base_map,
                                                            evaluated_map=evaluated_map, locker=locker,
                                                            player=new_player, enemy=enemy,
                                                            player_another=player_another, enemy_child=enemy_child,
                                                            level=level + 1,
                                                            pos_list=new_pos_list,
                                                            act_list=new_act_list)

            if value < point:
                value = point
                new_pos_list = new_pos_list
                new_act_list = tmp_act_list
            print(f"200 attack:{cur_weapon} level:{level}", new_act_list, new_pos_list)
        # switch weapon

        if len(pos_list) >= 2:
            copy_list = [pos for pos in pos_list if pos not in Attack.ATTACKS.value]

            if len(copy_list) >= 2:
                face = get_face(copy_list[-2], copy_list[-1])

        for act_atk in WeaponRange.WOODEN.value:
            pos_w_atk = [sum(i) for i in zip(player.position, act_atk)]
            if base_map.get_obj_map(pos_w_atk) == 3:
                new_base_map = deepcopy(base_map)
                new_player = deepcopy(player)
                new_pos_list = deepcopy(pos_list)
                new_act_list = deepcopy(act_list)

                new_base_map.set_val_map(pos_w_atk, 0)
                new_base_map.up_point += 100

                if FaceAction.FACES.value[face] == act_atk:
                    new_act_list.append(Attack.WOODEN.value)
                else:
                    new_act_list += [get_face_act_v2(act_atk), Attack.WOODEN.value]

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
                    new_pos_list = new_pos_list
                    new_act_list = tmp_act_list

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
    pr_green(f"235 level:{level} move")

    if (not can_go_new_pos(new_pos_player, base_map, locker)
            ):
        print(f"240 end:{current_action} level:{level}", act_list, pos_list)
        return StatusPoint.MIN.value, act_list, pos_list

    new_player = deepcopy(player)
    new_pos_list = deepcopy(pos_list)
    new_act_list = deepcopy(act_list)

    new_player.position = new_pos_player
    new_act_list.append(current_action)
    new_pos_list.append(new_pos_player)

    if level < H:
        print(f"250 move:{current_action} level:{level}", new_act_list, new_pos_list)
        return get_max_val(actions=actions, base_map=base_map, evaluated_map=evaluated_map, locker=locker,
                           player=new_player, enemy=enemy, player_another=player_another, enemy_child=enemy_child,
                           level=level + 1,
                           pos_list=new_pos_list,
                           act_list=new_act_list)
    else:
        point = val(base_map=base_map, evaluated_map=evaluated_map, locker=locker,
                    player=player, enemy=enemy, player_another=player_another, enemy_child=enemy_child,
                    pos_list=pos_list,act_list=act_list)

        print(f"260 end:{current_action} level:{level}\033[91m point: {point}\033[00m", new_act_list, new_pos_list)
        return point, new_act_list, new_pos_list
