import sys
import threading
import time

import socketio

from lib.alg.astar import a_star_optimized
from lib.alg.bfs_action import bfs_dq, bfs_dq_out_danger
from lib.alg.max import max_val, gen_hammer
from lib.model.dataclass import *
from lib.model.enum.action import Action, Attack
from lib.model.enum.gameobjects import Tag, Time
from lib.model.enum.range import BombRange
from lib.utils.generator import gen_direction, gen_drive_data, gen_action_data
from lib.utils.map import euclid_distance, find_index, prepare_action
from lib.utils.printer import pr_green, pr_yellow, pr_red
from match import *

# MAP
MAP = Map()
EVALUATED_MAP = EvaluatedMap()
SHARE_ENV = ShareEnv()

# PLAYER
PLAYER = Player(position=[])  # [row,col]
ENEMY = Player(position=[])
PLAYER_CHILD = Player(position=[0, 0])
ENEMY_CHILD = Player(position=[0, 0])

LOCKER = Locker(a_star_lock=Objects.A_STAR_PHASE1_LOCK.value)
LOCKER_CHILD = Locker(a_star_lock=Objects.A_STAR_PHASE2_LOCK.value)

HAVE_CHILD = False
ENEMY_NOT_IN_MAP = True


def check_id_child(pid) -> bool:
    if (
            (pid in PLAYER_ID or pid[0:10] in PLAYER_ID)
            and "child" in pid
    ):
        return True
    return False


# PASTE DATA
def paste_player_data(players):
    global PLAYER, ENEMY, HAVE_CHILD, ENEMY_NOT_IN_MAP
    ENEMY_NOT_IN_MAP = True

    ENEMY.position = [0, 0]
    ENEMY.is_stun = True
    ENEMY_CHILD.position = [0, 0]
    ENEMY_CHILD.is_stun = True

    for player in players:
        # print(player["id"],check_id_child(player["id"]))
        if player["id"] in PLAYER_ID and not player.get("isChild", False):
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

        elif check_id_child(player["id"]) and player.get("isChild", False):
            # print("paste_player Child", player["currentPosition"])
            PLAYER_CHILD.position = [player["currentPosition"]["row"], player["currentPosition"]["col"]]
            PLAYER_CHILD.power = player["power"]
            PLAYER_CHILD.cur_weapon = player["currentWeapon"]
            PLAYER_CHILD.owner_weapon = player["ownerWeapon"]
            PLAYER_CHILD.is_child = player["isChild"]
            PLAYER_CHILD.time_to_use_special_weapons = player["timeToUseSpecialWeapons"]
            HAVE_CHILD = True
        elif player["id"] not in PLAYER_ID and player.get("isChild", False):
            # print("paste_ENEMY_CHILD", player)
            ENEMY_CHILD.position = [player["currentPosition"]["row"], player["currentPosition"]["col"]]
            ENEMY_CHILD.power = player["power"]
            ENEMY_CHILD.is_stun = player["isStun"]
        else:
            # print("paste_ENEMY", player)
            ENEMY.lives = player["lives"]
            ENEMY_CHILD.lives = player["lives"]
            ENEMY.position = [player["currentPosition"]["row"], player["currentPosition"]["col"]]
            ENEMY.power = player["power"]
            ENEMY.has_transform = player["hasTransform"]
            ENEMY.transform_type = player.get("transformType", 0)
            ENEMY.is_stun = player["isStun"]
            ENEMY_NOT_IN_MAP = False
    # print(PLAYER)
    # print(PLAYER_CHILD)
    # print(ENEMY)
    # print(ENEMY_CHILD)


def paste_locker(locker, pos_lock, lock_danger, pos_warning, pos_all):
    locker.pos_lock = pos_lock
    locker.danger_pos_lock_max = lock_danger
    locker.danger_pos_lock_bfs = lock_danger
    locker.warning_pos_bfs = pos_warning
    locker.warning_pos_max = pos_warning
    locker.all_bomb_pos = pos_all
    # renew
    locker.another = {
        "trigger_by_point": False,
        "unlock_brick": False,
    }
    locker.dedup_act = []


