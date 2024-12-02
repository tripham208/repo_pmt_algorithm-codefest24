import datetime
from copy import deepcopy

from lib.model.enum.action import FaceAction, Attack
from lib.model.enum.range import BombRange
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


def test_copy():
    a = [
        [2, 3],
        [5, 7]
    ]

    b = deepcopy(a)
    b += [[3, 2], [3, 2]]
    b[1][1] = 1
    print(a)
    print(b)
    cd = a[:]
    cd[0][0] = 10
    cd[1] = [4, 4]
    print(a)
    print(cd)
    """
    [[2, 3], [5, 7]]
    [[2, 3], [5, 1], [3, 2]]
    [[10, 3], [5, 7]]
    [[10, 3], [4, 4]]
    """

    x = b[:]
    x.remove([3, 2])
    x.remove([3, 3])
    print(x)
    print(b)


def test_dynamic_val():
    for i in range(1, 4):
        print()
        print(BombRange[f"LV{i}"].value)


def test_pr():
    print("\033[91m d\033[00m")

def test_compare():
    print([2,3]==[2,3])
    print(FaceAction.FACE_ACTION.value)
    print(FaceAction.FACE_ACTION.value[1] == [-1, 0])
    print(FaceAction.FACE_ACTION.value.index([-1, 0]))
    print(None == [1,1])

def test_a():
    a = "hello worldllllll"
    def b():
        nonlocal a
        print(a)
        c="aaaaaaaaa"
        a="hello world"
    b()
    #print(c) error
    print(a)

    print(a[0:3])
    print(int(datetime.datetime.now().timestamp() * 1000))

def test_b():
    print(not False)
    a =[]
    if a:
        print("blank")
    else:
        print("no blank")
    c ={}
    d ={}
    c["d"] = d.get("d")
    print( c["d"])

    match [6,6]:
        case Attack.SWITCH_WEAPON.value:
            print("match")

def test_list():
    l = [1,2,3,4,5]
    print(l)