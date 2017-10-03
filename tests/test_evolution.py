from unittest import TestCase

from evol import Evolution, Population


class TestEvolution(TestCase):

    def test_add_step(self):
        evo = Evolution()
        self.assertListEqual(evo.chain, [])
        evo_step = evo._add_step('step')
        self.assertListEqual(evo.chain, [])  # original unchanged
        self.assertListEqual(evo_step.chain, ['step'])  # copy with extra step

    def test_evolve(self):
        evo = Evolution().mutate(lambda x: x+1)
        pop = Population(chromosomes=[0, 1, 2, 3], eval_function=lambda x: x)
        new_pop = evo.evolve(pop, inplace=False)
        # New population has evolved
        self.assertListEqual([i.chromosome for i in new_pop], [1, 2, 3, 4])
        # Old population is unchanged
        self.assertListEqual([i.chromosome for i in pop], [0, 1, 2, 3])

    def test_multiple_evolve(self):
        evo = Evolution().mutate(lambda x: x+1)
        pop = Population(chromosomes=[0, 1, 2, 3], eval_function=lambda x: x)
        new_pop = evo.evolve(pop, n=100, inplace=False)
        # New population has evolved
        self.assertListEqual([i.chromosome for i in new_pop], [100, 101, 102, 103])
        # Old population is unchanged
        self.assertListEqual([i.chromosome for i in pop], [0, 1, 2, 3])
