from lib.model.enum.gameobjects import MarryItem, AnotherItem
from lib.utils.point import get_point_match_spoil


def test_match_spoil():
    assert get_point_match_spoil(MarryItem.RICE.value) == 50
    assert get_point_match_spoil(MarryItem.CAKE.value) == 100
    assert get_point_match_spoil(MarryItem.ELEPHANT.value) == 300
    assert get_point_match_spoil(MarryItem.ROOSTER.value) == 150
    assert get_point_match_spoil(MarryItem.HORSE.value) == 200
    assert get_point_match_spoil(AnotherItem.SPIRIT_STONE.value) == 150
    assert get_point_match_spoil('unknown_item') == 0
