import pytest

from lib.model.dataclass import Locker, Map, EvaluatedMap
from lib.utils.map import create_map_zero

M = "d"


@pytest.fixture
def mock_locker():
    return Locker(danger_pos_lock_bfs=[], danger_pos_lock_max=[], a_star_lock=[],pos_lock=[])


@pytest.fixture
def mock_base_map():
    base_map = Map(map=create_map_zero(50, 50), bombs=[], spoils=[])
    return base_map


@pytest.fixture
def mock_eval_map():
    eval_map = EvaluatedMap(
        player_map=create_map_zero(50, 50),
        enemy_map=create_map_zero(50, 50),
        road_map=create_map_zero(50, 50)
    )
    return eval_map
