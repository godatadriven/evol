from time import sleep, time

import os
from copy import copy
from pytest import raises, mark
from random import random, choices, seed

from evol import Population, ContestPopulation
from evol.helpers.groups import group_duplicate, group_stratified
from evol.helpers.pickers import pick_random
from evol.population import Contest


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

    def test_is_evaluated(self, any_population):
        assert not any_population.is_evaluated
        assert any_population.evaluate().is_evaluated


class TestPopulationCopy:

    def test_population_copy(self, any_population):
        copied_population = copy(any_population)
        for key in any_population.__dict__.keys():
            if key not in ('id', 'individuals'):
                assert copied_population.__dict__[key] == any_population.__dict__[key]

    def test_population_is_evaluated(self, any_population):
        evaluated_population = any_population.evaluate()
        copied_population = copy(evaluated_population)
        assert evaluated_population.is_evaluated
        assert copied_population.is_evaluated


class TestPopulationEvaluate:

    cpus = os.cpu_count()
    latency = 0.005

    def test_individuals_are_not_initially_evaluated(self, any_population):
        assert all([i.fitness is None for i in any_population])

    def test_evaluate_lambda(self, simple_chromosomes):
        # without concurrency (note that I'm abusing a boolean operator to introduce some latency)
        pop = Population(simple_chromosomes, eval_function=lambda x: (sleep(self.latency) or x))
        t0 = time()
        pop.evaluate()
        t1 = time()
        single_proc_time = t1 - t0
        for individual in pop:
            assert individual.chromosome == individual.fitness
        # with concurrency
        pop = Population(simple_chromosomes, eval_function=lambda x: (sleep(self.latency) or x),
                         concurrent_workers=self.cpus)
        t0 = time()
        pop.evaluate()
        t1 = time()
        multi_proc_time = t1 - t0
        for individual in pop:
            assert individual.chromosome == individual.fitness
        if self.cpus > 1:
            assert multi_proc_time < single_proc_time

    def test_evaluate_func(self, simple_chromosomes):
        def evaluation_function(x):
            sleep(self.latency)
            return x * x
        pop = Population(simple_chromosomes, eval_function=evaluation_function)
        t0 = time()
        pop.evaluate()
        t1 = time()
        single_proc_time = t1 - t0
        for individual in pop:
            assert evaluation_function(individual.chromosome) == individual.fitness
        # with concurrency
        pop = Population(simple_chromosomes, eval_function=evaluation_function, concurrent_workers=self.cpus)
        t0 = time()
        pop.evaluate()
        t1 = time()
        multi_proc_time = t1 - t0
        for individual in pop:
            assert evaluation_function(individual.chromosome) == individual.fitness
        if self.cpus > 1:
            assert multi_proc_time < single_proc_time

    def test_evaluate_lazy(self, any_population):
        pop = any_population
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

    def test_breed_increases_generation(self, any_population):
        assert any_population.breed(parent_picker=pick_random, combiner=lambda mom, dad: mom).generation == 1

    def test_survive_throws_correct_errors(self, any_population):
        """If the resulting population is zero or larger than initial we need to see errors."""
        with raises(RuntimeError):
            any_population.survive(n=0)
        with raises(ValueError):
            any_population.survive(n=250)
        with raises(ValueError):
            any_population.survive()


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
        assert pop1.generation == 1
        assert pop2.generation == 1

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

    def test_breed_raises_with_multiple_values_for_kwarg(self, simple_population):

        (simple_population
            .survive(fraction=0.5)
            .breed(parent_picker=pick_random,
                   combiner=lambda x, y: x + y))

        with raises(TypeError):
            (simple_population
                .survive(fraction=0.5)
                .breed(parent_picker=pick_random,
                       combiner=lambda x, y: x + y, y=2))


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

    def test_mutate_elitist(self):
        pop = Population([1, 1, 3], eval_function=lambda x: x).evaluate().mutate(lambda x: x + 1, elitist=True)
        for chromosome in pop.chromosomes:
            assert chromosome > 1
        assert len(pop) == 3


