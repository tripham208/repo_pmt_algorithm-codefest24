import sys
import time

import socketio

from lib.alg.astar import a_star_optimized
from lib.alg.bfs import bfs_dq
from lib.alg.max import max_val
from lib.model.dataclass import *
from lib.model.enum.action import Attack, Action
from lib.model.enum.gameobjects import Tag
from lib.model.enum.range import BombRange
from lib.utils.emit_generator import gen_direction, gen_drive_data, gen_action_data
from lib.utils.map import euclid_distance, find_index
from lib.utils.printer import pr_green, pr_yellow
from match import *

# MAP
MAP = Map(map=[], bombs=[], spoils=[])
EVALUATED_MAP = EvaluatedMap(player_map=[], enemy_map=[], road_map=[])

# PLAYER
PLAYER = Player(position=[])  # [row,col]
ENEMY = Player(position=[])
PLAYER_CHILD = Player(position=[0, 0])
ENEMY_CHILD = Player(position=[0, 0])

LOCKER = Locker(danger_pos_lock_max=[], danger_pos_lock_bfs=[], a_star_lock=[], pos_lock=[])


# PASTE DATA
def paste_player_data(players):
    global PLAYER, ENEMY

    for player in players:
        print(player)
        if player["id"] in PLAYER_ID and not player.get("isChild", False):
            PLAYER.position = [player["currentPosition"]["row"], player["currentPosition"]["col"]]
            PLAYER.power = player["power"]
            PLAYER.score = player["score"]
            PLAYER.lives = player["lives"]
            PLAYER.has_transform = player["hasTransform"]
            PLAYER.cur_weapon = player["currentWeapon"]
            PLAYER.owner_weapon = player["ownerWeapon"]
            if PLAYER.has_transform:
                PLAYER.transform_type = player["transformType"]
            if not PLAYER.has_full_marry_items and PLAYER.has_transform:
                PLAYER.rice = player["stickyRice"]
                PLAYER.cake = player["chungCake"]
                PLAYER.elephant = player["nineTuskElephant"]
                PLAYER.rooster = player["nineSpurRooster"]
                PLAYER.horse = player["nineManeHairHorse"]
                if PLAYER.owned_marry_items == 5:
                    PLAYER.has_full_marry_items = True
        elif player["id"] in PLAYER_ID and player["isChild"]:
            PLAYER_CHILD.position = [player["currentPosition"]["row"], player["currentPosition"]["col"]]
            PLAYER_CHILD.power = player["power"]
        elif player["id"] not in PLAYER_ID and player.get("isChild", False):
            ENEMY_CHILD.position = [player["currentPosition"]["row"], player["currentPosition"]["col"]]
            ENEMY_CHILD.power = player["power"]
        else:
            ENEMY.position = [player["currentPosition"]["row"], player["currentPosition"]["col"]]
            ENEMY.power = player["power"]
            ENEMY.has_transform = player["hasTransform"]


def paste_update(data):
    """

    :param data:
    :return:
    """
    global MAP, EVALUATED_MAP, LOCKER

    MAP.cols = data["map_info"]["size"]["cols"]
    MAP.rows = data["map_info"]["size"]["rows"]
    MAP.map = data["map_info"]["map"]
    MAP.bombs = data["map_info"]["bombs"]
    MAP.spoils = data["map_info"]["spoils"]

    paste_player_data(players=data["map_info"]["players"])

    EVALUATED_MAP.reset_point_map(cols=MAP.cols, rows=MAP.rows)
    EVALUATED_MAP.set_point_map(base_map=MAP, status=PLAYER)

    lock = get_lock_bombs(base_map=MAP)
    LOCKER.pos_lock = lock
    LOCKER.danger_pos_lock_max = lock
    LOCKER.danger_pos_lock_bfs = lock
    # case vẫn tính đc đường dù bị bomb chặn => dừng ở vị trí bị lock

    pr_yellow(f"spoil {MAP.spoils}")


def get_lock_bombs(base_map: Map):
    pos_danger = []
    PLAYER.has_bomb = True
    PLAYER_CHILD.has_bomb = True
    for bomb in base_map.bombs:
        power = bomb.get("power", 0)
        bomb_range = BombRange[f"LV{power}"].value
        pos_danger += [[bomb["row"], bomb["col"]]]
        is_danger = bomb.get("remainTime", 0) < 1000

        if bomb.get("playerId") in PLAYER_ID:
            if power == 1:
                PLAYER_CHILD.has_bomb = False
            else:
                PLAYER.has_bomb = False

        if not is_danger:
            continue

        for i in bomb_range:
            for j in i:
                pos = [bomb["row"] + j[0], bomb["col"] + j[1]]
                if base_map.get_obj_map(pos) in Objects.BOMB_NO_DESTROY.value:
                    break
                pos_danger.append(pos)

    return pos_danger


# EVENT HANDLER

DIRECTION_HIST = []
TIME_POINT = 0
TIME_POINT_OWN = 0
ACTION_PER_POINT = 2
COUNT = 0
COUNT_UPDATE = 0
COUNT_ST = 0
RANGE_TIME = 550
RANGE_TIME_OWN = 400


def set_bonus_point_road(pos_list, x: int):
    global EVALUATED_MAP
    for pos in pos_list:
        EVALUATED_MAP.set_val_road(pos, euclid_distance(PLAYER.position, pos) * x)


