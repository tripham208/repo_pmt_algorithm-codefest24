from copy import deepcopy
from heapq import heappop, heappush

from lib.model.dataclass import Locker, Map
from lib.model.enum.action import NextMoveZone, get_move_out_zone
from lib.model.enum.gameobjects import Objects
from lib.utils.map import euclid_distance, is_zone


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
            new_status[1] = euclid_distance(new_pos_player, target)
            new_status[2].append(new_pos_player)
            new_status[3].append(act)
            queue.append(new_status)

        queue.sort(key=lambda x: x[1])
    else:
        return []


def a_star_optimized(start: list, target: list[int, int], locker: Locker, base_map: Map):
    queue = [(euclid_distance(start, target), start, [start], [])]
    lock_duplicate = {tuple(start)}

    acts = get_move_out_zone(is_zone(pos=start, size=[base_map.rows, base_map.cols]))
    print(start,target)
    while queue:
        _, current_pos, pos_list, act_list = heappop(queue)

        if euclid_distance(current_pos, target) == 1:
            return act_list, pos_list

        for act in acts:

            new_pos_player = [sum(i) for i in zip(current_pos, act)]
            new_pos_lock = tuple(new_pos_player)

            if (
                    new_pos_player in locker.danger_pos_lock_bfs
                    or base_map.map[new_pos_player[0]][new_pos_player[1]] in locker.a_star_lock
                    or new_pos_lock in lock_duplicate
            ):
                continue

            lock_duplicate.add(new_pos_lock)
            new_pos_list = pos_list + [new_pos_player]
            new_act_list = act_list + [act]
            heappush(queue, (euclid_distance(new_pos_player, target), new_pos_player, new_pos_list, new_act_list))

    return [], []
