from lib.model.enum.gameobjects import MarryItem, AnotherItem
from lib.utils.point import match_spoil


def test_match_spoil():
    assert match_spoil(MarryItem.RICE.value) == 50
    assert match_spoil(MarryItem.CAKE.value) == 100
    assert match_spoil(MarryItem.ELEPHANT.value) == 300
    assert match_spoil(MarryItem.ROOSTER.value) == 150
    assert match_spoil(MarryItem.HORSE.value) == 200
    assert match_spoil(AnotherItem.SPIRIT_STONE.value) == 150
    assert match_spoil('unknown_item') == 0
