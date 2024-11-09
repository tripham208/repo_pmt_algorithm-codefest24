from dataclasses import dataclass

from lib.model.enum.gameobjects import MarryItem
from lib.utils.map import create_map_zero


@dataclass
class Map:
    map: list
    bombs: list
    spoils: list
    cols: int = 0
    rows: int = 0


@dataclass
class StatusPlayer:
    transform: bool = False


@dataclass
class EvaluatedMap:
    player_map: list
    enemy_map: list
    road_map: list

    def evaluated_map(self, pos_player: list, pos_enemy: list):
        return sum(
            [
                self.player_map[pos_player[0]][pos_player[1]],
                self.road_map[pos_player[0]][pos_player[1]],
                self.enemy_map[pos_enemy[0]][pos_enemy[1]]
            ]
        )

    def reset_point_map(self, cols, rows):
        self.player_map = create_map_zero(cols, rows)
        self.enemy_map = create_map_zero(cols, rows)
        self.road_map = create_map_zero(cols, rows)

    def set_point_map(self):
        self.set_addition_point()

    def set_addition_point(self):
        self.set_bombs()
        self.set_spoils()

    def set_bombs(self):
        pass

    def set_spoils(self):
        pass


@dataclass
class Player:
    position: [int, int]
    lives: int = 5
    score: int = 0
    power: int = 1
    delay: int = 2000
    rice: int = 0
    cake: int = 0
    elephant: int = 0
    rooster: int = 0
    horse: int = 0
    has_transform: bool = False
    has_full_marry_items: bool = False

    @property
    def owned_marry_items(self) -> int:
        items = [self.rice, self.cake, self.elephant, self.rooster, self.horse]
        return sum(1 for item in items if item > 0)

    @property
    def need_items(self) -> list:
        if self.has_full_marry_items:
            return []
        marry_items = [(self.rice, MarryItem.RICE.value),
                       (self.cake, MarryItem.CAKE.value),
                       (self.elephant, MarryItem.ELEPHANT.value),
                       (self.rooster, MarryItem.ROOSTER.value),
                       (self.horse, MarryItem.HORSE.value)]
        return [item for num_item, item in marry_items if num_item == 0]


@dataclass
class State:
    pos_player: list
    pos_enemy: list
    owner_weapon: list
    cur_weapon: int
    transform_type: int
    time_to_use_special_weapons: int
    face: int = 0  # 0: unknown
    has_transform: bool = False
    power: int = 1
    holy_spirit_stone: int = 0
    is_stun: bool = False
    is_child: bool = False
