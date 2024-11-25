import sys
from datetime import datetime

import socketio

from lib.alg.astar import a_star_optimized
from lib.alg.bfs import bfs_dq
from lib.alg.max import max_val
from lib.model.dataclass import *
from lib.model.enum.action import Action, Attack
from lib.model.enum.gameobjects import Tag
from lib.model.enum.range import BombRange
from lib.utils.emit_generator import gen_direction, gen_drive_data, gen_action_data
from lib.utils.map import euclid_distance, find_index, get_info_action
from lib.utils.printer import pr_green, pr_yellow, pr_red
from match import *

# MAP
MAP = Map(map=[], bombs=[], spoils=[])
EVALUATED_MAP = EvaluatedMap(player_map=[], enemy_map=[], road_map=[])

# PLAYER
PLAYER = Player(position=[])  # [row,col]
ENEMY = Player(position=[])
PLAYER_CHILD = Player(position=[0, 0])
ENEMY_CHILD = Player(position=[0, 0])

LOCKER = Locker(danger_pos_lock_max=[], danger_pos_lock_bfs=[], a_star_lock=Objects.A_STAR_PHASE1_LOCK.value,
                pos_lock=[])

HAVE_CHILD = False
ENEMY_NOT_IN_MAP = True


def check_id_child(pid) -> bool:
    if (pid in PLAYER_ID
            or PLAYER_ID in pid
            or pid[0:10] in PLAYER_ID
    ):
        return True
    return False


# PASTE DATA
def paste_player_data(players):
    global PLAYER, ENEMY, HAVE_CHILD, ENEMY_NOT_IN_MAP
    ENEMY_NOT_IN_MAP = True

    for player in players:
        print(player)
        if player["id"] in PLAYER_ID and player.get("isChild", False) == False:
            # print("paste_player")
            PLAYER.position = [player["currentPosition"]["row"], player["currentPosition"]["col"]]
            PLAYER.power = player["power"]
            PLAYER.score = player["score"]
            PLAYER.lives = player["lives"]
            PLAYER.has_transform = player["hasTransform"]
            PLAYER.cur_weapon = player["currentWeapon"]
            PLAYER.owner_weapon = player["ownerWeapon"]
            PLAYER.is_stun = player["isStun"]
            if PLAYER.has_transform:
                PLAYER.transform_type = player.get("transformType", 0)
                PLAYER.time_to_use_special_weapons = player["timeToUseSpecialWeapons"]
                PLAYER.can_use_item = True
            if not PLAYER.has_full_marry_items and PLAYER.has_transform:
                PLAYER.rice = player["stickyRice"]
                PLAYER.cake = player["chungCake"]
                PLAYER.elephant = player["nineTuskElephant"]
                PLAYER.rooster = player["nineSpurRooster"]
                PLAYER.horse = player["nineManeHairHorse"]
                if PLAYER.owned_marry_items == 5:
                    PLAYER.has_full_marry_items = True
        elif check_id_child(player["id"]) and player["isChild"] == True:
            # print("paste_player Child", player["currentPosition"])
            PLAYER_CHILD.position = [player["currentPosition"]["row"], player["currentPosition"]["col"]]
            PLAYER_CHILD.power = player["power"]
            PLAYER_CHILD.cur_weapon = player["currentWeapon"]
            PLAYER_CHILD.owner_weapon = player["ownerWeapon"]
            HAVE_CHILD = True
        elif player["id"] not in PLAYER_ID and player.get("isChild", False) == True:
            # print("paste_ENEMY_CHILD")
            ENEMY_CHILD.position = [player["currentPosition"]["row"], player["currentPosition"]["col"]]
            ENEMY_CHILD.power = player["power"]
            ENEMY_CHILD.is_stun = player["isStun"]
        else:
            # print("paste_ENEMY")
            ENEMY.position = [player["currentPosition"]["row"], player["currentPosition"]["col"]]
            ENEMY.power = player["power"]
            ENEMY.has_transform = player["hasTransform"]
            ENEMY.is_stun = player["isStun"]
            ENEMY_NOT_IN_MAP = False


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

    lock_danger, pos_warning, pos_all = get_lock_bombs(base_map=MAP)
    LOCKER.pos_lock = lock_danger + [PLAYER_CHILD.position, ENEMY.position, ENEMY_CHILD.position]
    LOCKER.danger_pos_lock_max = lock_danger
    LOCKER.danger_pos_lock_bfs = lock_danger
    LOCKER.warning_pos_bfs = pos_warning
    LOCKER.warning_pos_max = pos_warning
    LOCKER.all_bomb_pos = pos_all
    # case vẫn tính đc đường dù bị bomb chặn => dừng ở vị trí bị lock

    pr_yellow(f"spoil {MAP.spoils}")
    pr_yellow(f"bombs {MAP.bombs}")


