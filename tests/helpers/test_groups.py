from random import seed

from pytest import mark, raises

from evol import Population
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


class TestGroupStratified:

    def test_unique(self, evaluated_individuals):
        indexes = group_stratified(evaluated_individuals, n_groups=2)
        assert set(index for island in indexes for index in island) == set(range(len(evaluated_individuals)))

    @mark.parametrize('n_groups', (2, 4))
    def test_is_stratified(self, shuffled_chromosomes, n_groups):
        population = Population(shuffled_chromosomes, eval_function=lambda x: x).evaluate()
        islands = population.group(group_stratified, n_groups=n_groups)
        # All islands should have the same total fitness
        assert len(set(sum(map(lambda i: i.fitness, island.individuals)) for island in islands)) == 1

    def test_must_be_evaluated(self, simple_population):
        with raises(RuntimeError):
            simple_population.group(group_stratified)


def test_group_stratified_unevaluated(simple_individuals):
    simple_individuals[0].fitness = None
    with raises(RuntimeError):
        group_stratified(simple_individuals)
