from lib.alg.astar import a_star_optimized
from lib.model.dataclass import Locker, Map
from lib.model.enum.gameobjects import Objects
from test import time_function, show_map
from unused.astar import a_star_original

A = [
    [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1
    ],
    [
        1,
        0,
        0,
        3,
        3,
        0,
        3,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        3,
        0,
        3,
        3,
        0,
        0,
        1
    ],
    [
        1,
        0,
        1,
        3,
        2,
        2,
        2,
        2,
        2,
        2,
        0,
        2,
        2,
        2,
        2,
        0,
        2,
        2,
        2,
        2,
        2,
        2,
        3,
        1,
        0,
        1
    ],
    [
        1,
        0,
        2,
        1,
        0,
        0,
        0,
        2,
        2,
        0,
        0,
        2,
        2,
        2,
        2,
        0,
        0,
        0,
        2,
        0,
        0,
        0,
        1,
        2,
        0,
        1
    ],
    [
        1,
        0,
        2,
        2,
        1,
        5,
        0,
        2,
        2,
        0,
        2,
        1,
        1,
        1,
        1,
        2,
        0,
        0,
        2,
        0,
        5,
        1,
        2,
        2,
        0,
        1
    ],
    [
        1,
        0,
        0,
        2,
        2,
        1,
        2,
        2,
        2,
        0,
        2,
        1,
        2,
        2,
        1,
        2,
        0,
        0,
        2,
        2,
        1,
        2,
        2,
        0,
        0,
        1
    ],
    [
        1,
        0,
        0,
        0,
        2,
        3,
        2,
        2,
        0,
        0,
        2,
        2,
        2,
        2,
        2,
        2,
        0,
        0,
        2,
        2,
        3,
        2,
        0,
        0,
        0,
        1
    ],
    [
        1,
        0,
        0,
        0,
        3,
        0,
        3,
        3,
        0,
        0,
        2,
        6,
        0,
        0,
        6,
        2,
        0,
        0,
        3,
        3,
        0,
        3,
        0,
        0,
        0,
        1
    ],
    [
        1,
        0,
        0,
        2,
        2,
        1,
        2,
        2,
        0,
        2,
        2,
        0,
        0,
        0,
        0,
        2,
        2,
        0,
        2,
        2,
        1,
        2,
        2,
        0,
        0,
        1
    ],
    [
        1,
        0,
        2,
        2,
        1,
        5,
        0,
        2,
        0,
        2,
        2,
        0,
        0,
        0,
        0,
        2,
        2,
        0,
        2,
        0,
        5,
        1,
        2,
        2,
        0,
        1
    ],
    [
        1,
        0,
        2,
        1,
        0,
        0,
        0,
        0,
        0,
        3,
        3,
        0,
        3,
        3,
        0,
        3,
        3,
        0,
        0,
        0,
        0,
        0,
        1,
        2,
        0,
        1
    ],
    [
        1,
        0,
        1,
        2,
        2,
        2,
        2,
        2,
        0,
        2,
        2,
        2,
        0,
        0,
        2,
        2,
        2,
        0,
        2,
        2,
        2,
        2,
        2,
        1,
        0,
        1
    ],
    [
        1,
        0,
        0,
        3,
        0,
        3,
        0,
        3,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        3,
        0,
        3,
        0,
        3,
        0,
        0,
        1
    ],
    [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1
    ]
]


def test_astar():
    target = [7, 14]
    start = [8, 23]
    show_map(A)
    locker = Locker(danger_pos_lock_bfs=[], danger_pos_lock_max=[], a_star_lock=Objects.A_STAR_PHASE1_LOCK.value,
                    pos_lock=[])
    base_map = Map(map=A, bombs=[], spoils=[])
    print("D")
    result_original, time_original = time_function(a_star_original, start, target, locker, base_map)
    print("d")
    result_optimized, time_optimized = time_function(a_star_optimized, start, target, locker, base_map)
    print()
    print(f"Original a_star result: {result_original}, Time taken: {time_original} seconds")
    print(f"Optimized a_star result: {result_optimized}, Time taken: {time_optimized} seconds")
