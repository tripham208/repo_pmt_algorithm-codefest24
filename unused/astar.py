from copy import deepcopy

from lib.model.dataclass import Locker, Map
from lib.model.enum.action import NextMoveZone
from lib.model.enum.gameobjects import Objects
from lib.utils.map import euclid_distance


def a_star_original(start: list, target: list, locker: Locker, base_map: Map):
    # print(start, target)
    queue = [[start, euclid_distance(start, target), [start], []]]
    # pos , dis, pos_list, act_list

    lock_duplicate = [start]

    while queue:
        current_status = queue.pop(0)
        if current_status[1] == 1:
            return current_status[3]
        for act in NextMoveZone.Z4.value:
            new_pos_player = [sum(i) for i in zip(current_status[0], act)]
            if new_pos_player in locker.danger_pos_lock_bfs:
                continue
            if base_map.map[new_pos_player[0]][new_pos_player[1]] in Objects.NO_DESTROY.value:
                continue
            if new_pos_player in lock_duplicate:
                continue
            lock_duplicate.append(new_pos_player)
            new_status = deepcopy(current_status)

            new_status[0] = new_pos_player
            if base_map.get_obj_map(new_pos_player) == 3:
                new_status[1] = euclid_distance(new_pos_player, target) + 1
            else:
                new_status[1] = euclid_distance(new_pos_player, target)
            new_status[2].append(new_pos_player)
            new_status[3].append(act)
            queue.append(new_status)

        queue.sort(key=lambda x: x[1])
    else:
        return []