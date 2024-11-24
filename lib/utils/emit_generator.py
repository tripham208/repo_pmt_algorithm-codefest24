from lib.model.enum.action import FaceAction


def gen_direction(list_action: list[list]):
    """
    1 - Move LEFT \n
    2 - Move RIGHT.\n
    3 - Move UP\n
    4 - Move DOWN\n
    b - Use WEAPON\n
    x - Stop Moving\n
    :param list_action: list[list]
    :return: direction
    """
    direction = ""
    for i in list_action:
        match i:
            case [0, -1]:
                direction += "1"
            case [0, 1]:
                direction += "2"
            case [-1, 0]:
                direction += "3"
            case [1, 0]:
                direction += "4"
            case [0, 0]:
                direction += "x"
            case [2, 2]:
                direction += "b" #wooden
            case [3, 3]:
                direction += "b" #bomb
            case FaceAction.UP_V2.value:
                direction += "3"
                break
            case FaceAction.RIGHT_V2.value:
                direction += "2"
                break
            case FaceAction.DOWN_V2.value:
                direction += "4"
                break
            case FaceAction.LEFT_V2.value:
                direction += "1"
                break
    return direction


def gen_drive_data(direction: str, child: bool = False) -> dict:
    return {"direction": direction, "characterType": "child"} if child else {"direction": direction}


def gen_action_data(action: str, mountain_god: bool = False, child: bool = False, payload=None):
    match [action, mountain_god, child]:
        case ["switch weapon", _, True]:
            return {"action": action, "characterType": "child"}
        case ["use weapon", True, True]:
            return {"action": action, "payload": payload, "characterType": "child"}
        case ["use weapon", True, False]:
            return {"action": action, "payload": payload}
        case _:
            return {"action": action}
