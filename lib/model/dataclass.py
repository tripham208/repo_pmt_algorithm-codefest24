from dataclasses import dataclass, field

from lib.model.enum.action import Face
from lib.model.enum.gameobjects import MarryItem, Objects, StatusPoint, Weapon
from lib.model.enum.range import AroundRange, WeaponRange, BombRange
from lib.utils.map import create_map_zero


@dataclass
class Map:
    map: list = field(default_factory=lambda: [])
    bombs: list = field(default_factory=lambda: [])
    spoils: list = field(default_factory=lambda: [])
    cols: int = 0
    rows: int = 0
    up_point: int = 0
    badges: list = field(default_factory=lambda: [])
    hammers: list = field(default_factory=lambda: [])
    winds: list = field(default_factory=lambda: [])

    def get_obj_map(self, pos):
        return self.map[pos[0]][pos[1]]

    def set_val_map(self, pos, val):
        self.map[pos[0]][pos[1]] = val

    @property
    def get_pos_spoils(self) -> list:
        return [[spoil["row"], spoil["col"]] for spoil in self.spoils]

    @property
    def get_pos_bombs(self) -> list:
        return [[bomb["row"], bomb["col"]] for bomb in self.bombs]

    @property
    def get_pos_hammers(self) -> list:
        pos_danger = []
        if self.hammers is not None:
            for hammer in self.hammers:
                destination = hammer.get("destination", {
                    "col": 0,
                    "row": 0,
                })
                destination = [destination["row"], destination["col"]]
                pos_danger += [[sum(i) for i in zip(destination, pos)] for pos in AroundRange.LV2.value]

        return pos_danger

    @property
    def get_pos_winds(self) -> list:
        pos_danger = []
        if self.winds is not None:
            for wind in self.winds:
                direction = wind.get("direction", 0)
                if direction != 0:
                    cur_pos = [wind["currentRow"], wind["currentCol"]]
                    wind_range = WeaponRange[f'WIND_{direction}'].value
                    next_post = [sum(i) for i in zip(cur_pos, wind_range)]
                    while self.get_obj_map(next_post) not in Objects.BOMB_NO_DESTROY.value:
                        pos_danger.append(next_post)
                        next_post = [sum(i) for i in zip(next_post, wind_range)]

        return pos_danger

    @property
    def get_pos_god_weapon(self) -> list:
        pos_danger = self.get_pos_winds + self.get_pos_hammers
        return pos_danger

    @property
    def get_pos_bomb(self) -> dict:
        pos_bomb_dict = {
            "danger": [],
            "warning": [],
            "all": [],
            "destroy": [],
            "new": []
        }
        for bomb in self.bombs:
            power = bomb.get("power", 0)
            bomb_range = BombRange[f'LV{power}'].value
            bomb_pos = [bomb["row"], bomb["col"]]
            pos_bomb_dict["danger"].append(bomb_pos)
            is_warning = bomb.get("remainTime", 0) > 1000

            for i in bomb_range:
                for j in i:
                    pos = [bomb["row"] + j[0], bomb["col"] + j[1]]
                    if self.get_obj_map(pos) in Objects.BOMB_BREAK.value:
                        break
                    if is_warning:
                        pos_bomb_dict["warning"].append(pos)
                    else:
                        pos_bomb_dict["danger"].append(pos)
                    pos_bomb_dict["all"].append(pos)

        return pos_bomb_dict


@dataclass
class Player:
    position: [int, int]
    face: int = Face.UNKNOWN.value
    owner_weapon: list = field(default_factory=lambda: [1])
    cur_weapon: int = 1
    time_to_use_special_weapons: int = 0
    transform_type: int = 0
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
    stone: int = 0
    has_transform: bool = False
    has_bomb: bool = False
    has_full_marry_items: bool = False
    is_stun: bool = False
    is_child: bool = False
    can_use_god_attack: bool = False
    can_use_item: bool = False
    remember_face: bool = False

    def update_face(self, act):
        match act:
            case [-1, 0]:
                self.face = Face.UP.value
            case [0, 1]:
                self.face = Face.RIGHT.value
            case [1, 0]:
                self.face = Face.DOWN.value
            case [0, -1]:
                self.face = Face.LEFT.value
            case [-10, 0]:
                self.face = Face.UP.value
            case [0, 10]:
                self.face = Face.RIGHT.value
            case [10, 0]:
                self.face = Face.DOWN.value
            case [0, -10]:
                self.face = Face.LEFT.value

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
class Locker:
    """
    Lock anything you want
    - can use for save status for next trigger
    """
    danger_pos_lock_max: list = field(default_factory=lambda: [])
    danger_pos_lock_bfs: list = field(default_factory=lambda: [])
    pos_lock: list = field(default_factory=lambda: [])  # list pos all player + boms
    a_star_lock: list = field(default_factory=lambda: [])

    warning_pos_bfs: list = field(default_factory=lambda: [])
    warning_pos_max: list = field(default_factory=lambda: [])

    all_bomb_pos: list = field(default_factory=lambda: [])
    # use for checkpoint
    expect_pos: list = field(default_factory=lambda: [0, 0])
    expect_face: int = 0
    # dedup max
    dedup_act: list = field(default_factory=lambda: [])
    # use on-demand
    another: dict = field(
        default_factory=lambda: {
            "trigger_by_point": False,
        }
    )