def paste_update(data):
    """

    :param data:
    :return:
    """
    global MAP, EVALUATED_MAP, LOCKER, LOCKER_CHILD

    MAP.cols = data["map_info"]["size"]["cols"]
    MAP.rows = data["map_info"]["size"]["rows"]
    MAP.map = data["map_info"]["map"]
    MAP.bombs = data["map_info"]["bombs"]
    MAP.spoils = data["map_info"]["spoils"]
    MAP.hammers = data["map_info"]["weaponHammers"]
    MAP.winds = data["map_info"]["weaponWinds"]

    check_hammer_timeout(hammers=MAP.hammers)

    paste_player_data(players=data["map_info"]["players"])

    if PLAYER.transform_type == 1:
        PLAYER.can_use_god_attack = False
        PLAYER_CHILD.can_use_god_attack = False

        if data["timestamp"] - CHECKPOINT_WEAPON["player_god"] > Time.HAMMER.value:
            PLAYER.can_use_god_attack = True
        if data["timestamp"] - CHECKPOINT_WEAPON["child_god"] > Time.HAMMER.value:
            PLAYER_CHILD.can_use_god_attack = True
    # print("146",data["timestamp"] , CHECKPOINT_PLAYER["timestamp_wooden"], data["timestamp"] - CHECKPOINT_PLAYER["timestamp_wooden"])
    if data["timestamp"] - CHECKPOINT_PLAYER["timestamp_wooden"] < Time.WOODEN.value:
        PLAYER.remember_face = True
    else:
        PLAYER.remember_face = False
    if HAVE_CHILD:
        if data["timestamp"] - CHECKPOINT_CHILD["timestamp_wooden"] < Time.WOODEN.value:
            PLAYER_CHILD.remember_face = True
        else:
            PLAYER_CHILD.remember_face = False

    EVALUATED_MAP.reset_point_map(cols=MAP.cols, rows=MAP.rows)
    EVALUATED_MAP.set_point_map(base_map=MAP, status=PLAYER)

    lock_danger, pos_warning, pos_all = get_lock_bombs(base_map=MAP)

    pos_lock_player = lock_danger + [PLAYER_CHILD.position, ENEMY.position, ENEMY_CHILD.position]
    pos_lock_child = lock_danger + [PLAYER.position, ENEMY.position, ENEMY_CHILD.position]

    paste_locker(LOCKER, pos_lock_player, lock_danger, pos_warning, pos_all)
    paste_locker(LOCKER_CHILD, pos_lock_child, lock_danger, pos_warning, pos_all)

    if ENABLE_DEDUP:
        LOCKER.dedup_act = DEDUP["player_max"]
        LOCKER_CHILD.dedup_act = DEDUP["child_max"]
        DEDUP["player_max"] = []
        DEDUP["child_max"] = []

    # case vẫn tính đc đường dù bị bomb chặn => dừng ở vị trí bị lock

    pr_yellow(f"spoil {MAP.spoils}")
    pr_yellow(f"bombs {MAP.bombs}")
    pr_yellow(f"hammers {MAP.hammers}")
    pr_yellow(f"wind {MAP.winds}")

    print(LOCKER)
    print(LOCKER_CHILD)


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

        if bomb.get("playerId") in PLAYER_ID and bomb.get("remainTime", 0) >= 0:  # =0 check xem bomb noor chuwa
            PLAYER.has_bomb = False
        elif check_id_child(bomb.get("playerId")) and bomb.get("remainTime", 0) >= 0:
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


# SHARE ENV
def reset_share_env_by_player(child: bool = False):
    global SHARE_ENV
    if child:
        SHARE_ENV.child_used_pos = []
        SHARE_ENV.child_targeted_boxes = []
    else:
        SHARE_ENV.player_used_pos = []
        SHARE_ENV.player_targeted_boxes = []


# EVENT HANDLER
def set_bonus_point_road(pos_list, start, x: int):
    global EVALUATED_MAP
    for pos in pos_list:
        EVALUATED_MAP.set_val_player(pos, euclid_distance(start, pos) * x)


