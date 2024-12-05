from copy import deepcopy

from lib.alg.val import val, gen_bomb, gen_hammer
from lib.model.dataclass import *
from lib.model.enum.action import get_action_zone, Face, FaceAction, Attack
from lib.model.enum.gameobjects import StatusPoint
from lib.model.enum.range import WeaponRange, BombRange
from lib.utils.map import is_zone, get_face_act_v2, check_have_attack, deepcopy_env
from lib.utils.printer import pr_red, pr_yellow, pr_green

H = 4
H_NO_ATTACK_BOMB = 3



def check_bomb_have_target(bomb, base_map: Map, enemy: Player, enemy_child: Player) -> bool:
    power = bomb.get("power", 0)
    bomb_range = BombRange[f'LV{power}'].value

    for i in bomb_range:
        for j in i:
            pos = [bomb["row"] + j[0], bomb["col"] + j[1]]
            if (
                    base_map.get_obj_map(pos) == 2
                    or enemy.position == pos
                    or enemy_child.position == pos
            ):
                return True
            elif base_map.get_obj_map(pos) in Objects.BOMB_NO_DESTROY.value:
                break
    return False


def max_val(
        base_map: Map,
        evaluated_map: EvaluatedMap,
        locker: Locker,
        player: Player,
        enemy: Player,
        player_another: Player,
        enemy_child: Player,
):
    value = StatusPoint.MIN.value

    pos_list = [player.position]
    act_list = []
    acts = get_action_zone(is_zone(pos=player.position, size=[base_map.rows, base_map.cols]))  # change
    player.face = Face.UNKNOWN.value
    response = get_max_val(
        actions=acts,
        base_map=base_map,
        evaluated_map=evaluated_map,
        locker=locker,
        player=player,
        enemy=enemy,
        player_another=player_another,
        enemy_child=enemy_child,
        level=1,
        pos_list=pos_list,
        act_list=act_list,
    )

    if value < response.value:
        act_list = response.act_list
        pos_list = response.pos_list
        locker.expect_pos = response.expect_pos
        locker.expect_face = response.expect_face
        if response.another:
            locker.another["hammer"] = response.another.get("hammer")
        else:
            locker.another = {}

    pr_red(f"end max_val:{response.value} {act_list}")
    return act_list


def get_max_val(
        actions: list,
        base_map: Map,
        evaluated_map: EvaluatedMap,
        locker: Locker,
        player: Player,
        enemy: Player,
        player_another: Player,
        enemy_child: Player,
        level: int,
        pos_list,
        act_list,
) -> ValResponse:
    response = ValResponse(pos_list=list(pos_list), act_list=list(act_list))
    # print(f"90 get_max_val level:{level} current action:{act_list}")

    for action in actions:
        if action == [1, 1]:
            if check_have_attack(act_list=act_list):
                continue
            tmp_response = attack_action(
                actions=actions,
                base_map=base_map,
                evaluated_map=evaluated_map,
                locker=locker,
                player=player,
                enemy=enemy,
                player_another=player_another,
                enemy_child=enemy_child,
                level=level,
                pos_list=pos_list,
                act_list=act_list,
            )
            # print(f"105 act:{action} level:{level}\033[91m point: {tmp_response.value}\033[00m {tmp_response.act_list, tmp_response.pos_list}")
            if response.value < tmp_response.value:
                response = tmp_response

        elif action == [0, 0]:
            new_act_list = deepcopy(act_list)
            if new_act_list in locker.dedup_act:
                continue
            point = val(
                base_map=base_map,
                evaluated_map=evaluated_map,
                locker=locker,
                player=player,
                enemy=enemy,
                player_another=player_another,
                enemy_child=enemy_child,
                pos_list=pos_list,
                act_list=act_list,
            )
            # pr_yellow(f"125 stop:{action} level:{level}\033[91m point: {point}\033[00m {response.value} {[response.act_list, action]} {response.pos_list}")
            if response.value < point:
                # #pr_green(response)
                response = ValResponse(pos_list=list(pos_list), act_list=list(new_act_list), value=point)
        else:
            # pr_red(f"{response}")
            tmp_response = move_action(
                actions=actions,
                base_map=base_map,
                evaluated_map=evaluated_map,
                locker=locker,
                player=player,
                enemy=enemy,
                player_another=player_another,
                enemy_child=enemy_child,
                level=level,
                pos_list=pos_list,
                act_list=act_list,
                current_action=action,
            )
            # print(f"145 action:{action} level:{level}\033[91m point: {tmp_response.value}\033[00m {response.value} {tmp_response.act_list} {tmp_response.pos_list}")
            if response.value < tmp_response.value:
                response = tmp_response
        # print(f"150 return max_val level:{level}\033[91m value: {response.value}\033[00m", response.act_list)
    return response






