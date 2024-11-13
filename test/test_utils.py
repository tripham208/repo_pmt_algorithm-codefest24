from lib.utils.map import euclid_distance, dif_distance_with_target

map_s1 = [[1, 0], [1, 1]]
map_s2 = [[2, 0], [2, 2]]
map_s3 = [[3, 0], [3, 3]]

cols, rows = 3, 3


def test_euclid_distance_different_points():
    assert euclid_distance([0, 0], [0, 2]) == 2


def test_dif_distance_with_target():
    pos_player = [1, 2]
    pos_enemy = [4, 6]
    target = [8,10]  # Tính sự chênh lệch khoảng cách
    difference = dif_distance_with_target(pos_player, pos_enemy, target)
    print()
    print(euclid_distance(pos_player, target))
    print(euclid_distance(pos_enemy, target))
    print("Sự chênh lệch khoảng cách là:", difference)
