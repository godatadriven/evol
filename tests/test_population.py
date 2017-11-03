from unittest import TestCase
from random import random, choices, seed
from evol import Population, ContestPopulation


def init_func():
    return 1


def eval_func(x):
    return x


def pick_two_random_parents(population):
    return choices(population, k=2)


def pick_n_random_parents(population, n_parents=2):
    return choices(population, k=n_parents)


def combine_two_parents(mom, dad):
    return (mom+dad)/2


def general_combiner(*parents):
    return sum(parents)/len(parents)


class TestPopulationSimple(TestCase):

    def setUp(self):
        self.chromosomes = list(range(100))

    def test_filter_works(self):
        pop = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        self.assertTrue(len(pop.filter(func=lambda i: random() > 0.5)) < 200)


class TestPopulationEvaluate(TestCase):

    def setUp(self):
        self.chromosomes = list(range(100))

    def test_individuals_are_not_initially_evaluated(self):
        pop = Population(self.chromosomes, eval_function=lambda x: x)
        self.assertTrue(all([i.fitness is None for i in pop]))

    def test_evaluate_lambda(self):
        pop = Population(self.chromosomes, eval_function=lambda x: x)
        pop.evaluate()
        for individual in pop:
            self.assertEqual(individual.chromosome, individual.fitness)

    def test_evaluate_func(self):
        def evaluation_function(x):
            return x*x
        pop = Population(self.chromosomes, eval_function=evaluation_function)
        pop.evaluate()
        for individual in pop:
            self.assertEqual(evaluation_function(individual.chromosome), individual.fitness)

    def test_evaluate_lazy(self):
        pop = Population(self.chromosomes, eval_function=lambda x: x)
        pop.evaluate(lazy=True)  # should evaluate

        def raise_function(x):
            raise Exception

        pop.eval_function = raise_function
        pop.evaluate(lazy=True)  # should not evaluate
        with self.assertRaises(Exception):
            pop.evaluate(lazy=False)


class TestPopulationSurvive(TestCase):

    def setUp(self):
        self.chromosomes = list(range(100))

    def test_survive_n_works(self):
        pop1 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        pop2 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        pop3 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        self.assertEqual(len(pop1), 200)
        self.assertEqual(len(pop2.survive(n=50)), 50)
        self.assertEqual(len(pop3.survive(n=150, luck=True)), 150)

    def test_survive_p_works(self):
        pop1 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        pop2 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        pop3 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        self.assertEqual(len(pop1), 200)
        self.assertEqual(len(pop2.survive(fraction=0.5)), 100)
        self.assertEqual(len(pop3.survive(fraction=0.1, luck=True)), 20)

    def test_survive_n_and_p_works(self):
        pop1 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        pop2 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        pop3 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        self.assertEqual(len(pop1.survive(fraction=0.5, n=200)), 100)
        self.assertEqual(len(pop2.survive(fraction=0.9, n=10)), 10)
        self.assertEqual(len(pop3.survive(fraction=0.5, n=190, luck=True)), 100)

    def test_survive_throws_correct_errors(self):
        """If the resulting population is zero or larger than initial we need to see errors."""
        pop1 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        with self.assertRaises(RuntimeError):
            pop1.survive(n=0)
        pop2 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        with self.assertRaises(ValueError):
            pop2.survive(n=250)
        pop3 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        with self.assertRaises(ValueError):
            pop3.survive()


class TestPopulationBreed(TestCase):

    def setUp(self):
        self.chromosomes = list(range(100))

    def test_breed_amount_works(self):
        pop1 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        pop1.survive(n=50).breed(parent_picker=pick_two_random_parents, combiner=combine_two_parents)
        self.assertEqual(len(pop1), 200)
        pop2 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        pop2.survive(n=50).breed(parent_picker=pick_two_random_parents, combiner=combine_two_parents,
                                 population_size=400)
        self.assertEqual(len(pop2), 400)
        self.assertEqual(pop2.intended_size, 400)

    def test_breed_works_with_kwargs(self):
        pop1 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        pop1.survive(n=50).breed(parent_picker=pick_n_random_parents, combiner=combine_two_parents, n_parents=2)
        self.assertEqual(len(pop1), 200)
        pop2 = Population(chromosomes=self.chromosomes, eval_function=eval_func)
        pop2.survive(n=50).breed(parent_picker=pick_n_random_parents, combiner=general_combiner, population_size=400,
                                 n_parents=3)
        self.assertEqual(len(pop2), 400)
        self.assertEqual(pop2.intended_size, 400)


class TestPopulationMutate(TestCase):

    def setUp(self):
        self.population = Population(chromosomes=[1 for _ in range(100)],
                                     eval_function=float)

    def test_mutate_lambda(self):
        pop = self.population.mutate(lambda x: x+1)
        for chromosome in pop.chromosomes:
            self.assertEqual(chromosome, 2)
        self.assertEqual(len(pop), 100)

    def test_mutate_inplace(self):
        self.population.mutate(lambda x: x+1)
        for chromosome in self.population.chromosomes:
            self.assertEqual(chromosome, 2)

    def test_mutate_func(self):
        def mutate_func(x):
            return -x
        self.population.mutate(mutate_func)
        for chromosome in self.population.chromosomes:
            self.assertEqual(chromosome, -1)
        self.assertEqual(len(self.population), 100)

    def test_mutate_probability(self):
        seed(0)
        pop = self.population.mutate(lambda x: x+1, probability=0.5)
        self.assertEqual(pop.min_individual.chromosome, 1)
        self.assertEqual(pop.max_individual.chromosome, 2)
        self.assertEqual(len(pop), 100)

    def test_mutate_zero_probability(self):
        self.population.mutate(lambda x: x+1, probability=0)
        for chromosome in self.population.chromosomes:
            self.assertEqual(chromosome, 1)

    def test_mutate_func_kwargs(self):
        def mutate_func(x, y=0):
            return x+y
        self.population.mutate(mutate_func, y=16)
        for chromosome in self.population.chromosomes:
            self.assertEqual(chromosome, 17)


class TestContestPopulation(TestCase):

    def test_init(self):
        cp = ContestPopulation([0, 1, 2], lambda x: x, contests_per_round=15, individuals_per_contest=15)
        self.assertEqual(cp.contests_per_round, 15)
        self.assertEqual(cp.individuals_per_contest, 15)

    def check_no_fitness(self, population):
        for individual in population:
            self.assertIsNone(individual.fitness)
