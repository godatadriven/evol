from random import random, choices, seed

from pytest import raises

from evol import Population, ContestPopulation
from evol.helpers.pickers import pick_random


class TestPopulationSimple:

    def test_filter_works(self, simple_chromosomes, simple_evaluation_function):
        pop = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)
        assert len(pop.filter(func=lambda i: random() > 0.5)) < 200

    def test_population_init(self, simple_chromosomes):
        pop = Population(simple_chromosomes, eval_function=lambda x: x)
        assert len(pop) == len(simple_chromosomes)
        assert pop.intended_size == len(pop)

    def test_population_generate(self, simple_evaluation_function):
        def init_func():
            return 1

        pop = Population.generate(init_function=init_func, eval_function=simple_evaluation_function, size=200)
        assert len(pop) == 200
        assert pop.intended_size == 200
        assert pop.individuals[0].chromosome == 1


class TestPopulationEvaluate:

    def test_individuals_are_not_initially_evaluated(self, simple_population):
        assert all([i.fitness is None for i in simple_population])

    def test_evaluate_lambda(self, simple_chromosomes):
        pop = Population(simple_chromosomes, eval_function=lambda x: x)
        pop.evaluate()
        for individual in pop:
            assert individual.chromosome == individual.fitness

    def test_evaluate_func(self, simple_chromosomes):
        def evaluation_function(x):
            return x*x
        pop = Population(simple_chromosomes, eval_function=evaluation_function)
        pop.evaluate()
        for individual in pop:
            assert evaluation_function(individual.chromosome) == individual.fitness

    def test_evaluate_lazy(self, simple_population):
        pop = simple_population
        pop.evaluate(lazy=True)  # should evaluate

        def raise_function(_):
            raise Exception

        pop.eval_function = raise_function
        pop.evaluate(lazy=True)  # should not evaluate
        with raises(Exception):
            pop.evaluate(lazy=False)


class TestPopulationSurvive:

    def test_survive_n_works(self, simple_chromosomes, simple_evaluation_function):
        pop1 = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)
        pop2 = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)
        pop3 = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)
        assert len(pop1) == len(simple_chromosomes)
        assert len(pop2.survive(n=50)) == 50
        assert len(pop3.survive(n=75, luck=True)) == 75

    def test_survive_p_works(self, simple_chromosomes, simple_evaluation_function):
        pop1 = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)
        pop2 = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)
        pop3 = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)
        assert len(pop1) == len(simple_chromosomes)
        assert len(pop2.survive(fraction=0.5)) == len(simple_chromosomes) * 0.5
        assert len(pop3.survive(fraction=0.1, luck=True)) == len(simple_chromosomes) * 0.1

    def test_survive_n_and_p_works(self, simple_evaluation_function):
        chromosomes = list(range(200))
        pop1 = Population(chromosomes=chromosomes, eval_function=simple_evaluation_function)
        pop2 = Population(chromosomes=chromosomes, eval_function=simple_evaluation_function)
        pop3 = Population(chromosomes=chromosomes, eval_function=simple_evaluation_function)
        assert len(pop1.survive(fraction=0.5, n=200)) == 100
        assert len(pop2.survive(fraction=0.9, n=10)) == 10
        assert len(pop3.survive(fraction=0.5, n=190, luck=True)) == 100

    def test_survive_throws_correct_errors(self, simple_population):
        """If the resulting population is zero or larger than initial we need to see errors."""
        with raises(RuntimeError):
            simple_population.survive(n=0)
        with raises(ValueError):
            simple_population.survive(n=250)
        with raises(ValueError):
            simple_population.survive()


class TestPopulationBreed:

    def test_breed_amount_works(self, simple_chromosomes, simple_evaluation_function):
        pop1 = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)
        pop1.survive(n=50).breed(parent_picker=lambda population: choices(population, k=2),
                                 combiner=lambda mom, dad: (mom + dad) / 2)
        assert len(pop1) == len(simple_chromosomes)
        pop2 = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)
        pop2.survive(n=50).breed(parent_picker=lambda population: choices(population, k=2),
                                 combiner=lambda mom, dad: (mom + dad) / 2, population_size=400)
        assert len(pop2) == 400
        assert pop2.intended_size == 400

    def test_breed_works_with_kwargs(self, simple_chromosomes, simple_evaluation_function):
        pop1 = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)
        pop1.survive(n=50).breed(parent_picker=pick_random,
                                 combiner=lambda mom, dad: (mom + dad) / 2,
                                 n_parents=2)
        assert len(pop1) == len(simple_chromosomes)
        pop2 = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)
        pop2.survive(n=50).breed(parent_picker=pick_random,
                                 combiner=lambda *parents: sum(parents)/len(parents),
                                 population_size=400, n_parents=3)
        assert len(pop2) == 400
        assert pop2.intended_size == 400


