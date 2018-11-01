import math

import pytest

from evol.problems.routing.magicsanta import MagicSanta


@pytest.fixture
def base_problem():
    return MagicSanta(city_coordinates=[(0, 1), (1, 0), (1, 1)],
                      home_coordinate=(0, 0),
                      gift_weight=[0, 0, 0])


@pytest.fixture
def adv_problem():
    return MagicSanta(city_coordinates=[(0, 1), (1, 1), (0, 1)],
                      home_coordinate=(0, 0),
                      gift_weight=[5, 1, 1],
                      sleigh_weight=2)


def test_error_raised_wrong_cities(base_problem):
    # we want an error if we see too many cities
    with pytest.raises(ValueError) as execinfo1:
        base_problem.eval_function([[0, 1, 2, 3]])
    assert "Extra: {3}" in str(execinfo1.value)
    # we want an error if we see too few cities
    with pytest.raises(ValueError) as execinfo2:
        base_problem.eval_function([[0, 2]])
    assert "Missing: {1}" in str(execinfo2.value)
    # we want an error if we see multiple occurences of cities
    with pytest.raises(ValueError) as execinfo3:
        base_problem.eval_function([[0, 2], [0, 1]])
    assert "Multiple occurrences found for cities: {0}" in str(execinfo3.value)


def test_base_score_method(base_problem):
    assert base_problem.distance((0, 0), (0, 2)) == 2
    expected = 1 + math.sqrt(2) + 1 + math.sqrt(2)
    assert base_problem.eval_function([[0, 1, 2]]) == pytest.approx(expected)
    assert base_problem.eval_function([[2, 1, 0]]) == pytest.approx(expected)
    base_problem.sleigh_weight = 2
    assert base_problem.eval_function([[2, 1, 0]]) == pytest.approx(2*expected)


def test_sleight_gift_weights(adv_problem):
    expected = (2+7) + (2+2) + (2+1) + (2+0)
    assert adv_problem.eval_function([[0, 1, 2]]) == pytest.approx(expected)


def test_multiple_routes(adv_problem):
    expected = (2 + 6) + (2 + 1) + math.sqrt(2)*(2 + 0) + (2 + 1) + (2 + 0)
    assert adv_problem.eval_function([[0, 1], [2]]) == pytest.approx(expected)
