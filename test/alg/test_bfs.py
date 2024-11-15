from lib.alg.bfs import bfs, bfs_dq, bfs_around_dq
from test import time_function
from test.conftest import *


def test_bfs(mock_locker, mock_base_map, mock_eval_map):
    start = [0, 0]
    mock_eval_map.road_map[10][10] = 30
    #mock_base_map.map[49][0] = 1222 #~~[-1, 0]
    result_bfs, time_bfs = time_function(bfs, start, mock_locker, mock_base_map, mock_eval_map)
    result_bfs_dq, time_bfs_dq = time_function(bfs_dq, start, mock_locker, mock_base_map, mock_eval_map)
    print()
    print(f"Original  result: {len(result_bfs)}, Time taken: {time_bfs} seconds")
    print()
    print(f"dq  result: {len(result_bfs_dq)}, Time taken: {time_bfs_dq} seconds")


def test_bfs_around_dq(mock_eval_map, mock_base_map):
    start = [15, 15]
    mock_eval_map.road_map[15][18] = 30
    result_bfs, time_bfs = time_function(bfs_around_dq, start, mock_base_map, mock_eval_map)
    print()
    print(f"Original  result: {result_bfs}, Time taken: {time_bfs} seconds")