def set_road_to_badge():
    global MAP, PLAYER, LOCKER, EVALUATED_MAP
    badges = find_index(MAP.map, 6)
    pr_yellow(badges)
    nearest_badge = []
    dis = 100
    MAP.badges = badges
    for pos in badges:
        tmp_dis = euclid_distance(PLAYER.position, pos)
        if dis > tmp_dis:
            dis = tmp_dis
            nearest_badge = pos
    LOCKER.a_star_lock = Objects.A_STAR_PHASE1_LOCK.value  # lock phase 1
    act_list, pos_list = get_action(case=4, param={"target": nearest_badge})
    # pr_red(f"astar {pos_list}")
    # print(act_list)
    set_bonus_point_road(pos_list, PLAYER.position, 100)


def get_action(case, param: dict = None):
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
            act_list, pos_list = max_val(
                base_map=MAP,
                evaluated_map=EVALUATED_MAP,
                locker=LOCKER,
                player=PLAYER,
                enemy=ENEMY,
                player_another=PLAYER_CHILD,
                enemy_child=ENEMY_CHILD,
                share_env=SHARE_ENV
            )
            end_time = time.time()
            check = end_time - start_time

            pr_green(f"Original max_val result taken: {end_time - start_time} seconds")
            if check >= 0.25:
                return [], []

            SHARE_ENV.player_used_pos = pos_list
            SHARE_ENV.player_targeted_boxes = LOCKER.another.get("pos_des_by_bomb", [])
            return act_list, pos_list
        case 2:
            if not HAVE_CHILD:
                return bfs_dq(start=PLAYER.position, locker=LOCKER, base_map=MAP, eval_map=EVALUATED_MAP)
            else:
                return bfs_dq(start=PLAYER.position, locker=LOCKER, base_map=MAP, eval_map=EVALUATED_MAP,
                              player_another_pos=PLAYER_CHILD.position)

        case 4:
            return a_star_optimized(
                start=PLAYER.position, locker=LOCKER, base_map=MAP, target=param.get("target", PLAYER.position)
            )
        case 10:
            start_time = time.time()
            act_list, pos_list = max_val(
                base_map=MAP,
                evaluated_map=EVALUATED_MAP,
                locker=LOCKER_CHILD,
                player=PLAYER_CHILD,
                enemy=ENEMY,
                player_another=PLAYER,
                enemy_child=ENEMY_CHILD,
                share_env=SHARE_ENV
            )
            end_time = time.time()
            SHARE_ENV.child_used_pos = pos_list
            SHARE_ENV.child_targeted_boxes = LOCKER.another.get("pos_des_by_bomb", [])
            pr_green(f"Original max_val result taken: {end_time - start_time} seconds")
            return act_list, pos_list
        case 20:
            return bfs_dq(start=PLAYER_CHILD.position, locker=LOCKER_CHILD, base_map=MAP, eval_map=EVALUATED_MAP,
                          is_child=True, player_another_pos=PLAYER.position)

        case 40:
            return a_star_optimized(
                start=PLAYER_CHILD.position, locker=LOCKER_CHILD, base_map=MAP,
                target=param.get("target", PLAYER_CHILD.position)
            )


BOX_CLEARED = False


def set_road_to_point(start, child: bool = False):
    global BOX_CLEARED
    if not child:
        act_list, pos_list = get_action(case=2)
        print(pos_list)
        if len(pos_list) == 0:
            BOX_CLEARED = True
        else:
            BOX_CLEARED = False
        set_bonus_point_road(pos_list, start, 100)
    else:
        act_list, pos_list = get_action(case=20)
        print(pos_list)
        set_bonus_point_road(pos_list, start, 100)


def set_road_to_enemy_child(start, child: bool = False):
    if not child:
        act_list, pos_list = get_action(case=4, param={"target": ENEMY_CHILD.position})
        print(pos_list)
        set_bonus_point_road(pos_list, start, 50)
    else:
        act_list, pos_list = get_action(case=40, param={"target": ENEMY_CHILD.position})
        print(pos_list)
        set_bonus_point_road(pos_list, start, 50)


