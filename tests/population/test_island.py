from pytest import raises

from evol import Population, IslandPopulation, ContestPopulation, Individual


class TestIslandPopulation:

    def population(self, size):
        return Population(chromosomes=list(range(size)),
                          eval_function=lambda x: x)

    def test_init(self):
        pop1 = self.population(10)
        pop2 = self.population(20)
        islands = IslandPopulation(populations=[pop1, pop2])
        assert len(islands) == 30
        assert len(islands.populations) == 2

    def test_from_population_duplicate(self):
        pop = self.population(10).duplicate(4)
        assert len(pop) == 40
        assert len(pop.populations) == 4

    def test_add(self):
        pop = self.population(10).duplicate(4)
        pop.add(Individual(80))
        assert len(pop) == 44

    def test_no_islands(self):
        with raises(ValueError):
            IslandPopulation(populations=[])
        with raises(ValueError):
            self.population(10).duplicate(0)


class TestIslandContestPopulation(TestIslandPopulation):

    def population(self, size):
        return ContestPopulation(chromosomes=list(range(size)),
                                 eval_function=lambda x, y: [x, y])


# class TestIslandSubPopulation(TestIslandPopulation):
#
#     def population(self, size):
#         return IslandPopulation(populations=[Population(list(range(int(size / 2))), eval_function=lambda x: x),
#                                              Population(list(range(int(size / 2))), eval_function=lambda x: x)])
