from lib.model.dataclass import Player


def test_player():
    player = Player(rice=1, cake=0, elephant=2, rooster=0, horse=0)
    assert player.need_items == [33, 35, 36]
    assert player.owned_marry_items == 2