def get_lock_bombs(base_map: Map):
    pos_danger = []
    pos_warning = []
    pos_all = []
    PLAYER.has_bomb = True
    PLAYER_CHILD.has_bomb = True
    for bomb in base_map.bombs:
        power = bomb.get("power", 0)
        bomb_range = BombRange[f"LV{power}"].value
        pos_danger += [[bomb["row"], bomb["col"]]]
        is_safe = bomb.get("remainTime", 0) > 1300
        is_warning = 1000 < bomb.get("remainTime", 0) < 1300

        if bomb.get("playerId") in PLAYER_ID:
            PLAYER.has_bomb = False
        elif check_id_child(bomb.get("playerId")):
            PLAYER_CHILD.has_bomb = False

        for i in bomb_range:
            for j in i:
                pos = [bomb["row"] + j[0], bomb["col"] + j[1]]
                if base_map.get_obj_map(pos) in Objects.BOMB_NO_DESTROY.value:
                    break
                if is_warning:
                    pos_warning.append(pos)
                else:
                    pos_danger.append(pos)
                pos_all.append(pos)

    return pos_danger, pos_warning, pos_all


# EVENT HANDLER
def set_bonus_point_road(pos_list, start, x: int):
    global EVALUATED_MAP
    for pos in pos_list:
        EVALUATED_MAP.set_val_road(pos, euclid_distance(start, pos) * x)


def set_road_to_badge():
    global MAP, PLAYER, LOCKER, EVALUATED_MAP
    badges = find_index(MAP.map, 6)
    pr_yellow(badges)
    nearest_badge = []
    dis = 100
    MAP.badges = badges
    for pos in badges:
        tmp_dis = euclid_distance(PLAYER.position, pos)
        # EVALUATED_MAP.set_val_player(pos, StatusPoint.BADGE.value)

        # print(pos, tmp_dis)
        if dis > tmp_dis:
            dis = tmp_dis
            nearest_badge = pos
    LOCKER.a_star_lock = Objects.A_STAR_PHASE1_LOCK.value  # lock phase 1
    act_list, pos_list = get_action(case=4, param={"target": nearest_badge})
    # pr_red(f"astar {pos_list}")
    # print(act_list)
    set_bonus_point_road(pos_list, PLAYER.position, 100)


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
    x10 -> for child
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
            check = end_time - start_time

            pr_green(f"Original max_val result taken: {end_time - start_time} seconds")
            if check >= 0.15:
                return []
            return x
        case 2:
            return bfs_dq(start=PLAYER.position, locker=LOCKER, base_map=MAP, eval_map=EVALUATED_MAP)
        case 4:
            return a_star_optimized(
                start=PLAYER.position, locker=LOCKER, base_map=MAP, target=param.get("target", PLAYER.position)
            )
        case 10:
            start_time = time.time()
            x = max_val(
                base_map=MAP,
                evaluated_map=EVALUATED_MAP,
                locker=LOCKER,
                player=PLAYER_CHILD,
                enemy=ENEMY,
                player_another=PLAYER,
                enemy_child=ENEMY_CHILD,
            )
            end_time = time.time()
            pr_green(f"Original max_val result taken: {end_time - start_time} seconds")
            return x
        case 20:
            return bfs_dq(start=PLAYER_CHILD.position, locker=LOCKER, base_map=MAP, eval_map=EVALUATED_MAP)
        case 40:
            return a_star_optimized(
                start=PLAYER_CHILD.position, locker=LOCKER, base_map=MAP,
                target=param.get("target", PLAYER_CHILD.position)
            )


def set_road_to_point(start, child: bool = False):
    if not child:
        act_list, pos_list = get_action(case=2)
        set_bonus_point_road(pos_list, start, 50)
    else:
        act_list, pos_list = get_action(case=20)
        set_bonus_point_road(pos_list, start, 50)


DIRECTION_HIST_PLAYER = []
DIRECTION_HIST_CHILD = []
UNLOCK = 6
COUNT_UNLOCK = 0


