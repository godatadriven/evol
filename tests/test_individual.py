from copy import copy

from evol import Individual


class TestIndividual:

    def test_init(self):
        chromosome = (3, 4)
        ind = Individual(chromosome=chromosome)
        assert chromosome == ind.chromosome
        assert ind.fitness is None

    def test_copy(self):
        individual = Individual(chromosome=(1, 2))
        individual.evaluate(sum)
        copied_individual = copy(individual)
        assert individual.chromosome == copied_individual.chromosome
        assert individual.fitness == copied_individual.fitness
        assert individual.id == copied_individual.id
        copied_individual.mutate(lambda x: (2, 3))
        assert individual.chromosome == (1, 2)

    def test_evaluate(self):
        ind = Individual(chromosome=(1, 2))
        ind.evaluate(sum)

        def eval_func1(chromosome):
            raise RuntimeError

        ind.evaluate(eval_function=eval_func1, lazy=True)
        assert ind.fitness == 3

        def eval_func2(chromosome):
            return 5

        ind.evaluate(eval_function=eval_func2, lazy=False)
        assert ind.fitness == 5

    def test_mutate(self):
        ind = Individual(chromosome=(1, 2, 3))
        ind.evaluate(sum)

        def mutate_func(chromosome, value):
            return chromosome[0], value, chromosome[2]

        ind.mutate(mutate_func, value=5)
        assert (1, 5, 3) == ind.chromosome
        assert ind.fitness is None