def set_road_to_enemy(start, child: bool = False):
    if not child:
        act_list, pos_list = get_action(case=4, param={"target": ENEMY.position})
        print(pos_list)
        set_bonus_point_road(pos_list, start, 50)
    else:
        act_list, pos_list = get_action(case=40, param={"target": ENEMY.position})
        print(pos_list)
        set_bonus_point_road(pos_list, start, 50)


def process_emit_action(origin_act_list, child: bool = False):
    global CHECKPOINT_PLAYER, CHECKPOINT_CHILD
    global LOCKER, LOCKER_CHILD

    info, act_list = prepare_action(origin_act_list)
    # print(act_list)
    # print(info)
    if info["switch"]:
        emit_action(gen_action_data(action=Action.SWITCH_WEAPON.value, child=child))

    if info["use_god_attack"]:
        if info["god_attack"] == Attack.HAMMER.value:
            if not child:
                pos = LOCKER.another.get("hammer")
            else:
                pos = LOCKER_CHILD.another.get("hammer")
            if pos:
                payload = gen_hammer(pos)
                print(payload)
                # sys_exit()
                emit_action(gen_action_data(action=Action.USE_WEAPON.value, payload=payload, child=child))
    print(LOCKER.another)
    print(LOCKER_CHILD.another)
    if not child:
        direction = handle_info_action(CHECKPOINT_PLAYER, info, act_list)
    else:
        direction = handle_info_action(CHECKPOINT_CHILD, info, act_list)
    # print(act_list)
    if ENABLE_DEDUP:
        dedup_action(act_list, child=child)
    drive_data = gen_drive_data(direction, child=child)
    emit_drive(drive_data)
    origin_pos = PLAYER.position if not child else PLAYER_CHILD.position
    if (
            info["attack"] == Attack.WOODEN.value
            and (direction == 'b'
            #  or (len(direction) == 2
            #  and direction[0] == 'b'
            #  and MAP.get_obj_map(next_pos(origin_pos, FaceAction.FACE_ACTION.value[int(direction[1])])) == 3)
    ) or direction == ''
    ):  # todo time in case ~'b1' chưa khớp
        if child:
            pr_red("set_range_time_no_direction child")
            set_range_time_no_direction("child")
        else:
            pr_red("set_range_time_no_direction")
            set_range_time_no_direction("player")


def handle_info_action(checkpoint: dict, info: dict, act_list):
    if info["reface"]:
        direction = gen_direction(act_list)
        checkpoint["action_per_emit"] = len(direction)
    elif info["attack"] == Attack.WOODEN.value:
        direction = gen_direction(act_list)
        checkpoint["action_per_emit"] = len(direction)
    elif info["use_god_attack"]:
        direction = gen_direction(act_list)
        checkpoint["action_per_emit"] = len(direction)
    elif info["attack"] == Attack.BOMB.value:
        direction = gen_direction(act_list)
        checkpoint["action_per_emit"] = info["drop"]
    else:
        direction = gen_direction(act_list[0:info["drop"]])
        checkpoint["action_per_emit"] = info["drop"]

    checkpoint["action_per_emit"] = max(checkpoint["action_per_emit"], 1)
    checkpoint["count_action"] = 0

    return direction


ENABLE_DEDUP = True
DIRECTION_HIST_PLAYER = []
DIRECTION_HIST_CHILD = []
# TODO DEDUP MUL
UNLOCK = 6
COUNT_UNLOCK = 0
DEDUP = {
    "player_max": [],
    "child_max": []
}


def dedup_action(act_list, child=False):
    global DIRECTION_HIST_PLAYER, DIRECTION_HIST_CHILD
    global CHECKPOINT_PLAYER
    if not child:
        DIRECTION_HIST_PLAYER.append(act_list)
        if len(DIRECTION_HIST_PLAYER) > 7:
            if DIRECTION_HIST_PLAYER.count(act_list) >= 4:
                DEDUP["player_max"].append(act_list)
            DIRECTION_HIST_PLAYER.pop(0)
    else:
        DIRECTION_HIST_CHILD.append(act_list)
        if len(DIRECTION_HIST_CHILD) > 7:
            if DIRECTION_HIST_CHILD.count(act_list) >= 4:
                DEDUP["player_max"].append(act_list)
            DIRECTION_HIST_CHILD.pop(0)


