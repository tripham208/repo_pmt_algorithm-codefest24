import socketio

from lib.alg.astar import a_star_optimized
from lib.alg.bfs import bfs_dq
from lib.model.dataclass import *
from lib.model.enum.range import BombRange
from lib.utils.map import euclid_distance
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
        if player["id"] in PLAYER_ID and not player["isChild"]:
            PLAYER.position = [player["currentPosition"]["row"], player["currentPosition"]["col"]]
            PLAYER.power = player["power"]
            PLAYER.score = player["score"]
            PLAYER.lives = player["lives"]
            if not PLAYER.has_full_marry_items:
                PLAYER.rice = player["stickyRice"]
                PLAYER.cake = player["chungCake"]
                PLAYER.elephant = player["elephant"]
                PLAYER.rooster = player["rooster"]
                PLAYER.horse = player["horse"]
                if PLAYER.owned_marry_items == 5:
                    PLAYER.has_full_marry_items = True
        elif player["id"] in PLAYER_ID and player["isChild"]:
            PLAYER_CHILD.position = [player["currentPosition"]["row"], player["currentPosition"]["col"]]
            PLAYER_CHILD.power = player["power"]
        elif player["id"] not in PLAYER_ID and player["isChild"]:
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
    global MAP, EVALUATED_MAP

    MAP.cols = data["map_info"]["size"]["cols"]
    MAP.cols = data["map_info"]["size"]["rows"]
    MAP.map = data["map_info"]["map"]
    MAP.bombs = data["map_info"]["bombs"]
    MAP.spoils = data["map_info"]["spoils"]

    paste_player_data(players=data["map_info"]["players"])

    EVALUATED_MAP.reset_point_map(cols=MAP.cols, rows=MAP.rows)
    EVALUATED_MAP.set_point_map(base_map=MAP, status=PLAYER)

def get_lock_bombs(base_map: Map):
    pos_danger = []
    for bomb in base_map.bombs:
        power = bomb.get("power", 0)
        bomb_range = BombRange[f'LV{power}'].value
        pos_danger += [[bomb["row"], bomb["col"]]]
        is_danger = bomb.get("remainTime", 0) < 1000

        if not is_danger:
            continue

        for i in bomb_range:
            for j in i:
                pos = [[bomb["row"] + j[0]], [bomb["col"] + j[1]]]
                if base_map.get_obj_map(pos) in Objects.BOMB_NO_DESTROY.value:
                    break
                pos_danger.append(pos)

    return pos_danger
# EVENT HANDLER

DIRECTION_HIST = []


def ticktack_handler(data):
    global PLAYER, ENEMY, PLAYER_CHILD, ENEMY_CHILD
    global MAP, EVALUATED_MAP


def get_case_action() -> tuple[int, dict]:
    if euclid_distance(PLAYER.position, ENEMY.position) <= 4:
        return 1, {}
    '''
    if PLAYER.power > 1:
        for pos in AroundRange.LV1.value:
            if MAP.get_obj_map([sum(i) for i in zip(PLAYER.position, pos)]) == Objects.BALK.value:
                return 1, {}
    '''
    val_pos = EVALUATED_MAP.get_val_road(PLAYER.position)

    if val_pos != 0:
        return 1, {}
    else:
        return 2, {}


def get_action(case, param: dict) -> list:
    """
    1 -> MAX \n
    2 -> BFS \n
    2 -> A STAR \n
    :param param:
    :param case:
    :return:
    """
    match case:
        case 1:
            pass
        case 2:
            return bfs_dq(start=PLAYER.position, locker=LOCKER, base_map=MAP, eval_map=EVALUATED_MAP)
        case 4:
            return a_star_optimized(start=PLAYER.position, locker=LOCKER, base_map=MAP,
                                    target=param.get("target", PLAYER.position))


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