def set_road_to_badge():
    global MAP, PLAYER, LOCKER, EVALUATED_MAP
    badges = find_index(MAP.map, 6)
    pr_yellow(badges)
    nearest_badge = []
    dis = 100
    for pos in badges:
        tmp_dis = euclid_distance(PLAYER.position, pos)
        EVALUATED_MAP.set_val_road(pos, StatusPoint.BADGE.value)

        # print(pos, tmp_dis)
        if dis > tmp_dis:
            dis = tmp_dis
            nearest_badge = pos
    LOCKER.a_star_lock = Objects.A_STAR_PHASE1_LOCK.value  # lock phase 1
    act_list, pos_list = get_action(case=4, param={"target": nearest_badge})
    # print(pos_list)
    # print(act_list)
    set_bonus_point_road(pos_list, 100)


COUNT_STOP = 0


def set_road_to_point():
    act_list, pos_list = get_action(case=2)
    set_bonus_point_road(pos_list, 50)


def ticktack_handler(data):
    global PLAYER, ENEMY, PLAYER_CHILD, ENEMY_CHILD
    global MAP, EVALUATED_MAP
    global DIRECTION_HIST, TIME_POINT, TIME_POINT_OWN
    global COUNT, COUNT_UPDATE, COUNT_ST, ACTION_PER_POINT
    global COUNT_STOP
    print(data["id"], "-", data.get("player_id", "no id"), "-", data["tag"], "-", data["timestamp"], "-", TIME_POINT)

    if data.get("player_id", "no id") in PLAYER_ID:
        TIME_POINT_OWN = data["timestamp"]

    if data["tag"] in Tag.TAG_STOP.value and data["player_id"] in PLAYER_ID:
        TIME_POINT = data["timestamp"]
        COUNT += 1
        print("line 350: ", COUNT, " in ", ACTION_PER_POINT)
    if (
            COUNT == ACTION_PER_POINT
            or data.get("player_id", "no id") in PLAYER_ID
            and data["timestamp"] - TIME_POINT_OWN > RANGE_TIME_OWN
            or data["timestamp"] - TIME_POINT > RANGE_TIME
    ):
        ACTION_PER_POINT = 2
        TIME_POINT = data["timestamp"]

        paste_update(data)

        if not PLAYER.has_transform:
            set_road_to_badge()
        if EVALUATED_MAP.get_val_road(PLAYER.position) == 0:
            set_road_to_point()
        act_list = get_action(1)

        direction = gen_direction(act_list)
        print(act_list)
        drive_data = gen_drive_data(direction)
        print(drive_data)
        if Attack.SWITCH_WEAPON.value in act_list:
            emit_action(gen_action_data(action=Action.SWITCH_WEAPON.value))
            pass
        emit_drive(drive_data)
    if COUNT_STOP == 2:
        sys.exit()
    else:
        COUNT_STOP += 0


def get_case_action() -> tuple[int, dict]:
    if euclid_distance(PLAYER.position, ENEMY.position) <= 4:
        return 1, {}
    """
    if PLAYER.power > 1:
        for pos in AroundRange.LV1.value:
            if MAP.get_obj_map([sum(i) for i in zip(PLAYER.position, pos)]) == Objects.BALK.value:
                return 1, {}
    """
    val_pos = EVALUATED_MAP.get_val_road(PLAYER.position)

    if val_pos != 0:
        return 1, {}
    else:
        return 2, {}


def get_action(case, param: dict = None) -> list:
    """
    1 -> MAX \n
    2 -> BFS \n
    4 -> A STAR ; {target}\n
    :param param:
    :param case:
    :return:
    """
    match case:
        case 1:
            start_time = time.time()
            x = max_val(
                base_map=MAP,
                evaluated_map=EVALUATED_MAP,
                locker=LOCKER,
                player=PLAYER,
                enemy=ENEMY,
                player_another=PLAYER_CHILD,
                enemy_child=ENEMY_CHILD,
            )
            end_time = time.time()
            pr_green(f"Original max_val result taken: {end_time - start_time} seconds")

            return x
        case 2:
            return bfs_dq(start=PLAYER.position, locker=LOCKER, base_map=MAP, eval_map=EVALUATED_MAP)
        case 4:
            return a_star_optimized(
                start=PLAYER.position, locker=LOCKER, base_map=MAP, target=param.get("target", PLAYER.position)
            )


# SOCKET HANDLER
sio = socketio.Client()


@sio.event
def connect():
    print("connection established")


@sio.event
def disconnect():
    print("disconnected from server")


@sio.on(event=JOIN_GAME_EVENT)
def event_handle(data):
    print(f"joined game:{data}")


@sio.on(event=TICKTACK_EVENT)
def event_handle(data):
    ticktack_handler(data)


@sio.on(event=DRIVE_EVENT)
def event_handle(data):
    pass


def connect_server():
    sio.connect(URL)


def emit_event(event: str, data: dict):
    sio.emit(event=event, data=data)


def emit_join_game(game_id: str, player_id: str):
    emit_event(event=JOIN_GAME_EVENT, data={"game_id": game_id, "player_id": player_id})


def emit_drive(data: dict):
    emit_event(event=DRIVE_EVENT, data=data)


def emit_register(game_id: str, god_type: int):
    emit_event(event=REGISTER_EVENT, data={"gameId": game_id, "type": god_type})


def emit_action(data: dict):
    emit_event(event=ACTION_EVENT, data=data)


if __name__ == "__main__":
    connect_server()
    emit_join_game(game_id=GAME_ID, player_id=PLAYER_ID)
