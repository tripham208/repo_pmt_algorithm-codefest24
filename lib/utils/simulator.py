from copy import deepcopy

from lib.alg.val import gen_bomb
from lib.model.dataclass import Player, Map
from lib.model.enum.action import Action, FaceAction, Attack
from lib.model.enum.gameobjects import Objects
from lib.model.enum.range import BombRange


def action_simulator(player: Player, base_map: Map, act_list: list):
    fake_player = deepcopy(player)
    pos_destroy = []
    pos_move = [player.position]
    for current_action in act_list:
        if current_action in Action.MOVE.value:
            fake_player.position = [sum(i) for i in zip(fake_player.position, current_action)]
            pos_move.append(fake_player.position)
            fake_player.update_face(current_action)
        if current_action in FaceAction.FACE_ACTION_V2.value:
            fake_player.update_face(current_action)
        if current_action in [[2, 2], [22, 22]]:
            act_atk = FaceAction.FACE_ACTION.value[fake_player.face]
            pos_w_atk = [sum(i) for i in zip(player.position, act_atk)]
            if base_map.get_obj_map(pos_w_atk) == 3:
                pos_destroy.append(pos_w_atk)
                # base_map.set_val_map(pos_w_atk, 0)
        if current_action == Attack.BOMB.value:
            pos_destroy += check_obj_destroy_by_bomb(gen_bomb(player), base_map)
    return pos_destroy, pos_move


def check_obj_destroy_by_bomb(bomb, base_map: Map) -> list:
    power = bomb.get("power", 0)
    bomb_range = BombRange[f'LV{power}'].value
    pos_destroy = []
    for i in bomb_range:
        for j in i:
            pos = [bomb["row"] + j[0], bomb["col"] + j[1]]
            if base_map.get_obj_map(pos) == 2:
                pos_destroy.append(pos_destroy)
                break
            elif base_map.get_obj_map(pos) in Objects.BOMB_NO_DESTROY.value:
                break
    return pos_destroy