@dataclass
class EvaluatedMap:
    enemy_map: list = field(default_factory=lambda: [])
    player_map: list = field(default_factory=lambda: [])

    def get_evaluated_map(self, pos_player: list, pos_enemy: list, pos_enemy_child: list):
        return sum(
            [
                self.player_map[pos_player[0]][pos_player[1]],
                self.enemy_map[pos_enemy[0]][pos_enemy[1]],
                self.enemy_map[pos_enemy_child[0]][pos_enemy_child[1]],
            ]
        )

    def get_val_enemy(self, pos):
        return self.enemy_map[pos[0]][pos[1]]

    def get_val_player(self, pos):
        return self.player_map[pos[0]][pos[1]]

    def add_val_player(self, pos, val):
        self.player_map[pos[0]][pos[1]] += val

    def set_val_player(self, pos, val):
        self.player_map[pos[0]][pos[1]] = val

    def reset_point_map(self, cols, rows):
        self.enemy_map = create_map_zero(cols, rows)
        self.player_map = create_map_zero(cols, rows)

    def set_point_map(self, base_map: Map, status: Player):
        self.__set_road_point(base_map, status)
        self.__set_addition_point(base_map, status)

    def __set_road_point(self, base_map: Map, status: Player):
        if status.has_transform:
            destructible_values = Objects.DESTRUCTIBLE_PHASE2.value
        else:
            destructible_values = Objects.DESTRUCTIBLE.value
        around_range_values = AroundRange.LV1_4.value

        for row in range(base_map.rows):
            for col in range(base_map.cols):
                if base_map.map[row][col] in destructible_values:
                    for i in around_range_values:
                        self.player_map[row + i[0]][col + i[1]] = 25

    def __set_addition_point(self, base_map: Map, status: Player):
        self.__set_bombs(base_map)
        self.__set_spoils(base_map, status)

    def __set_bombs(self, base_map: Map):
        # set trong hàm val nên maybe không cần nuwa
        pass

    def __set_spoils(self, base_map: Map, status: Player):
        around_range_values = AroundRange.LV1_4.value
        if status.can_use_item:
            for spoil in base_map.spoils:
                self.player_map[spoil["row"]][spoil["col"]] = 150
                for i in around_range_values:
                    self.player_map[spoil["row"] + i[0]][spoil["col"] + i[1]] = 25


@dataclass()
class ValResponse:
    pos_list: list
    act_list: list
    value: int = StatusPoint.MIN.value
    weapon: int = Weapon.NO.value

    expect_pos: list = field(default_factory=lambda: [0, 0])
    expect_face: int = 0
    # use on-demand
    another: dict = field(
        default_factory=lambda: {
            "pos_des_by_bomb": []
        }
    )


@dataclass()
class ShareEnv:
    player_used_pos: list = field(default_factory=lambda: [])
    player_targeted_boxes: list = field(default_factory=lambda: [])
    child_used_pos: list = field(default_factory=lambda: [])
    child_targeted_boxes: list = field(default_factory=lambda: [])

    @property
    def used_pos(self):
        return self.player_used_pos + self.child_used_pos

    @property
    def targeted_boxes(self):
        return self.player_targeted_boxes + self.child_targeted_boxes


@dataclass()
class MapFrame:
    player: Player
    base_map: Map
    possible_pos: dict = field(default_factory=lambda: {})

    @property
    def get_list_pos_valid(self, deep: int = 4) -> list:
        list_pos_valid = []

        return list_pos_valid
