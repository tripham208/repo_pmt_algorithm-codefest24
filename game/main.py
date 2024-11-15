import socketio

from lib.model.dataclass import *
from match import *

# MAP
MAP = Map(map=[], bombs=[], spoils=[])
EVALUATED_MAP = EvaluatedMap(player_map=[], enemy_map=[], road_map=[])

# PLAYER
PLAYER = Player(position=[])  # [row,col]
ENEMY = Player(position=[])
PLAYER_CHILD = Player(position=[])
ENEMY_CHILD = Player(position=[])

STATUS_PLAYER = StatusPlayer()
STATUS_ENEMY = StatusPlayer()


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
    EVALUATED_MAP.set_point_map(base_map=MAP,status=STATUS_PLAYER)


# EVENT HANDLER

DIRECTION_HIST = []

def ticktack_handler(data):
    pass


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
