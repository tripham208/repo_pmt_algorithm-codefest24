from collections import deque

from lib.model.dataclass import Locker, Map
from lib.model.enum.action import Action
from lib.model.enum.gameobjects import Objects


def bfs_possible_position(start: list, locker: Locker, base_map: Map, is_child: bool = False,
                          player_another_pos: list = None, deep: int = 4) -> dict:
    lock_duplicate = {tuple(start)}

    queue = deque([[start, 0]])

    possible_pos = {
        "lv0": [start],
        "lv1": [],
        "lv2": [],
        "lv3": [],
        "lv4": [],
        "lv5": [],
    }

    while queue:
        # print(queue)
        current_status = queue.popleft()

        for act in Action.MOVE.value:
            # print(current_status, act)
            new_pos_player = [sum(i) for i in zip(current_status[0], act)]
            new_deep = current_status[1] + 1
            new_pos_tuple = tuple(new_pos_player)
            if (
                    new_pos_tuple in lock_duplicate
                    or base_map.get_obj_map(new_pos_player) in Objects.BFS_BLOCK.value
                    or new_pos_tuple in locker.danger_pos_lock_bfs
                    or new_deep > deep
                    # or new_pos_player == POS_ENEMY
            ):
                continue

            lock_duplicate.add(new_pos_tuple)
            possible_pos[f"lv{new_deep}"].append(new_pos_tuple)
            queue.append([new_pos_player, new_deep])

    return possible_pos
