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


