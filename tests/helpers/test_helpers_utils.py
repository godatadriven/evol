from evol.helpers.utils import rotating_window, sliding_window


def test_sliding_window():
    assert list(sliding_window([1, 2, 3, 4])) == [(1, 2), (2, 3), (3, 4)]


def test_rotating_window():
    assert list(rotating_window([1, 2, 3, 4])) == [(4, 1), (1, 2), (2, 3), (3, 4)]
