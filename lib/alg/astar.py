from heapq import heappop, heappush

from lib.model.dataclass import Locker, Map
from lib.model.enum.action import get_move_out_zone
from lib.utils.map import euclid_distance, is_zone


def a_star_optimized(start: list, target: list[int, int], locker: Locker, base_map: Map):
    queue = [(euclid_distance(start, target), start, [start], [])]
    lock_duplicate = {tuple(start)}

    acts = get_move_out_zone(is_zone(pos=start, size=[base_map.rows, base_map.cols]))
    # print(start, target)
    while queue:
        _, current_pos, pos_list, act_list = heappop(queue)

        if euclid_distance(current_pos, target) == 1:
            return act_list, pos_list

        for act in acts:

            new_pos_player = [sum(i) for i in zip(current_pos, act)]
            new_pos_lock = tuple(new_pos_player)

            if (
                    new_pos_player in locker.danger_pos_lock_bfs
                    or base_map.get_obj_map(new_pos_player) in locker.a_star_lock
                    or new_pos_player in locker.pos_lock
                    or new_pos_lock in lock_duplicate
            ):
                continue

            lock_duplicate.add(new_pos_lock)
            new_pos_list = pos_list + [new_pos_player]
            new_act_list = act_list + [act]

            if base_map.get_obj_map(new_pos_player) == 3:
                dis = euclid_distance(new_pos_player, target) + 1.5
            # elif base_map.get_obj_map(new_pos_player) == 2:
            #     dis = euclid_distance(new_pos_player, target) + 1.5
            else:
                dis = euclid_distance(new_pos_player, target)
            heappush(queue, (dis, new_pos_player, new_pos_list, new_act_list))

    return [], []
