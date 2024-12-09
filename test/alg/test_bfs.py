from lib.alg.bfs_action import bfs_dq
from lib.alg.bfs_position import bfs_possible_position
from test import time_function
from test.conftest import *
from unused import bfs
from unused.bfs import bfs_around_dq


def test_bfs(mock_locker, mock_base_map, mock_eval_map):
    start = [0, 0]
    mock_eval_map.player_map[10][10] = 30
    #mock_base_map.map[49][0] = 1222 #~~[-1, 0]
    result_bfs, time_bfs = time_function(bfs, start, mock_locker, mock_base_map, mock_eval_map)
    result_bfs_dq, time_bfs_dq = time_function(bfs_dq, start, mock_locker, mock_base_map, mock_eval_map)
    print()
    print(f"Original  result: {len(result_bfs)}, Time taken: {time_bfs} seconds")
    print()
    print(f"dq  result: {len(result_bfs_dq)}, Time taken: {time_bfs_dq} seconds")


def test_bfs_around_dq(mock_eval_map, mock_base_map):
    start = [15, 15]
    mock_eval_map.player_map[15][18] = 30
    result_bfs, time_bfs = time_function(bfs_around_dq, start, mock_base_map, mock_eval_map)
    print()
    print(f"Original  result: {result_bfs}, Time taken: {time_bfs} seconds")

def test_bfs_possible_position(mock_eval_map, mock_base_map, mock_locker):
    start = [15, 15]
    result_bfs, time_bfs = time_function(bfs_possible_position, start,mock_locker, mock_base_map)
    print()
    print(f"Original  result: {result_bfs}, ")
    print(f"Time taken: {time_bfs} seconds ")