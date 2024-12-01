from lib.alg.max import is_valid_hammer
from lib.model.enum.range import AroundRange
from lib.utils.map import euclid_distance, dif_distance_with_target, find_index, get_info_action

map_s1 = [[1, 0], [1, 1]]
map_s2 = [[2, 0], [2, 2]]
map_s3 = [[3, 0], [3, 3]]

cols, rows = 3, 3


def test_euclid_distance_different_points():
    matrix = [
        [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8]],
        [[1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8]],
        [[2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8]],
        [[3, 0], [3, 1], [3, 2], [3, 3], [3, 4], [3, 5], [3, 6], [3, 7], [3, 8]],
        [[4, 0], [4, 1], [4, 2], [4, 3], [4, 4], [4, 5], [4, 6], [4, 7], [4, 8]],
        [[5, 0], [5, 1], [5, 2], [5, 3], [5, 4], [5, 5], [5, 6], [5, 7], [5, 8]],
        [[6, 0], [6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6], [6, 7], [6, 8]],
        [[7, 0], [7, 1], [7, 2], [7, 3], [7, 4], [7, 5], [7, 6], [7, 7], [7, 8]],
        [[8, 0], [8, 1], [8, 2], [8, 3], [8, 4], [8, 5], [8, 6], [8, 7], [8, 8]]
    ]
    print()

    for row in matrix:
        print([[[sum(i) for i in zip([19, 3], pos)], euclid_distance([0, 0], pos)] for pos in row])
    for row in matrix:
        print([euclid_distance([0, 0], point) for point in row])

    destination = [5, 5]
    print([[sum(i) for i in zip(destination, pos)] for pos in AroundRange.LV2.value])


def test_dif_distance_different_points():
    print(euclid_distance([19, 9], [14, 13]))


def test_dif_distance_with_target():
    pos_player = [1, 2]
    pos_enemy = [4, 6]
    target = [8, 10]  # Tính sự chênh lệch khoảng cách
    difference = dif_distance_with_target(pos_player, pos_enemy, target)
    print()
    print(euclid_distance(pos_player, target))
    print(euclid_distance(pos_enemy, target))
    print("Sự chênh lệch khoảng cách là:", difference)


def test_find_index_exists():
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 6, 9]
    ]
    target = 6
    result = find_index(matrix, target)
    assert result == [[1, 2], [2, 1]], f"Expected [[1, 2], [2, 1]] but got {result}"


def test_get_info_action():
    act_list = [[0, 10], [6, 6]]
    act_list2 = [[6, 6], [0, 10]]
    act_list3 = [[4, 4], [0, 10]]
    act_list4 = [[6, 6], [4, 4]]
    print()
    print(get_info_action(act_list))
    print(get_info_action(act_list2))
    print(get_info_action(act_list3))
    print(get_info_action(act_list4))


def test_f():
    fmap = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 3, 3, 0, 0, 3, 3, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 3, 3, 0, 0, 0, 0,
         0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2,
         0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 2, 1, 2, 2, 2, 0, 0, 2, 1, 2, 3, 0, 3, 0, 3, 3, 3, 3, 0, 3, 2, 1, 2, 0, 0, 2, 2, 2, 1, 2, 2,
         0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 2, 2, 1, 2, 2, 2, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 2, 0, 0, 2, 1, 2, 0, 0, 2, 2, 2, 1, 2, 2, 0,
         0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 2, 2, 1, 2, 2, 2, 0, 0, 2, 1, 2, 3, 0, 3, 3, 0, 3, 2, 1, 2, 3, 3, 2, 2, 2, 1, 2, 2, 0, 0,
         0, 0, 0, 0, 1],
        [1, 0, 0, 5, 0, 0, 0, 0, 2, 2, 1, 2, 2, 2, 0, 0, 2, 1, 2, 0, 2, 2, 0, 2, 1, 2, 0, 0, 2, 2, 2, 1, 2, 2, 0, 0, 0,
         0, 5, 0, 0, 1],
        [1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 2, 1, 0, 3, 3, 3, 1, 2, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 0, 0, 1],
        [1, 0, 0, 0, 3, 0, 3, 0, 3, 3, 0, 2, 2, 2, 0, 0, 3, 1, 0, 0, 0, 0, 0, 0, 1, 3, 0, 0, 2, 2, 2, 0, 3, 3, 0, 3, 0,
         3, 0, 0, 0, 1],
        [1, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 3, 0, 3, 0, 3, 0, 6, 2, 2, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 2, 2, 2, 2, 2,
         2, 2, 0, 0, 1],
        [1, 0, 0, 0, 3, 0, 3, 0, 3, 0, 3, 3, 2, 2, 0, 0, 3, 1, 0, 0, 0, 0, 0, 0, 1, 3, 0, 0, 2, 2, 3, 3, 0, 3, 0, 3, 0,
         3, 0, 0, 0, 1],
        [1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 2, 1, 3, 3, 3, 3, 1, 2, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 0, 0, 1],
        [1, 0, 0, 5, 0, 0, 0, 0, 2, 2, 1, 2, 2, 2, 0, 0, 2, 1, 2, 0, 2, 2, 0, 2, 1, 2, 0, 0, 2, 2, 2, 1, 2, 2, 0, 0, 0,
         0, 5, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 2, 2, 1, 2, 2, 2, 0, 0, 2, 1, 2, 3, 0, 3, 3, 0, 3, 2, 1, 2, 0, 0, 2, 2, 2, 1, 2, 2, 0, 0,
         0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 2, 2, 1, 2, 2, 2, 0, 0, 2, 1, 2, 0, 0, 2, 2, 2, 2, 0, 0, 2, 1, 2, 0, 0, 2, 2, 2, 1, 2, 2, 0,
         0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 2, 1, 2, 2, 2, 0, 0, 2, 1, 2, 3, 0, 3, 3, 3, 3, 3, 3, 0, 3, 2, 1, 2, 0, 0, 2, 2, 2, 1, 2, 2,
         0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2,
         0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 3, 3, 0, 0, 3, 3, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1, 1, 1]]
    pos = [9, 26]
    print(fmap[pos[0]][pos[1]])


def test_is_valid_hammer():
    # Test case where both x and y coordinates are within range
    print(is_valid_hammer([19, 3], [26, 8]))  # x
    print(is_valid_hammer([19, 3], [26, 7]))  # v
    print(is_valid_hammer([19, 3], [25, 9]))  # v
    print(is_valid_hammer([19, 3], [27, 7]))  # x
    print(is_valid_hammer([19, 3], [27, 6]))  # x
    print(is_valid_hammer([19, 3], [26, 9]))  # v
    print(is_valid_hammer([19, 3], [26, 10]))  # v
    print(is_valid_hammer([19, 3], [26, 11]))  # x
    print(is_valid_hammer([19, 9], [19, 9]))  # v
    print(is_valid_hammer([19, 9], [14, 13]))  # v
    print(is_valid_hammer([19, 9], [14, 9]))  # v
