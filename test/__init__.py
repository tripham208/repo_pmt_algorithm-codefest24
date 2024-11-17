import time


def time_function(func, *args):
    start_time = time.time()
    result = func(*args)
    end_time = time.time()
    return result, end_time - start_time

def show_map(matrix):
    print()
    for i in matrix:
        print(i)
    print("")
