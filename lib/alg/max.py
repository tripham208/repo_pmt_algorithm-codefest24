from copy import deepcopy

from game.match import PLAYER_ID
from lib.alg.val import val
from lib.model.dataclass import *
from lib.model.enum.action import get_action_zone, Face, FaceAction, Attack
from lib.model.enum.gameobjects import StatusPoint
from lib.model.enum.range import WeaponRange, BombRange
from lib.utils.map import is_zone, get_face, get_face_act_v2, check_have_attack
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
    print(f"90 get_max_val level:{level} current action:{act_list}")

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
            print(f"105 act:{action} level:{level}\033[91m point: {tmp_response.value}\033[00m {tmp_response.act_list, tmp_response.pos_list}")
            if response.value < tmp_response.value:
                response = tmp_response

        elif action == [0, 0]:
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
            pr_yellow(f"125 stop:{action} level:{level}\033[91m point: {point}\033[00m {response.value} {[response.act_list, action]} {response.pos_list}")
            if response.value < point:
                # #pr_green(response)
                response = ValResponse(pos_list=list(pos_list), act_list=list(act_list), value=point)
                response.act_list.append(action)
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
            print(f"145 action:{action} level:{level}\033[91m point: {tmp_response.value}\033[00m {response.value} {tmp_response.act_list} {tmp_response.pos_list}")
            if response.value < tmp_response.value:
                response = tmp_response
        print(f"150 return max_val level:{level}\033[91m value: {response.value}\033[00m", response.act_list)
    return response


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


def deepcopy_env(base_map, pos_list, act_list):
    return deepcopy(base_map), deepcopy(pos_list), deepcopy(act_list)


def is_valid_hammer(current, target):
    if (abs(current[0] - target[0]) <= 7) and (abs(current[1] - target[1]) <= 7): return True
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
        act_list: list,
        current_max: ValResponse
) -> ValResponse:
    cur_weapon = player.cur_weapon
    response = ValResponse(pos_list=list(pos_list), act_list=list(act_list))
    face = Face.UNKNOWN.value

    def wooden_attack():
        nonlocal face, response, pos_list, act_list, base_map, level, locker, actions, evaluated_map, cur_weapon
        nonlocal player, enemy, player_another, enemy_child
        #pr_yellow("wooden_attack")
        if len(pos_list) >= 2:
            copy_list = [pos for pos in pos_list]

            if len(copy_list) >= 2:
                face = get_face(copy_list[-2], copy_list[-1])
                #print(f"185 level:{level} attack new {face} by {copy_list[-2], copy_list[-1]}")
        else:
            if locker.expect_pos == player.position:
                face = locker.expect_face
                # #print(f"190 level:{level} expect_face attack {face}")
        if face == Face.UNKNOWN.value:
            # #print(f"195 level:{level} attack UNKNOW return")
            return
        if player.position in locker.all_bomb_pos:
            return
        for act_atk in WeaponRange.WOODEN.value:
            pos_w_atk = [sum(i) for i in zip(player.position, act_atk)]
            #print(pos_w_atk, base_map.get_obj_map(pos_w_atk))
            if base_map.get_obj_map(pos_w_atk) == 3 or (pos_w_atk == enemy.position and not enemy.is_stun):
                new_player = deepcopy(player)
                new_base_map, new_pos_list, new_act_list = deepcopy_env(base_map, pos_list, act_list)

                new_base_map.set_val_map(pos_w_atk, 0)
                if (base_map.get_obj_map(pos_w_atk) == 3
                        and (
                                player.has_transform
                                or (evaluated_map.get_val_road(pos_w_atk) > 75 and not player.has_transform)
                        )
                ):
                    new_base_map.up_point += StatusPoint.BRICK_WALL.value
                elif pos_w_atk == enemy.position:
                    new_base_map.up_point += StatusPoint.BOMB_ENEMY.value if not enemy.is_stun else 0

                if cur_weapon == 2:
                    new_act_list.append(Attack.SWITCH_WEAPON.value)

                if FaceAction.FACES.value[face] == act_atk:
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
                    response.expect_pos = player.position
                    response.expect_face = FaceAction.FACES.value.index(act_atk)

    def bomb_attack():
        nonlocal response, pos_list, act_list, base_map, level, locker, actions, evaluated_map
        nonlocal player, enemy, player_another, enemy_child

        #pr_yellow("bomb_attack")
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
        #print(f"295 attack:{cur_weapon} level:{level}", new_act_list, new_pos_list)

    def god_attack():
        nonlocal face, response, pos_list, act_list, base_map, level, locker, actions, evaluated_map
        nonlocal player, enemy, player_another, enemy_child
        enemy_have_child = False if enemy_child.position == [0, 0] else True
        pr_yellow("god_attack")

        # todo máu nhiều hơn phang luôn
        if player.transform_type == Objects.MOUNTAIN_GOD.value:
            if is_valid_hammer(player.position, enemy.position):  # 9
                new_player = deepcopy(player)
                new_base_map, new_pos_list, new_act_list = deepcopy_env(base_map, pos_list, act_list)

                new_act_list.append(Attack.HAMMER.value)
                new_base_map.hammers.append(gen_hammer(enemy.position))
                print( new_base_map.hammers)
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
                    response.another["hammer"] = enemy.position
            if enemy_have_child and is_valid_hammer(player.position, enemy_child.position):

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

                # #print(f"225 attack:{cur_weapon} level:{level}", new_act_list, new_pos_list)
                if response.value < tmp_response.value:
                    response = tmp_response
                    response.another["hammer"] = enemy.position
        else:
            pass


    if (not is_basic_attacked(act_list) and player.has_transform
            and max(player.time_to_use_special_weapons,
                    player_another.time_to_use_special_weapons) > 0 and player.can_use_god_attack) and level <= 2:
        god_attack()

    if not is_basic_attacked(act_list) and 2 in player.owner_weapon and player.has_bomb and level <= H_NO_ATTACK_BOMB:
        bomb_attack()

    if not is_basic_attacked(act_list):
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
        #print(f"405 end:{current_action} level:{level}", act_list, pos_list)
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
