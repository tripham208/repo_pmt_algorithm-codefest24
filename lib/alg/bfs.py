from collections import deque
from copy import deepcopy

from lib.model.dataclass import Locker, Map, EvaluatedMap
from lib.model.enum.action import get_move_out_zone
from lib.model.enum.gameobjects import Objects
from lib.utils.map import is_zone, euclid_distance


def bfs(start: list[int], locker: Locker, base_map: Map, eval_map: EvaluatedMap) -> list[int]:
    lock_duplicate = {tuple(start)}

    acts = get_move_out_zone(is_zone(pos=start, size=[base_map.rows, base_map.cols]))
    queue = [[start, []]]  # current pos , action to pos
    act_list = []
    try:
        point, pos_set, end_status = next_pos_bfs(actions=acts, lock_duplicate=lock_duplicate, queue=queue,
                                                  locker=locker, base_map=base_map, eval_map=eval_map)
        if point >= 25:
            act_list = end_status[1]
    except Exception as e:
        print(e)  # lỗi limit  recursion /1000
    finally:
        return act_list


def next_pos_bfs(actions: list, lock_duplicate: set, queue: list[list], locker: Locker, base_map: Map,
                 eval_map: EvaluatedMap):
    current_status = queue.pop(0)

    for act in actions:
        new_pos_player = [sum(i) for i in zip(current_status[0], act)]
        new_pos_tuple = tuple(new_pos_player)

        if (
                new_pos_tuple in lock_duplicate
                or base_map.map[new_pos_player[0]][new_pos_player[1]] in Objects.BFS_BLOCK.value
                or new_pos_tuple in locker.danger_pos_lock_bfs
                # or new_pos_player == POS_ENEMY
        ):
            continue
        point = eval_map.road_map[new_pos_player[0]][new_pos_player[1]]

        new_status = deepcopy(current_status)
        new_status[1].append(act)
        new_status[0] = new_pos_player
        lock_duplicate.add(new_pos_tuple)

        if point >= 25:
            return point, lock_duplicate, new_status

        queue.append(new_status)

    if not queue:
        return 0, lock_duplicate, current_status

    return next_pos_bfs(actions=actions, lock_duplicate=lock_duplicate, queue=queue,
                        locker=locker, base_map=base_map, eval_map=eval_map)


def bfs_dq(start: list[int], locker: Locker, base_map: Map, eval_map: EvaluatedMap, is_child: bool = False,
           player_another_pos: list = None) -> list[int]:
    lock_duplicate = {tuple(start)}

    acts = get_move_out_zone(is_zone(pos=start, size=[base_map.rows, base_map.cols]), is_child=is_child)
    start_status = [start, [], []]
    queue = [start_status]  # current pos , action to pos , pos to pos
    queue = deque(queue)

    point, end_status = next_pos_bfs_dq(actions=acts, lock_duplicate=lock_duplicate, queue=queue,
                                        locker=locker, base_map=base_map, eval_map=eval_map,
                                        player_another_pos=player_another_pos)
    if point >= 25:
        start_status = end_status

    return start_status[1], start_status[2]


def next_pos_bfs_dq(actions: list, lock_duplicate: set, queue: deque, locker: Locker, base_map: Map,
                    eval_map: EvaluatedMap, player_another_pos: list = None):
    current_status = queue[0]

    while queue:
        current_status = queue.popleft()
        for act in actions:
            new_pos_player = [sum(i) for i in zip(current_status[0], act)]
            new_pos_tuple = tuple(new_pos_player)
            if (
                    new_pos_tuple in lock_duplicate
                    or base_map.map[new_pos_player[0]][new_pos_player[1]] in Objects.BFS_BLOCK.value
                    or new_pos_tuple in locker.danger_pos_lock_bfs
                    # or new_pos_player == POS_ENEMY
            ):
                continue

            if player_another_pos is not None and euclid_distance(new_pos_player, player_another_pos) <= 5:
                continue
            else:
                point = eval_map.road_map[new_pos_player[0]][new_pos_player[1]]

            new_status = deepcopy(current_status)
            new_status[1].append(act)
            new_status[2].append(new_pos_player)
            new_status[0] = new_pos_player
            lock_duplicate.add(new_pos_tuple)

            if point >= 25:
                return point, new_status

            queue.append(new_status)

    return 0, current_status


def bfs_around_dq(start: list[int], base_map: Map, eval_map: EvaluatedMap, level_around: int = 0) -> bool:
    lock_duplicate = {tuple(start)}

    acts = get_move_out_zone(is_zone(pos=start, size=[base_map.rows, base_map.cols]))  # get_move_in_zone
    queue = [[start, 0]]  # start level_around = 0
    queue = deque(queue)
    result = False
    try:
        point, _ = next_pos_around_dq(actions=acts, lock_duplicate=lock_duplicate, queue=queue,
                                      base_map=base_map, eval_map=eval_map, level_around=level_around)
        if point != 0:
            result = True
    finally:
        return result


def next_pos_around_dq(actions: list, lock_duplicate: set, queue: deque, base_map: Map,
                       eval_map: EvaluatedMap, level_around: int) -> tuple[int, deque]:
    current_status = queue[0]

    while queue:
        current_status = queue.popleft()
        for act in actions:
            new_pos_player = [sum(i) for i in zip(current_status[0], act)]
            new_pos_tuple = tuple(new_pos_player)

            if (
                    new_pos_tuple in lock_duplicate
                    or base_map.map[new_pos_player[0]][new_pos_player[1]] in Objects.BFS_BLOCK.value
            ):
                continue

            point = eval_map.road_map[new_pos_player[0]][new_pos_player[1]]

            if point == 0 and current_status[1] == level_around:  # check den round n
                continue

            new_status = deepcopy(current_status)
            new_status[1] += 1
            new_status[0] = new_pos_player
            lock_duplicate.add(new_pos_tuple)

            if point != 0:
                return point, new_status

            queue.append(new_status)

    return 0, current_status


def bfs_dq_out_danger(start: list[int], danger_list, base_map: Map):
    lock_duplicate = {tuple(start)}

    acts = get_move_out_zone(is_zone(pos=start, size=[base_map.rows, base_map.cols]))
    start_status = [start, [], []]
    queue = [start_status]  # current pos , action to pos , pos to pos
    queue = deque(queue)

    end_status = next_pos_bfs_dq_out_danger(actions=acts, danger_list=danger_list, lock_duplicate=lock_duplicate,
                                            queue=queue,
                                            base_map=base_map)

    return end_status[1]


def next_pos_bfs_dq_out_danger(actions: list, lock_duplicate: set, queue: deque, base_map: Map,
                               danger_list: list):
    current_status = queue[0]

    while queue:
        current_status = queue.popleft()
        for act in actions:
            new_pos_player = [sum(i) for i in zip(current_status[0], act)]
            new_pos_tuple = tuple(new_pos_player)
            if (
                    new_pos_tuple in lock_duplicate
                    or base_map.map[new_pos_player[0]][new_pos_player[1]] in Objects.BFS_BLOCK.value
            ):
                continue

            new_status = deepcopy(current_status)
            new_status[1].append(act)
            new_status[2].append(new_pos_player)
            new_status[0] = new_pos_player
            lock_duplicate.add(new_pos_tuple)

            if new_pos_player not in danger_list:
                return new_status

            queue.append(new_status)

    return current_status
