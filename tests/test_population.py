import unittest
import random
from evol import Population

def init_func():
    return 1


def eval_func(x):
    return x


def pick_two_random_parents(population):
    return random.choices(population, k=2)


def pick_n_random_parents(population, n_parents=2):
    return random.choices(population, k=n_parents)


def combine_two_parents(mom, dad):
    return (mom+dad)/2


def general_combiner(*parents):
    return sum(parents)/len(parents)

chromosomes = [init_func() for _ in range(200)]

class TestPopulationClassMethod(unittest.TestCase):
    def test_classmethod_works(self):
        population = Population.generate(init_func=init_func, eval_func=eval_func, size=100)
        self.assertEqual(len(population), 100)


class TestPopulationSimple(unittest.TestCase):

    def test_filter_works(self):
        pop = Population(chromosomes=chromosomes, eval_function=eval_func)
        self.assertTrue(len(pop.filter(func=lambda i: random.random() > 0.5)) < 200)

    def test_individuals_are_not_initially_evaluated(self):
        pop = Population(chromosomes, eval_function=eval_func)
        self.assertTrue(all([i.fitness is None for i in pop]))

    def test_explicit_evaluate_works(self):
        pop = Population(chromosomes=chromosomes, eval_function=eval_func)
        pop.evaluate()
        self.assertTrue(all([i.fitness is not None for i in pop]))

    def test_mutate_works(self):
        pop = Population(chromosomes=chromosomes, eval_function=eval_func)
        pop.evaluate()
        values_before = [i.fitness for i in pop]
        pop.mutate(lambda x: x*2).evaluate()
        values_after = [i.fitness for i in pop]
        self.assertEqual([f*2 for f in values_before], values_after)


class TestPopulationSurvive(unittest.TestCase):

    def test_survive_n_works(self):
        pop1 = Population(chromosomes=chromosomes, eval_function=eval_func)
        pop2 = Population(chromosomes=chromosomes, eval_function=eval_func)
        pop3 = Population(chromosomes=chromosomes, eval_function=eval_func)
        self.assertEqual(len(pop1), 200)
        self.assertEqual(len(pop2.survive(n=50)), 50)
        self.assertEqual(len(pop3.survive(n=150, luck=True)), 150)

    def test_survive_p_works(self):
        pop1 = Population(chromosomes=chromosomes, eval_function=eval_func)
        pop2 = Population(chromosomes=chromosomes, eval_function=eval_func)
        pop3 = Population(chromosomes=chromosomes, eval_function=eval_func)
        self.assertEqual(len(pop1), 200)
        self.assertEqual(len(pop2.survive(fraction=0.5)), 100)
        self.assertEqual(len(pop3.survive(fraction=0.1, luck=True)), 20)

    def test_survive_n_and_p_works(self):
        pop1 = Population(chromosomes=chromosomes, eval_function=eval_func)
        pop2 = Population(chromosomes=chromosomes, eval_function=eval_func)
        pop3 = Population(chromosomes=chromosomes, eval_function=eval_func)
        self.assertEqual(len(pop1.survive(fraction=0.5, n=200)), 100)
        self.assertEqual(len(pop2.survive(fraction=0.9, n=10)), 10)
        self.assertEqual(len(pop3.survive(fraction=0.5, n=190, luck=True)), 100)

    def test_survive_throws_correct_errors(self):
        """If the resulting population is zero or larger than initial we need to see errors."""
        pop1 = Population(chromosomes=chromosomes, eval_function=eval_func)
        with self.assertRaises(RuntimeError):
            pop1.survive(n=0)
        pop2 = Population(chromosomes=chromosomes, eval_function=eval_func)
        with self.assertRaises(ValueError):
            pop2.survive(n=250)
        pop3 = Population(chromosomes=chromosomes, eval_function=eval_func)
        with self.assertRaises(ValueError):
            pop3.survive()

class TestPopulationBreed(unittest.TestCase):

    def test_breed_amount_works(self):
        pop1 = Population(chromosomes=chromosomes, eval_function=eval_func)
        pop1.survive(n=50).breed(parent_picker=pick_two_random_parents, combiner=combine_two_parents)
        self.assertEqual(len(pop1), 200)
        pop2 = Population(chromosomes=chromosomes, eval_function=eval_func)
        pop2.survive(n=50).breed(parent_picker=pick_two_random_parents, combiner=combine_two_parents, population_size=400)
        self.assertEqual(len(pop2), 400)
        self.assertEqual(pop2.intended_size, 400)

    def test_breed_works_with_kwargs(self):
        # TODO
        pass