def process_emit_action(act_list, child: bool = False):
    global ACTION_PER_POINT_PLAYER, COUNT_POINT_PLAYER
    global ACTION_PER_POINT_CHILD, COUNT_POINT_CHILD

    info = get_info_action(act_list)
    if info["switch"]:
        emit_action(gen_action_data(action=Action.SWITCH_WEAPON.value, child=child))

    if not child:
        if info["reface"]:
            direction = gen_direction(act_list)
            ACTION_PER_POINT_PLAYER = len(direction)
        elif info["attack"] in Attack.BASIC_ATTACKS.value:
            direction = gen_direction(act_list)
            ACTION_PER_POINT_PLAYER = info["drop"]
        else:
            direction = gen_direction(act_list[0:info["drop"]])
            ACTION_PER_POINT_PLAYER = info["drop"]

        ACTION_PER_POINT_PLAYER = max(ACTION_PER_POINT_PLAYER, 1)
        print(ACTION_PER_POINT_PLAYER)
        COUNT_POINT_PLAYER = 0
    else:
        print("process_emit_action set child")
        if info["reface"]:
            direction = gen_direction(act_list)
            ACTION_PER_POINT_CHILD = len(direction)
        elif info["attack"] in Attack.BASIC_ATTACKS.value:
            direction = gen_direction(act_list)
            ACTION_PER_POINT_CHILD = info["drop"]
        else:
            direction = gen_direction(act_list[0:info["drop"]])
            ACTION_PER_POINT_CHILD = info["drop"]

        ACTION_PER_POINT_CHILD = max(ACTION_PER_POINT_CHILD, 1)
        COUNT_POINT_CHILD = 0

    print(act_list)
    # DIRECTION_HIST.append(direction)
    drive_data = gen_drive_data(direction, child=child)
    # TODO DEDUP ACTION
    emit_drive(drive_data)


def dedup_action(action, action_v2):
    global ACTION_PER_POINT_PLAYER
    direction = gen_direction(action)
    DIRECTION_HIST_PLAYER.append(direction)
    print(DIRECTION_HIST_PLAYER)
    if len(DIRECTION_HIST_PLAYER) >= 6:
        if DIRECTION_HIST_PLAYER.count(direction) >= 3:
            ACTION_PER_POINT_PLAYER = len(action_v2)
            direction = gen_direction(action_v2)
            DIRECTION_HIST_PLAYER.pop()
            DIRECTION_HIST_PLAYER.append(direction)
        DIRECTION_HIST_PLAYER.pop(0)
    if len(direction) != ACTION_PER_POINT_PLAYER:  # re verify
        ACTION_PER_POINT_PLAYER = len(direction)
    # pr_red("line 400 new direction:" + direction)
    return direction


list_skip = [
    "x"
]

ACTION_PER_POINT_PLAYER = 1
ACTION_PER_POINT_CHILD = 1

TIME_POINT_PLAYER = 0
TIME_POINT_CHILD = 0

TIME_POINT_PLAYER_OWN = 0
TIME_POINT_CHILD_OWN = 0

COUNT_POINT_PLAYER = 0
COUNT_POINT_CHILD = 0

COUNT_UPDATE = 0
COUNT_ST = 0
RANGE_TIME = 550
RANGE_TIME_OWN = 400

DEDUP_EVENT_PLAYER = 0


def ticktack_handler(data):
    global HAVE_CHILD
    global TIME_POINT_PLAYER
    global TIME_POINT_CHILD
    is_paste_update = False
    if (
            COUNT_POINT_PLAYER == ACTION_PER_POINT_PLAYER
            or data["timestamp"] - TIME_POINT_PLAYER_OWN > RANGE_TIME_OWN
            or data["timestamp"] - TIME_POINT_PLAYER > RANGE_TIME
    ):
        pass
        pr_red("process PLAYER")
        if COUNT_POINT_PLAYER == ACTION_PER_POINT_PLAYER:
            pr_yellow("player trigger by point")
        if data["timestamp"] - TIME_POINT_PLAYER_OWN > RANGE_TIME_OWN:
            pr_yellow("player trigger by timeout own")
        if data["timestamp"] - TIME_POINT_PLAYER > RANGE_TIME:
            pr_yellow("player trigger by timeout")

        TIME_POINT_PLAYER = data["timestamp"]
        if not is_paste_update:
            paste_update(data)
            is_paste_update = True

        if PLAYER.has_full_marry_items and HAVE_CHILD == False and ENEMY_NOT_IN_MAP == False:
            emit_action(gen_action_data(action=Action.MARRY_WIFE.value))
        if not PLAYER.has_transform:
            set_road_to_badge()
        if EVALUATED_MAP.get_val_road(PLAYER.position) == 0:
            set_road_to_point(PLAYER.position)
        act_list = get_action(1)
        if act_list:
            process_emit_action(act_list)
    # CHILD
    #HAVE_CHILD = True
    if (
            (COUNT_POINT_CHILD == ACTION_PER_POINT_CHILD
             or data["timestamp"] - TIME_POINT_CHILD_OWN > RANGE_TIME_OWN
             or data["timestamp"] - TIME_POINT_CHILD > RANGE_TIME
            ) and HAVE_CHILD
    ):
        pr_red("process child")

        print("start", int(datetime.now().timestamp() * 1000))

        if COUNT_POINT_CHILD == ACTION_PER_POINT_CHILD:
            pr_yellow("CHILD trigger by point")
        if data["timestamp"] - TIME_POINT_CHILD_OWN > RANGE_TIME_OWN:
            pr_yellow(f"CHILD trigger by timeout own{data["timestamp"], TIME_POINT_CHILD_OWN}")
        if data["timestamp"] - TIME_POINT_CHILD > RANGE_TIME:
            pr_yellow("CHILD trigger by timeout")
        if not is_paste_update:
            paste_update(data)
        TIME_POINT_CHILD = data["timestamp"]
        if EVALUATED_MAP.get_val_road(PLAYER_CHILD.position) == 0:
            set_road_to_point(PLAYER_CHILD.position)
        act_list = get_action(10)
        if act_list:
            process_emit_action(act_list, child=True)

        print("end", int(datetime.now().timestamp() * 1000))
        #sys.exit()


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


