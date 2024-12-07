from lib.model.enum.action import Face


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