def is_valid_hammer(player, enemy):
    current = player.position
    target = enemy.position
    #print(current, target)
    if (2 < abs(current[0] - target[0]) <= 7) and (2 < abs(current[1] - target[1]) <= 7): return True
    if (player.lives > enemy.lives) and (abs(current[0] - target[0]) <= 2) and (2 <= abs(current[1] - target[1]) <= 2):
        return True
    return False


def attack_action(
        actions: list,
        base_map: Map,
        evaluated_map: EvaluatedMap,
        locker: Locker,
        player: Player,
        enemy: Player,
        player_another: Player,
        enemy_child: Player,
        level: int,
        pos_list: list,
        act_list: list
) -> ValResponse:
    cur_weapon = player.cur_weapon
    response = ValResponse(pos_list=list(pos_list), act_list=list(act_list))

    def wooden_attack():
        nonlocal response, pos_list, act_list, base_map, level, locker, actions, evaluated_map, cur_weapon
        nonlocal player, enemy, player_another, enemy_child
        #pr_yellow("wooden_attack")
        face = Face.UNKNOWN.value
        if len(act_list) >= 1:
            face = player.face
        else:
            #print("210", locker.another.get("trigger_by_point", False))
            if locker.expect_pos == player.position and (
                    locker.another.get("trigger_by_point", False) or player.remember_face):
                face = locker.expect_face
        if player.position in locker.all_bomb_pos:
            return
        for act_atk in WeaponRange.WOODEN.value:
            pos_w_atk = [sum(i) for i in zip(player.position, act_atk)]
            # print(pos_w_atk, base_map.get_obj_map(pos_w_atk))
            if base_map.get_obj_map(pos_w_atk) == 3 or (pos_w_atk == enemy.position and not enemy.is_stun):
                new_player = deepcopy(player)
                new_base_map, new_pos_list, new_act_list = deepcopy_env(base_map, pos_list, act_list)

                new_base_map.set_val_map(pos_w_atk, 0)
                if (base_map.get_obj_map(pos_w_atk) == 3
                        and (
                                (player.has_transform or player.is_child)
                                or (evaluated_map.get_val_road(pos_w_atk) > 75 and not player.has_transform)
                        )
                ):
                    new_base_map.up_point += StatusPoint.BRICK_WALL.value
                elif pos_w_atk == enemy.position:
                    new_base_map.up_point += StatusPoint.BOMB_ENEMY.value if not enemy.is_stun else 0

                if cur_weapon == 2:
                    new_act_list.append(Attack.SWITCH_WEAPON.value)

                if FaceAction.FACE_ACTION.value[face] == act_atk:
                    new_act_list.append(Attack.WOODEN.value)
                else:
                    new_act_list += [get_face_act_v2(act_atk), Attack.WOODEN.value]

                tmp_response = get_max_val(
                    actions=actions,
                    base_map=new_base_map,
                    evaluated_map=evaluated_map,
                    locker=locker,
                    player=new_player,
                    enemy=enemy,
                    player_another=player_another,
                    enemy_child=enemy_child,
                    level=level + 1,
                    pos_list=new_pos_list,
                    act_list=new_act_list,
                )

                # #print(f"225 attack:{cur_weapon} level:{level}", new_act_list, new_pos_list)
                if response.value < tmp_response.value:
                    response = tmp_response
                    response.weapon = Weapon.WOODEN.value
                    response.expect_pos = player.position
                    response.expect_face = FaceAction.FACE_ACTION.value.index(act_atk)

    def bomb_attack():
        nonlocal response, pos_list, act_list, base_map, level, locker, actions, evaluated_map
        nonlocal player, enemy, player_another, enemy_child

        #pr_yellow(f"bomb_attack {level}")
        new_player = deepcopy(player)
        new_player.has_bomb = False
        bomb = gen_bomb(new_player)

        if not check_bomb_have_target(bomb, base_map, enemy, enemy_child):
            return

        new_base_map, new_pos_list, new_act_list = deepcopy_env(base_map, pos_list, act_list)
        new_base_map.bombs.append(bomb)

        if cur_weapon == 1:
            new_act_list.append(Attack.SWITCH_WEAPON.value)
            new_player.cur_weapon = 2

        new_pos_list.append(new_player.position)
        new_act_list.append(Attack.BOMB.value)

        tmp_response = get_max_val(
            actions=actions,
            base_map=new_base_map,
            evaluated_map=evaluated_map,
            locker=locker,
            player=new_player,
            enemy=enemy,
            player_another=player_another,
            enemy_child=enemy_child,
            level=level + 1,
            pos_list=new_pos_list,
            act_list=new_act_list,
        )
        if response.value < tmp_response.value:
            response = tmp_response
            response.weapon = Weapon.BOMB.value
        #print(f"295 attack:{cur_weapon} level:{level}", new_act_list, new_pos_list)

    def god_attack():
        nonlocal response, pos_list, act_list, base_map, level, locker, actions, evaluated_map
        nonlocal player, enemy, player_another, enemy_child
        enemy_have_child = False if enemy_child.position == [0, 0] else True
        #pr_yellow(f"god_attack {level}")

        # todo máu nhiều hơn phang luôn
        if max(player.transform_type, player_another.transform_type) == Objects.MOUNTAIN_GOD.value:
            #print(f"god_attack {level} check enemy")
            if is_valid_hammer(player, enemy) and not enemy.is_stun:  # 9
                print("valid ene")
                new_player = deepcopy(player)
                new_base_map, new_pos_list, new_act_list = deepcopy_env(base_map, pos_list, act_list)

                new_act_list.append(Attack.HAMMER.value)
                new_base_map.hammers.append(gen_hammer(enemy.position))
                #print(new_base_map.hammers)
                tmp_response = get_max_val(
                    actions=actions,
                    base_map=new_base_map,
                    evaluated_map=evaluated_map,
                    locker=locker,
                    player=new_player,
                    enemy=enemy,
                    player_another=player_another,
                    enemy_child=enemy_child,
                    level=level + 1,
                    pos_list=new_pos_list,
                    act_list=new_act_list,
                )

                #print(f"225 attack:{cur_weapon} level:{level}", new_act_list, new_pos_list)
                if response.value < tmp_response.value:
                    response = tmp_response
                    response.weapon = Weapon.HAMMER.value
                    response.another["hammer"] = enemy.position
            if enemy_have_child and is_valid_hammer(player, enemy_child) and not enemy_child.is_stun:
                #print("valid child")
                new_player = deepcopy(player)
                new_base_map, new_pos_list, new_act_list = deepcopy_env(base_map, pos_list, act_list)

                new_act_list.append(Attack.HAMMER.value)
                new_base_map.hammers.append(gen_hammer(enemy_child.position))

                tmp_response = get_max_val(
                    actions=actions,
                    base_map=new_base_map,
                    evaluated_map=evaluated_map,
                    locker=locker,
                    player=new_player,
                    enemy=enemy,
                    player_another=player_another,
                    enemy_child=enemy_child,
                    level=level + 1,
                    pos_list=new_pos_list,
                    act_list=new_act_list,
                )

                #print(f"225 attack:{cur_weapon} level:{level}", new_act_list, new_pos_list)
                if response.value < tmp_response.value:
                    response = tmp_response
                    response.weapon = Weapon.HAMMER.value
                    response.another["hammer"] = enemy_child.position
        else:
            pass
    if (not is_basic_attacked(act_list) and (player.has_transform or player.is_child)
        and max(player.time_to_use_special_weapons,
                player_another.time_to_use_special_weapons) > 0 and player.can_use_god_attack) and level <= 2:
        god_attack()

    if not is_basic_attacked(act_list) and 2 in player.owner_weapon and player.has_bomb and level <= H_NO_ATTACK_BOMB:
        if not response.weapon == Weapon.HAMMER.value or response.value < 0:
            bomb_attack()

    if not is_basic_attacked(act_list) and level <= H_NO_ATTACK_BOMB:
        if not response.weapon == Weapon.HAMMER.value and not response.weapon == Weapon.BOMB.value or response.value < 0:
            wooden_attack()

    return response


