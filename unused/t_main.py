# SOCKET HANDLER
import sys
from time import sleep

import socketio


from game.match import DRIVE_EVENT, REGISTER_EVENT, ACTION_EVENT, JOIN_GAME_EVENT, URL, \
    TICKTACK_EVENT
from lib.model.enum.action import Action
from lib.utils.generator import gen_drive_data, gen_action_data

sio = socketio.Client()

GAME_ID = "11fad158-151d-4a85-8f96-c7571ebec11a"
PLAYER_ID = "player1-xxx"
@sio.event
def connect():
    print("connection established")


@sio.event
def disconnect():
    print("disconnected from server")


@sio.on(event=JOIN_GAME_EVENT)
def event_handle(data):
    print(f"joined game:{data}")
    sleep(1)
    print(gen_action_data(action=Action.SWITCH_WEAPON.value, child=False))
    #emit_action(gen_action_data(action=Action.SWITCH_WEAPON.value, child=False))

    emit_drive(gen_drive_data("b11"))
    sleep(0.5)
    emit_drive(gen_drive_data("b"))
    sys.exit()

@sio.on(event=TICKTACK_EVENT)
def event_handle(data):
    pass


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
