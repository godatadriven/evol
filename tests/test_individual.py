from unittest import TestCase

from evol import Individual


class TestIndividual(TestCase):

    def test_init(self):
        chromosome = (3, 4)
        ind = Individual(chromosome=chromosome)
        self.assertEqual(chromosome, ind.chromosome)
        self.assertIsNone(ind.fitness)

    def test_evaluate(self):
        ind = Individual(chromosome=(1, 2))
        ind.evaluate(sum)

        def eval_func(chromosome):
            raise RuntimeError

        ind.evaluate(eval_function=eval_func, lazy=True)
        self.assertEqual(ind.fitness, 3)

        def eval_func(chromosome):
            return 5

        ind.evaluate(eval_function=eval_func, lazy=False)
        self.assertEqual(ind.fitness, 5)

    def test_mutate(self):
        ind = Individual(chromosome=(1, 2, 3))
        ind.evaluate(sum)

        def mutate_func(chromosome, value):
            return chromosome[0], value, chromosome[2]

        ind.mutate(mutate_func, value=5)
        self.assertEqual((1, 5, 3), ind.chromosome)
        self.assertIsNone(ind.fitness)
