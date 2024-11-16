from lib.model.dataclass import Player


def test_player():
    player = Player(position=[0, 0], rice=1, cake=0, elephant=2, rooster=0, horse=0)
    assert player.need_items == [33, 35, 36]
    assert player.owned_marry_items == 2

def a(player):
    player.position = [0, 5]
def b(player):
    player.position = [0, 10]
def test_player2():
    player = Player(position=[0, 0], rice=1, cake=0, elephant=2, rooster=0, horse=0)
    print()
    print(player)
    a(player)
    print()
    print(player)

