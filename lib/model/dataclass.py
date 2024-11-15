from dataclasses import dataclass

from lib.model.enum.gameobjects import MarryItem, Objects
from lib.model.enum.range import AroundRange
from lib.utils.map import create_map_zero


@dataclass
class Map:
    map: list
    bombs: list
    spoils: list
    cols: int = 0
    rows: int = 0
    pos_enemy: list = None
    pos_enemy_child: list = None

    def get_pos_spoils(self) -> list:
        return [[spoil["row"], spoil["col"]] for spoil in self.spoils]


@dataclass
class StatusPlayer:
    transform: bool = False
    can_use_god_attack: bool = False
    can_use_item: bool = False


@dataclass
class Locker:
    danger_pos_lock_max: list
    danger_pos_lock_bfs: list
    a_star_lock: list


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

    def set_point_map(self, base_map: Map, status: StatusPlayer):
        self.__set_road_point(base_map)
        self.__set_addition_point(base_map, status)

    def __set_road_point(self, base_map: Map):
        destructible_values = Objects.DESTRUCTIBLE.value
        around_range_values = AroundRange.LV1_4.value

        for row in range(base_map.rows):
            for col in range(base_map.cols):
                if base_map.map[row][col] in destructible_values:
                    for i in around_range_values:
                        self.road_map[row + i[0]][col + i[1]] = 25

    def __set_addition_point(self, base_map: Map, status: StatusPlayer):
        self.__set_bombs(base_map)
        self.__set_spoils(base_map, status)

    def __set_bombs(self, base_map: Map):
        pass

    def __set_spoils(self, base_map: Map, status: StatusPlayer):
        if status.can_use_item:
            for spoil in base_map.spoils:
                self.road_map[spoil["row"]][spoil["col"]] = 50
                self.player_map[spoil["row"]][spoil["col"]] = 200


@dataclass
class Player:
    position: [int, int]
    god_type: int = 0
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