list_skip = [
    "x"
]

CHECKPOINT_PLAYER = {
    "action_per_emit": 1,
    "timestamp_nearest_stop": 0,  # TIME STOP TAG NEAREST
    "timestamp_own": 0,  # TIME EVENT OWN
    "count_action": 0,
    "timestamp_wooden": 0  # để đây vì lười refactor; remember face when wait wooden timeout
}
CHECKPOINT_CHILD = {
    "action_per_emit": 1,
    "timestamp_nearest_stop": 0,
    "timestamp_own": 0,
    "count_action": 0,
    "timestamp_wooden": 0  # để đây vì lười refactor
}

CHECKPOINT_WEAPON = {
    "player_god": 0,
    "child_god": 0,
}


def check_hammer_timeout(hammers):
    global CHECKPOINT_WEAPON
    for hammer in hammers:
        if hammer.get("playerId") in PLAYER_ID:
            CHECKPOINT_WEAPON["player_god"] = hammer.get("createdAt")
        if check_id_child(hammer.get("playerId")):
            CHECKPOINT_WEAPON["child_god"] = hammer.get("createdAt")


EXIT = 0
ENABLE_EXIT = True


def sys_exit():
    global EXIT
    if ENABLE_EXIT:
        if EXIT == 0:
            sys.exit()
        else:
            EXIT += 1


DRIVE_HIST_PLAYER = []
DRIVE_HIST_CHILD = []

# all action another / check from timestamp_nearest_stop
RANGE_TIME = {
    "child": 500,
    "player": 500
}
# all event by  player
RANGE_TIME_OWN = {
    "child": 400,
    "player": 400
}


def set_range_time_no_direction(type_set: str):
    global RANGE_TIME, RANGE_TIME_OWN
    RANGE_TIME[type_set] = 400
    RANGE_TIME_OWN[type_set] = 300


def reset_range_time(type_set: str):
    global RANGE_TIME, RANGE_TIME_OWN
    RANGE_TIME[type_set] = 500
    RANGE_TIME_OWN[type_set] = 400


# todo check start di chuyen, bomb ddeer nhieeu ac tion hown
def check_valid_event(checkpoint: dict, data, type_get: str):
    return (
            checkpoint["count_action"] == checkpoint["action_per_emit"]
            or data["timestamp"] - checkpoint["timestamp_own"] > RANGE_TIME_OWN[type_get]
            or data["timestamp"] - checkpoint["timestamp_nearest_stop"] > RANGE_TIME[type_get]
    )


def set_road_to_badge2():
    global MAP, PLAYER, LOCKER, EVALUATED_MAP
    badges = find_index(MAP.map, 6)
    pr_yellow(badges)
    nearest_badge = []
    MAP.badges = badges
    for pos in badges:
        nearest_badge = pos
    LOCKER.a_star_lock = Objects.A_STAR_PHASE2_LOCK.value  # lock phase 1
    act_list, pos_list = get_action(case=4, param={"target": nearest_badge})
    set_bonus_point_road(pos_list, PLAYER.position, 100)