class TestPopulationMutate:

    def test_mutate_lambda(self):
        pop = Population([1]*100, eval_function=lambda x: x).mutate(lambda x: x+1)
        for chromosome in pop.chromosomes:
            assert chromosome == 2
        assert len(pop) == 100

    def test_mutate_inplace(self):
        pop = Population([1]*100, eval_function=lambda x: x)
        pop.mutate(lambda x: x+1)
        for chromosome in pop.chromosomes:
            assert chromosome == 2

    def test_mutate_func(self):
        def mutate_func(x):
            return -x
        population = Population([1]*100, eval_function=lambda x: x)
        population.mutate(mutate_func)
        for chromosome in population.chromosomes:
            assert chromosome == -1
        assert len(population) == 100

    def test_mutate_probability(self):
        seed(0)
        pop = Population([1]*100, eval_function=lambda x: x).mutate(lambda x: x+1, probability=0.5).evaluate()
        assert min(individual.chromosome for individual in pop.individuals) == 1
        assert max(individual.chromosome for individual in pop.individuals) == 2
        assert pop.current_best.fitness == 2
        assert pop.documented_best.fitness == 2
        assert len(pop) == 100

    def test_mutate_zero_probability(self):
        pop = Population([1]*100, eval_function=lambda x: x).mutate(lambda x: x+1, probability=0)
        for chromosome in pop.chromosomes:
            assert chromosome == 1

    def test_mutate_func_kwargs(self):
        def mutate_func(x, y=0):
            return x+y
        pop = Population([1]*100, eval_function=lambda x: x).mutate(mutate_func, y=16)
        for chromosome in pop.chromosomes:
            assert chromosome == 17


class TestPopulationWeights:

    def test_weights(self, simple_chromosomes, simple_evaluation_function):
        for maximize in (False, True):
            pop = Population(chromosomes=simple_chromosomes,
                             eval_function=simple_evaluation_function, maximize=maximize)
            with raises(RuntimeError):
                _ = pop._individual_weights
            pop.evaluate()
            assert max(pop._individual_weights) == 1
            assert min(pop._individual_weights) == 0
            if maximize:
                assert pop._individual_weights[0] == 0
            else:
                assert pop._individual_weights[0] == 1


class TestPopulationBest:

    def test_current_best(self, simple_chromosomes):
        for maximize, best in ((True, max(simple_chromosomes)), (False, min(simple_chromosomes))):
            pop = Population(chromosomes=simple_chromosomes, eval_function=float, maximize=maximize)
            assert pop.current_best is None
            pop.evaluate()
            assert pop.current_best.chromosome == best

    def test_current_worst(self, simple_chromosomes):
        for maximize, worst in ((False, max(simple_chromosomes)), (True, min(simple_chromosomes))):
            pop = Population(chromosomes=simple_chromosomes, eval_function=float, maximize=maximize)
            assert pop.current_worst is None
            pop.evaluate()
            assert pop.current_worst.chromosome == worst

    def test_mutate_resets(self):
        pop = Population(chromosomes=[1, 1, 1], eval_function=float, maximize=True)
        assert pop.current_best is None and pop.current_worst is None
        pop.evaluate()
        assert pop.current_best.fitness == 1 and pop.current_worst.fitness == 1
        pop.mutate(lambda x: x)
        assert pop.current_best is None and pop.current_worst is None

    def test_documented_best(self):
        pop = Population(chromosomes=[100, 100, 100], eval_function=lambda x: x*2, maximize=True)
        assert pop.documented_best is None
        pop.evaluate()
        assert pop.documented_best.fitness == pop.current_best.fitness
        pop.mutate(func=lambda x: x-10, probability=1).evaluate()
        assert pop.documented_best.fitness - 20 == pop.current_best.fitness


class TestContestPopulation:

    def test_init(self):
        cp = ContestPopulation([0, 1, 2], lambda x: x, contests_per_round=15, individuals_per_contest=15)
        assert cp.contests_per_round == 15
        assert cp.individuals_per_contest == 15


class TestContestPopulationBest:

    def test_no_documented(self):
        pop = ContestPopulation([0, 1, 2], lambda x, y: [0, 0], contests_per_round=100, individuals_per_contest=2)
        pop.evaluate()
        assert pop.documented_best is None
