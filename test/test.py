import datetime
from copy import deepcopy

from lib.utils.map import create_map_zero


if __name__ == "__main__":
    print(datetime.datetime.now())
    m = create_map_zero(100, 100)
    print(datetime.datetime.now())
    c = create_map_zero(100, 100)
    print(datetime.datetime.now())
    d = deepcopy(c)
    print(datetime.datetime.now())


def vector_direction(A: list, B: list) -> list:
    """
    Xác định hướng của vectơ AB từ điểm A đến điểm B.
    A và B là các điểm dưới dạng [x, y].
    """
    direction = [B[0] - A[0], B[1] - A[1]]
    return direction




def test_vector_direction():
    # Ví dụ các điểm A và B
    A = [2, 3]
    B = [5, 7]

    # Xác định hướng của vectơ AB
    direction_AB = vector_direction(A, B)
    print("Hướng của vectơ AB là:", direction_AB)