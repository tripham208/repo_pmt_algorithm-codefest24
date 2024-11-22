from copy import deepcopy

from game.match import PLAYER_ID
from lib.alg.val import val
from lib.model.dataclass import *
from lib.model.enum.action import get_action_zone, Face, FaceAction, Attack
from lib.model.enum.point import StatusPoint
from lib.model.enum.range import WeaponRange
from lib.utils.map import is_zone, get_face, get_face_act_v2, check_have_attack
from lib.utils.printer import pr_red, pr_green, pr_yellow

H = 4
H_NO_ATTACK_BOMB = 3


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

    pr_red(f"end max_val:{response.value}", act_list)
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
    response = ValResponse(pos_list=pos_list, act_list=act_list)
    print(f"70 get_max_val level:{level}")

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
            print(
                f"90 act:{action} level:{level}\033[91m point: {tmp_response.value}\033[00m",
                tmp_response.act_list,
                tmp_response.pos_list,
            )
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
            pr_yellow(
                f"110 stop:{action} level:{level}\033[91m point: {point}\033[00m",
                response.value,
                response.act_list,
                response.pos_list,
            )
            if response.value < point:
                response = ValResponse(pos_list=pos_list, act_list=act_list, value=point)
                response.act_list.append(action)
        else:
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
            print(
                f"130 action:{action} level:{level}\033[91m point: {tmp_response.value}\033[00m",
                response.value,
                tmp_response.act_list,
                tmp_response.pos_list,
            )
            if response.value < tmp_response.value:
                response = tmp_response
        print(f"140 return max_val level:{level}\033[91m value: {response.value}\033[00m", response.act_list)
    return response

def gen_bomb(player: Player):
    return {
        "row": player.position[0],
        "col": player.position[1],
        "playerId": PLAYER_ID,
        "power": player.power,
        "remainTime": 2000,
    }


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
) -> ValResponse:
    cur_weapon = player.cur_weapon
    response = ValResponse(pos_list=pos_list, act_list=act_list)
    face = Face.UNKNOWN.value

    def wooden_attack():
        nonlocal face, response, pos_list, act_list, base_map, level, locker, actions, evaluated_map, cur_weapon
        nonlocal player, enemy, player_another, enemy_child
        pr_yellow("wooden_attack")
        if len(pos_list) >= 2:
            copy_list = [pos for pos in pos_list if pos not in Attack.ATTACKS.value]

            if len(copy_list) >= 2:
                face = get_face(copy_list[-2], copy_list[-1])
                print(f"185 level:{level} attack new {face} by {copy_list[-2], copy_list[-1]}")
        else:
            if locker.expect_pos == player.position:
                face = locker.expect_face
                print(f"190 level:{level} expect_face attack {face}")
        if face == Face.UNKNOWN.value:
            print(f"130 level:{level} attack UNKNOW return")
            return
        for act_atk in WeaponRange.WOODEN.value:
            pos_w_atk = [sum(i) for i in zip(player.position, act_atk)]
            if base_map.get_obj_map(pos_w_atk) == 3:
                new_base_map = deepcopy(base_map)
                new_player = deepcopy(player)
                new_pos_list = deepcopy(pos_list)
                new_act_list = deepcopy(act_list)

                new_base_map.set_val_map(pos_w_atk, 0)
                new_base_map.up_point += 300
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

                print(f"225 attack:{cur_weapon} level:{level}", new_act_list, new_pos_list)
                if response.value < tmp_response.value:
                    response = tmp_response
                    response.expect_pos = player.position
                    response.expect_face = FaceAction.FACES.value.index(act_atk)

    def bomb_attack():
        nonlocal response, pos_list, act_list, base_map, level, locker, actions, evaluated_map
        nonlocal player, enemy, player_another, enemy_child

        pr_yellow("bomb_attack")
        new_base_map = deepcopy(base_map)
        new_player = deepcopy(player)
        new_pos_list = deepcopy(pos_list)
        new_act_list = deepcopy(act_list)

        new_player.has_bomb = False
        new_base_map.bombs.append(gen_bomb(new_player))

        if cur_weapon == 1:
            new_act_list.append(Attack.SWITCH_WEAPON.value)
            new_player.cur_weapon = 2

        # new_pos_list.append(new_player.position)
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
        print(f"170 attack:{cur_weapon} level:{level}", new_act_list, new_pos_list)

    def god_attack():
        nonlocal face, response, pos_list, act_list, base_map, level, locker, actions, evaluated_map
        nonlocal player, enemy, player_another, enemy_child

    if Attack.WOODEN.value in act_list:
        pass
    else:
        wooden_attack()

    if Attack.BOMB.value in act_list:
        pass
    elif 2 in player.owner_weapon:
        bomb_attack()

    return response


def can_go_new_pos(new_pos_player, base_map: Map, locker: Locker) -> bool:
    if (
            new_pos_player in locker.danger_pos_lock_max
            or new_pos_player in locker.pos_lock
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
    pr_green(f"235 level:{level} move")

    if not can_go_new_pos(new_pos_player, base_map, locker):
        print(f"240 end:{current_action} level:{level}", act_list, pos_list)
        return ValResponse(act_list=act_list, pos_list=pos_list)

    new_player = deepcopy(player)
    new_pos_list = deepcopy(pos_list)
    new_act_list = deepcopy(act_list)

    new_player.position = new_pos_player
    new_act_list.append(current_action)
    new_pos_list.append(new_pos_player)

    if level < H:
        print(f"250 move:{current_action} level:{level}", new_act_list, new_pos_list)
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

        print(f"260 end:{current_action} level:{level}\033[91m point: {point}\033[00m", new_act_list, new_pos_list)
        return ValResponse(value=point, act_list=new_act_list, pos_list=new_pos_list)
