import unittest
import random
from evol import Population

def init_func():
    return random.random()

def eval_func(x):
    return x

class TestFilter(unittest.TestCase):

    def test_filter_works(self):
        pop = Population(init_function=init_func, eval_function=eval_func, size=200)
        self.assertTrue(len(pop.filter(func=lambda i: random.random() > 0.5)) < 200)

    def test_explicit_evaluate_works(self):
        pop = Population(init_function=init_func, eval_function=eval_func, size=200)
        self.assertTrue(all([i.fitness is None for i in pop]))
        pop.evaluate()
        self.assertTrue(all([i.fitness is not None for i in pop]))