from lib.alg.astar import a_star_optimized, a_star_original
from lib.model.dataclass import Locker, Map
from lib.utils.map import create_map_zero
from test import time_function


def test_astar():
    start = [0, 0]
    target = [15, 15]
    locker = Locker(danger_pos_lock_bfs=[], danger_pos_lock_max=[], a_star_lock=[])
    base_map = Map(map=create_map_zero(50, 50), bombs=[], spoils=[])
    print("D")
    result_original, time_original = time_function(a_star_original, start, target, locker, base_map)
    print("d")
    result_optimized, time_optimized = time_function(a_star_optimized, start, target, locker, base_map)
    print()
    print(f"Original a_star result: {1}, Time taken: {time_original} seconds")
    print(f"Optimized a_star result: {1}, Time taken: {time_optimized} seconds")

    improvement = ((time_original - time_optimized) / time_original) * 100
    print(f"Performance improvement: {improvement:.2f}%")
