from game.main import PLAYER, ENEMY, EVALUATED_MAP
from lib.model.enum.action import Face
from lib.utils.map import euclid_distance


def get_face(old, new):
    if old[0] == new[0]:
        if old[1] > new[1]:
            return Face.LEFT.value
        elif old[1] < new[1]:
            return Face.RIGHT.value
        else:
            return Face.UNKNOWN.value
    elif old[1] == new[1]:
        if old[0] > new[0]:
            return Face.UP.value
        elif old[0] < new[0]:
            return Face.DOWN.value


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
