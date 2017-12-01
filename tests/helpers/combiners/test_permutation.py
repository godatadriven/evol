from random import seed

from evol.helpers.combiners.permutation import order_one_crossover, cycle_crossover


def test_order_one_crossover_int():
    seed(51)
    x, y = (8, 4, 7, 3, 6, 2, 5, 1, 9, 0), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    a = order_one_crossover(x, y)
    assert a == (0, 4, 7, 3, 6, 2, 5, 1, 8, 9)


def test_order_one_crossover_str():
    seed(51)
    x, y = ('I', 'E', 'H', 'D', 'G', 'C', 'F', 'B', 'J', 'A'), ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
    a = order_one_crossover(x, y)
    assert a == ('A', 'E', 'H', 'D', 'G', 'C', 'F', 'B', 'I', 'J')


def test_cycle_crossover_int():
    x, y = (8, 4, 7, 3, 6, 2, 5, 1, 9, 0), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    a, b = cycle_crossover(x, y)
    assert a == (8, 1, 2, 3, 4, 5, 6, 7, 9, 0) and b == (0, 4, 7, 3, 6, 2, 5, 1, 8, 9)


def test_cycle_crossover_str():
    x, y = ('I', 'E', 'H', 'D', 'G', 'C', 'F', 'B', 'J', 'A'), ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
    a, b = cycle_crossover(x, y)
    assert a == ('I', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'A')
    assert b == ('A', 'E', 'H', 'D', 'G', 'C', 'F', 'B', 'I', 'J')
