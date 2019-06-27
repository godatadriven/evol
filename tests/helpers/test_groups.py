from random import seed

from pytest import mark, raises

from evol.helpers.groups import group_duplicate, group_stratified, group_random


@mark.parametrize('n_groups', [1, 2, 3, 4])
def test_group_duplicate(simple_individuals, n_groups):
    indexes = group_duplicate(simple_individuals, n_groups=n_groups)
    assert all(len(index) == len(set(index)) for index in indexes)
    assert all(len(index) == len(simple_individuals) for index in indexes)
    assert len(indexes) == n_groups


def test_group_random(simple_individuals):
    seed(42)
    indexes = group_random(simple_individuals, n_groups=4)
    assert sum(len(index) for index in indexes) == len(simple_individuals)
    seed(41)
    alt_indexes = group_random(simple_individuals, n_groups=4)
    assert indexes != alt_indexes


def test_group_stratified(evaluated_individuals):
    indexes = group_stratified(evaluated_individuals, n_groups=2)
    assert all(index % 2 == 0 for index in indexes[0])
    assert all(index % 2 != 0 for index in indexes[1])
    assert sum(len(index) for index in indexes) == len(evaluated_individuals)


def test_group_stratified_unevaluated(simple_individuals):
    simple_individuals[0].fitness = None
    with raises(RuntimeError):
        group_stratified(simple_individuals)
