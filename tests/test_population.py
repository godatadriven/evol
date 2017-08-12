import unittest
import random
from evol import Population

def init_func():
    return 1

def eval_func(x):
    return x

class TestPopulationSimple(unittest.TestCase):

    def test_filter_works(self):
        pop = Population(init_function=init_func, eval_function=eval_func, size=200)
        self.assertTrue(len(pop.filter(func=lambda i: random.random() > 0.5)) < 200)

    def test_individuals_are_not_initially_evaluated(self):
        pop = Population(init_function=init_func, eval_function=eval_func, size=200)
        self.assertTrue(all([i.fitness is None for i in pop]))

    def test_explicit_evaluate_works(self):
        pop = Population(init_function=init_func, eval_function=eval_func, size=200)
        pop.evaluate()
        self.assertTrue(all([i.fitness is not None for i in pop]))

    def test_mutate_works(self):
        pop = Population(init_function=init_func, eval_function=eval_func, size=200)
        pop.evaluate()
        values_before = [i.fitness for i in pop]
        pop.mutate(lambda x: x*2).evaluate()
        values_after = [i.fitness for i in pop]
        self.assertEqual([f*2 for f in values_before], values_after)


class TestPopulationSurvive(unittest.TestCase):

    def test_survive_n_works(self):
        pop1 = Population(init_function=init_func, eval_function=eval_func, size=200)
        pop2 = Population(init_function=init_func, eval_function=eval_func, size=200)
        pop3 = Population(init_function=init_func, eval_function=eval_func, size=200)
        self.assertEqual(len(pop1), 200)
        self.assertEqual(len(pop2.survive(n=50)), 50)
        self.assertEqual(len(pop3.survive(n=150, luck=True)), 150)

    def test_survive_p_works(self):
        pop1 = Population(init_function=init_func, eval_function=eval_func, size=200)
        pop2 = Population(init_function=init_func, eval_function=eval_func, size=200)
        pop3 = Population(init_function=init_func, eval_function=eval_func, size=200)
        self.assertEqual(len(pop1), 200)
        self.assertEqual(len(pop2.survive(fraction=0.5)), 100)
        self.assertEqual(len(pop3.survive(fraction=0.1, luck=True)), 20)

    def test_survive_n_and_p_works(self):
        pop1 = Population(init_function=init_func, eval_function=eval_func, size=200)
        pop2 = Population(init_function=init_func, eval_function=eval_func, size=200)
        pop3 = Population(init_function=init_func, eval_function=eval_func, size=200)
        self.assertEqual(len(pop1.survive(fraction=0.5, n=200)), 100)
        self.assertEqual(len(pop2.survive(fraction=0.9, n=10)), 10)
        self.assertEqual(len(pop3.survive(fraction=0.5, n=190, luck=True)), 100)

    def test_survive_throws_correct_errors(self):
        """if n/fraction > pop_size or n/fraction == 0"""
        pop1 = Population(init_function=init_func, eval_function=eval_func, size=200)
        with self.assertRaises(RuntimeError):
            pop1.survive(n=0)
        pop2 = Population(init_function=init_func, eval_function=eval_func, size=200)
        with self.assertRaises(ValueError):
            pop2.survive(n=250)
        pop3 = Population(init_function=init_func, eval_function=eval_func, size=200)
        with self.assertRaises(ValueError):
            pop3.survive()