def ticktack_handler(data):
    global HAVE_CHILD, CHECK_COUNT
    global CHECKPOINT_PLAYER, CHECKPOINT_CHILD
    is_paste_update = False
    if check_valid_event(CHECKPOINT_PLAYER, data, "player"):  # and False
        pr_red("process PLAYER")

        if not is_paste_update:
            paste_update(data)
            is_paste_update = True

        if CHECKPOINT_PLAYER["count_action"] == CHECKPOINT_PLAYER["action_per_emit"]:
            pr_yellow("player trigger by point")
            LOCKER.another["trigger_by_point"] = True
        if data["timestamp"] - CHECKPOINT_PLAYER["timestamp_own"] > RANGE_TIME_OWN["player"]:
            pr_yellow("player trigger by timeout own")
        if data["timestamp"] - CHECKPOINT_PLAYER["timestamp_nearest_stop"] > RANGE_TIME["player"]:
            pr_yellow("player trigger by timeout")

        CHECKPOINT_PLAYER["timestamp_nearest_stop"] = data["timestamp"]
        CHECKPOINT_PLAYER["action_per_emit"] = 1
        reset_range_time("player")
        # print(LOCKER)

        if PLAYER.position in LOCKER.danger_pos_lock_max:
            pr_red("outtttt")
            act_list = bfs_dq_out_danger(PLAYER.position, LOCKER.danger_pos_lock_max, MAP)
        else:
            if PLAYER.has_full_marry_items and HAVE_CHILD == False and ENEMY_NOT_IN_MAP == False:
                emit_action(gen_action_data(action=Action.MARRY_WIFE.value))
                return

            if not PLAYER.has_transform:  # todo :check map 2 cái có gần nhau ko thì fi đến chỗ cái kia
                set_road_to_badge()

            # if PLAYER.has_transform and len(MAP.badges) > 0:
            #     set_road_to_badge2()

            if EVALUATED_MAP.get_val_player(PLAYER.position) <= 0:
                print("find road")
                set_road_to_point(PLAYER.position)
            reset_share_env_by_player()

            act_list, pos_list = get_action(1)
            if not act_list:
                LOCKER.another["unlock_brick"] = True
                act_list, pos_list = get_action(1)
            if BOX_CLEARED and PLAYER.score < ENEMY.score:
                set_road_to_enemy_child(PLAYER.position)

        # sys_exit()
        if act_list and not STOP_THREADS_PLAYER:
            process_emit_action(act_list)
    # CHILD
    # HAVE_CHILD = True   enable khi chỉ muon run child
    if check_valid_event(CHECKPOINT_CHILD, data, "child") and HAVE_CHILD:
        pr_red("process child")

        if not is_paste_update:
            paste_update(data)

        if CHECKPOINT_CHILD["count_action"] == CHECKPOINT_CHILD["action_per_emit"]:
            pr_yellow("CHILD trigger by point")
            LOCKER_CHILD.another["trigger_by_point"] = True
        if data["timestamp"] - CHECKPOINT_CHILD["timestamp_own"] > RANGE_TIME_OWN["child"]:
            pr_yellow(f"CHILD trigger by timeout own{data["timestamp"], CHECKPOINT_CHILD["timestamp_own"]}")
        if data["timestamp"] - CHECKPOINT_CHILD["timestamp_nearest_stop"] > RANGE_TIME["child"]:
            pr_yellow("CHILD trigger by timeout")

        CHECKPOINT_CHILD["timestamp_nearest_stop"] = data["timestamp"]
        CHECKPOINT_CHILD["action_per_emit"] = 1
        reset_range_time("child")

        if PLAYER_CHILD.position in LOCKER_CHILD.danger_pos_lock_max:
            pr_red("CHILD outtttt")
            act_list = bfs_dq_out_danger(PLAYER_CHILD.position, LOCKER_CHILD.danger_pos_lock_max, MAP)
        else:
            if EVALUATED_MAP.get_val_player(PLAYER_CHILD.position) <= 0:
                print("chil road to point")
                set_road_to_point(PLAYER_CHILD.position, child=True)
            act_list, pos_list = get_action(10)
            if not act_list:
                LOCKER.another["unlock_brick"] = True
                act_list, pos_list = get_action(10)
        reset_share_env_by_player(child=True)
        # sys_exit()
        if CHECK_CHILD_LAGGING:
            if not act_list:
                CHECK_COUNT += 1
            if CHECK_COUNT == 10:
                set_road_to_enemy(PLAYER_CHILD.position, child=True)
                get_action(10)
        if act_list and not STOP_THREADS_CHILD:
            process_emit_action(act_list, child=True)


# TODO : CHILD BỊ treo
CHECK_CHILD_LAGGING = False
CHECK_COUNT = 0

# SOCKET HANDLER
sio = socketio.Client()


def check_ticktack_event(checkpoint: dict, data):
    checkpoint["timestamp_own"] = data["timestamp"]

    if data["tag"] in Tag.TAG_STOP.value:
        checkpoint["timestamp_nearest_stop"] = data["timestamp"]
        checkpoint["count_action"] += 1
        if data["tag"] == "wooden-pestle:setup":
            checkpoint["timestamp_wooden"] = data["timestamp"]