class TestPopulationWeights:

    def test_weights(self, simple_chromosomes, simple_evaluation_function):
        for maximize in (False, True):
            pop = Population(chromosomes=simple_chromosomes,
                             eval_function=simple_evaluation_function, maximize=maximize)
            with raises(RuntimeError):
                assert min(pop._individual_weights) >= 0
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
        pop.mutate(mutate_function=lambda x: x - 10, probability=1).evaluate()
        assert pop.documented_best.fitness - 20 == pop.current_best.fitness


class TestPopulationIslands:

    @mark.parametrize('n_groups', [1, 2, 3, 4])
    def test_groups(self, simple_population, n_groups):
        groups = simple_population.group(group_duplicate, n_groups=n_groups)
        assert len(groups) == n_groups
        assert type(groups) == list
        assert all(type(group) is Population for group in groups)

    def test_no_groups(self, simple_population):
        with raises(ValueError):
            simple_population.group(group_duplicate, n_groups=0)

    def test_empty_group(self, simple_population):
        def rogue_grouping_function(*args):
            return [[1, 2, 3], []]

        with raises(ValueError):
            simple_population.group(rogue_grouping_function)

    @mark.parametrize('result, error', [
        (['a', 'b', 'c'], TypeError),
        ([None, None], TypeError),
        ([10, 100, 1000], IndexError)
    ])
    def test_invalid_group(self, simple_population, result, error):
        def rogue_grouping_function(*args):
            return [result]

        with raises(error):
            simple_population.group(rogue_grouping_function)

    def test_not_evaluated(self, simple_population):
        with raises(RuntimeError):
            simple_population.group(group_stratified, n_groups=3)

    def test_combine(self, simple_population):
        groups = simple_population.evaluate().group(group_stratified, n_groups=3)
        combined = Population.combine(*groups)
        assert combined.intended_size == simple_population.intended_size

    def test_combine_nothing(self):
        with raises(ValueError):
            Population.combine()


class TestContest:

    def test_assign_score(self, simple_individuals):
        contest = Contest(simple_individuals)
        contest.assign_scores(range(len(simple_individuals)))
        for score, individual in zip(range(len(simple_individuals)), simple_individuals):
            assert individual.fitness == score

    @mark.parametrize('individuals_per_contest,contests_per_round', [(2, 1), (5, 1), (7, 1), (2, 5), (5, 4), (3, 3)])
    def test_generate_n_contests(self, simple_individuals, individuals_per_contest, contests_per_round):
        contests = Contest.generate(simple_individuals, contests_per_round=contests_per_round,
                                    individuals_per_contest=individuals_per_contest)
        for contest in contests:
            contest.assign_scores([1]*individuals_per_contest)  # Now the fitness equals the number of contests played
        # All individuals competed in the same number of contests
        assert len({individual.fitness for individual in simple_individuals}) == 1
        # The number of contests is _at least_ contests_per_round
        assert all([individual.fitness >= contests_per_round for individual in simple_individuals])
        # The number of contests is smaller than contests_per_round + individuals_per_contest
        assert all([individual.fitness < contests_per_round + individuals_per_contest
                    for individual in simple_individuals])


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
        # with concurrency
        pop = ContestPopulation([0, 1, 2], lambda x, y: [0, 0], contests_per_round=100, individuals_per_contest=2,
                                concurrent_workers=3)
        pop.evaluate()
        assert pop.documented_best is None
        pop = ContestPopulation([0, 1, 2],
                                lambda x, y: [x, y],
                                contests_per_round=100, individuals_per_contest=2)
        pop.evaluate()
        assert pop.documented_best is None
        # with concurrency
        pop = ContestPopulation([0, 1, 2],
                                lambda x, y: [x, y],
                                contests_per_round=100, individuals_per_contest=2,
                                concurrent_workers=3)
        pop.evaluate()
        assert pop.documented_best is None
