from lib.utils.map import euclid_distance

map_s1 = [[1, 0], [1, 1]]
map_s2 = [[2, 0], [2, 2]]
map_s3 = [[3, 0], [3, 3]]

cols, rows = 3, 3


def test_euclid_distance_different_points():
    assert euclid_distance([0, 0], [0, 2]) == 2