RUNNING = False
import threading
import time

lock = threading.Lock()


@sio.on(event=TICKTACK_EVENT)
def event_handle(data):
    global RUNNING, DEDUP_EVENT_PLAYER
    global TIME_POINT_CHILD_OWN, TIME_POINT_CHILD, COUNT_POINT_CHILD
    global TIME_POINT_PLAYER_OWN, TIME_POINT_PLAYER, COUNT_POINT_PLAYER

    player_id_of_event = data.get("player_id", "no id")
    print("event_handle", data["id"], "-", data.get("player_id", "no id"), "-", data["tag"], "-", data["timestamp"])

    if (player_id_of_event in PLAYER_ID
            or PLAYER_ID in player_id_of_event
            or player_id_of_event[0:10] in PLAYER_ID
    ):

        # print("event by player", data["timestamp"], TIME_POINT_PLAYER_OWN, data["timestamp"] - TIME_POINT_PLAYER_OWN,
        #       RANGE_TIME_OWN, "----------", TIME_POINT_PLAYER, data["timestamp"] - TIME_POINT_PLAYER, RANGE_TIME)

        if "child" in player_id_of_event and HAVE_CHILD:

            TIME_POINT_CHILD_OWN = data["timestamp"]

            if data["tag"] in Tag.TAG_STOP.value:

                if DEDUP_EVENT_PLAYER == data["id"]:
                    pass
                else:
                    DEDUP_EVENT_PLAYER = data["id"]
                    TIME_POINT_CHILD = data["timestamp"]
                    COUNT_POINT_CHILD += 1
                    print("line 350:", data["id"], COUNT_POINT_CHILD, " in ", ACTION_PER_POINT_CHILD)

        elif "child" not in player_id_of_event:
            TIME_POINT_PLAYER_OWN = data["timestamp"]

            if data["tag"] in Tag.TAG_STOP.value:

                if DEDUP_EVENT_PLAYER == data["id"]:
                    pass
                else:
                    DEDUP_EVENT_PLAYER = data["id"]
                    TIME_POINT_PLAYER = data["timestamp"]
                    COUNT_POINT_PLAYER += 1
                    print("line 350:", data["id"], COUNT_POINT_PLAYER, " in ", ACTION_PER_POINT_PLAYER)
    # if not RUNNING:
    #     RUNNING = True
    #     ticktack_handler(data)
    #     RUNNING = False

    ticktack_handler(data)
    # if lock.acquire(blocking=False):
    #     try:
    #         # Xử lý sự kiện
    #         print(f"Start handling event {data['id']}")
    #         ticktack_handler(data)
    #         # print(f"Finished handling event {data['id']}")
    #     finally:
    #         lock.release()
    # return
    # print(f"Skipping event {data['id']} because handler is busy")
    #todo: fix sao cho cac event ko overlap

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
    print(data, "player", ACTION_PER_POINT_PLAYER, "child", ACTION_PER_POINT_CHILD)
    emit_event(event=DRIVE_EVENT, data=data)


def emit_register(game_id: str, god_type: int):
    emit_event(event=REGISTER_EVENT, data={"gameId": game_id, "type": god_type})


def emit_action(data: dict):
    emit_event(event=ACTION_EVENT, data=data)


if __name__ == "__main__":
    connect_server()
    emit_join_game(game_id=GAME_ID, player_id=PLAYER_ID)
