from pytest import raises

from evol import Population, IslandPopulation, Individual


class TestIslandPopulation:

    def test_init(self):
        pop1 = Population(chromosomes=list(range(10)), eval_function=lambda x: x)
        pop2 = Population(chromosomes=list(range(20)), eval_function=lambda x: x)
        islands = IslandPopulation(populations=[pop1, pop2])
        assert len(islands) == 30
        assert len(islands.populations) == 2

    def test_from_population_duplicate(self):
        pop = Population(chromosomes=list(range(10)), eval_function=lambda x: x).duplicate(4)
        assert len(pop) == 40
        assert len(pop.populations) == 4

    def test_add(self):
        pop = Population(chromosomes=list(range(10)), eval_function=lambda x: x).duplicate(4)
        pop.add(Individual(80))
        assert len(pop) == 44
