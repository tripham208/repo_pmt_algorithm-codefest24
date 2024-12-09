import pytest

from lib.model.dataclass import Locker, Map, EvaluatedMap
from lib.utils.map import create_map_zero

M = "d"


@pytest.fixture
def mock_locker():
    return Locker(danger_pos_lock_bfs=[], danger_pos_lock_max=[], a_star_lock=[], pos_lock=[])


@pytest.fixture
def mock_base_map():
    base_map = Map(map=create_map_zero(50, 50), bombs=[], spoils=[])
    return base_map


@pytest.fixture
def mock_eval_map():
    eval_map = EvaluatedMap(
        enemy_map=create_map_zero(50, 50),
        player_map=create_map_zero(50, 50)
    )
    return eval_map


@pytest.fixture
def mock_fake_map():
    fake_map = [
        # 0  1  2  3  4  5  6  7  8  9 10 11 10 10 14 15 16 17
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 0
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # 1
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # 2
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # 3
        [1, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 1],  # 4
        [1, 0, 0, 0, 0, 0, 0, 3, 0, 0, 3, 2, 0, 0, 0, 0, 1, 1],  # 5
        [1, 0, 0, 5, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 1],  # 6
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # 7
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # 8
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # 9
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # 10
    ]
    base_map = Map(map=fake_map, bombs=[], spoils=[])
    return base_map