@sio.event
def connect():
    print("connection established")


@sio.event
def disconnect():
    print("disconnected from server")


@sio.on(event=JOIN_GAME_EVENT)
def event_handle(data):
    print(f"joined game:{data}")
    emit_register(game_id=GAME_ID, god_type=CURRENT_GOD)


RUNNING = False

lock = threading.Lock()
ts_god = 0
range_time_god = 400


def check_in_god(player_pos, base_map: Map, ts, child=False):
    global STOP_THREADS_CHILD, STOP_THREADS_PLAYER, ts_god
    if ts - ts_god > range_time_god:
        god_pos = base_map.get_pos_god_weapon
        print(player_pos, god_pos)
        if player_pos in god_pos:
            if child:
                act_list = bfs_dq_out_danger(PLAYER_CHILD.position, god_pos, MAP)
            else:
                act_list = bfs_dq_out_danger(PLAYER.position, god_pos, MAP)
            if act_list:
                if child:
                    STOP_THREADS_CHILD = True
                else:
                    STOP_THREADS_PLAYER = True
                pr_red(f"{child} in, {act_list}")
                # drop old drive
                drive_data = gen_drive_data("x", child=child)
                emit_drive(drive_data)
                ts_god = ts
                process_emit_action(act_list, child)
                if child:
                    STOP_THREADS_CHILD = False
                else:
                    STOP_THREADS_PLAYER = False


def is_have_god(data):
    if len(data["map_info"]["weaponHammers"]) > 0 or len(data["map_info"]["weaponWinds"]) > 0:
        return True
    else:
        return False


def god_handler(data):
    paste_update(data)
    print("run god")
    ts = data["timestamp"]
    check_in_god(PLAYER.position, MAP, ts, child=False)
    check_in_god(PLAYER_CHILD.position, MAP, ts, child=True)


STOP_THREADS_PLAYER = False
STOP_THREADS_CHILD = False


@sio.on(event=TICKTACK_EVENT)
def event_handle(data):
    global RUNNING
    global CHECKPOINT_PLAYER, CHECKPOINT_CHILD

    player_id_of_event = data.get("player_id", "no id")
    # print("event_handle", data["id"], "-", data.get("player_id", "no id"), "-", data["tag"], "-", data["timestamp"])

    if is_have_god(data):  # todo
        god_handler(data)

    if player_id_of_event in PLAYER_ID:
        check_ticktack_event(CHECKPOINT_PLAYER, data)
        print("player", data["id"], data["tag"], CHECKPOINT_PLAYER["count_action"], "in",
              CHECKPOINT_PLAYER["action_per_emit"])
    elif check_id_child(player_id_of_event):
        check_ticktack_event(CHECKPOINT_CHILD, data)
        print("child", data["id"], data["tag"], CHECKPOINT_CHILD["count_action"], "in",
              CHECKPOINT_CHILD["action_per_emit"])

    ticktack_handler(data)


@sio.on(event=DRIVE_EVENT)
def event_handle(data):
    pass


@sio.on(event=ACTION_EVENT)
def event_handle(data):
    """
    event hiện tại ko trả về
    :param data:
    :return:
    """
    pr_red(data)


def connect_server():
    sio.connect(URL)


def emit_event(event: str, data: dict):
    sio.emit(event=event, data=data)


def emit_join_game(game_id: str, player_id: str):
    emit_event(event=JOIN_GAME_EVENT, data={"game_id": game_id, "player_id": player_id})


def emit_drive(data: dict):
    print(data, "player", CHECKPOINT_PLAYER["action_per_emit"], "child", CHECKPOINT_CHILD["action_per_emit"])
    emit_event(event=DRIVE_EVENT, data=data)


def emit_register(game_id: str, god_type: int):
    emit_event(event=REGISTER_EVENT, data={"gameId": game_id, "type": god_type})


def emit_action(data: dict):
    print(data)
    emit_event(event=ACTION_EVENT, data=data)


if __name__ == "__main__":
    connect_server()
    emit_join_game(game_id=GAME_ID, player_id=PLAYER_ID)