def is_basic_attacked(act_list):
    if Attack.WOODEN.value in act_list or Attack.BOMB.value in act_list:
        return True
    else:
        return False


def can_go_new_pos(new_pos_player, base_map: Map, locker: Locker) -> bool:
    if (
            new_pos_player in locker.danger_pos_lock_max
            or new_pos_player in locker.pos_lock
            or new_pos_player in base_map.get_pos_bombs
            or base_map.map[new_pos_player[0]][new_pos_player[1]] in Objects.MAX_BLOCK.value
    ):
        return False
    return True


def move_action(
        actions: list,
        base_map: Map,
        evaluated_map: EvaluatedMap,
        locker: Locker,
        player: Player,
        enemy: Player,
        player_another: Player,
        enemy_child: Player,
        level: int,
        pos_list,
        act_list,
        current_action,
) -> ValResponse:
    new_pos_player = [sum(i) for i in zip(player.position, current_action)]
    #pr_green(f"400 level:{level} move; current action:{act_list}; current poss:{pos_list}")

    if not can_go_new_pos(new_pos_player, base_map, locker):
        # print(f"405 end:{current_action} level:{level}", act_list, pos_list)
        return ValResponse(pos_list=list(pos_list), act_list=list(act_list))

    if Attack.BOMB.value not in act_list and new_pos_player in pos_list:
        return ValResponse(pos_list=list(pos_list), act_list=list(act_list))
    if Attack.HAMMER.value not in act_list and new_pos_player in pos_list:
        return ValResponse(pos_list=list(pos_list), act_list=list(act_list))

    new_player = deepcopy(player)
    new_base_map, new_pos_list, new_act_list = deepcopy_env(base_map, pos_list, act_list)

    new_player.position = new_pos_player
    new_act_list.append(current_action)
    new_pos_list.append(new_pos_player)
    new_player.update_face(current_action)

    if level < H and not (
            Attack.WOODEN.value in act_list and len(act_list) >= 2 and act_list[-2] != Attack.WOODEN.value):
        #print(f"315 move:{current_action} level:{level}", new_act_list, new_pos_list)
        return get_max_val(
            actions=actions,
            base_map=base_map,
            evaluated_map=evaluated_map,
            locker=locker,
            player=new_player,
            enemy=enemy,
            player_another=player_another,
            enemy_child=enemy_child,
            level=level + 1,
            pos_list=new_pos_list,
            act_list=new_act_list,
        )
    else:
        if new_act_list in locker.dedup_act:
            return ValResponse(pos_list=list(pos_list), act_list=list(act_list))

        point = val(
            base_map=base_map,
            evaluated_map=evaluated_map,
            locker=locker,
            player=new_player,
            enemy=enemy,
            player_another=player_another,
            enemy_child=enemy_child,
            pos_list=new_pos_list,
            act_list=new_act_list,
        )

        #print(f"360 end:{current_action} level:{level}\033[91m point: {point}\033[00m", new_act_list, new_pos_list)
        return ValResponse(value=point, act_list=new_act_list, pos_list=new_pos_list)
