from random import seed

from evol.helpers.mutators.permutation import inversion


def test_inversion_int():
    seed(53)  # Fix result of select_partition
    x = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    a = inversion(x)
    assert a == (0, 1, 2, 7, 6, 5, 4, 3, 8, 9)


def test_inversion_str():
    seed(53)  # Fix result of select_partition
    x = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')
    a = inversion(x)
    assert a == ('A', 'B', 'C', 'H', 'G', 'F', 'E', 'D', 'I', 'J')
