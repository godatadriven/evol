from random import random, choices, seed

from pytest import raises

from evol import Population, ContestPopulation


class TestPopulation:

    @property
    def chromosomes(self):
        return list(range(200))

    @staticmethod
    def eval_func(x):
        return 2*x

    @staticmethod
    def pick_n_random_parents(population, n_parents=2):
        return choices(population, k=n_parents)

    @property
    def population(self):
        return Population(chromosomes=[1 for _ in range(100)], eval_function=float)


class TestPopulationSimple(TestPopulation):

    def test_filter_works(self):
        pop = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        assert len(pop.filter(func=lambda i: random() > 0.5)) < 200

    def test_population_init(self):
        pop = Population(self.chromosomes, eval_function=lambda x: x)
        assert len(pop) == len(self.chromosomes)
        assert pop.intended_size == len(pop)

    def test_population_generate(self):
        def init_func():
            return 1

        pop = Population.generate(init_func=init_func, eval_func=lambda x: x, size=200)
        assert len(pop) == 200
        assert pop.intended_size == 200
        assert pop.individuals[0].chromosome == 1


class TestPopulationEvaluate(TestPopulation):

    def test_individuals_are_not_initially_evaluated(self):
        pop = Population(self.chromosomes, eval_function=lambda x: x)
        assert all([i.fitness is None for i in pop])

    def test_evaluate_lambda(self):
        pop = Population(self.chromosomes, eval_function=lambda x: x)
        pop.evaluate()
        for individual in pop:
            assert individual.chromosome == individual.fitness

    def test_evaluate_func(self):
        def evaluation_function(x):
            return x*x
        pop = Population(self.chromosomes, eval_function=evaluation_function)
        pop.evaluate()
        for individual in pop:
            assert evaluation_function(individual.chromosome) == individual.fitness

    def test_evaluate_lazy(self):
        pop = Population(self.chromosomes, eval_function=lambda x: x)
        pop.evaluate(lazy=True)  # should evaluate

        def raise_function(_):
            raise Exception

        pop.eval_function = raise_function
        pop.evaluate(lazy=True)  # should not evaluate
        with raises(Exception):
            pop.evaluate(lazy=False)


class TestPopulationSurvive(TestPopulation):

    def test_survive_n_works(self):
        pop1 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        pop2 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        pop3 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        assert len(pop1) == 200
        assert len(pop2.survive(n=50)) == 50
        assert len(pop3.survive(n=150, luck=True)) == 150

    def test_survive_p_works(self):
        pop1 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        pop2 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        pop3 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        assert len(pop1) == 200
        assert len(pop2.survive(fraction=0.5)) == 100
        assert len(pop3.survive(fraction=0.1, luck=True)) == 20

    def test_survive_n_and_p_works(self):
        pop1 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        pop2 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        pop3 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        assert len(pop1.survive(fraction=0.5, n=200)) == 100
        assert len(pop2.survive(fraction=0.9, n=10)) == 10
        assert len(pop3.survive(fraction=0.5, n=190, luck=True)) == 100

    def test_survive_throws_correct_errors(self):
        """If the resulting population is zero or larger than initial we need to see errors."""
        pop1 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        with raises(RuntimeError):
            pop1.survive(n=0)
        pop2 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        with raises(ValueError):
            pop2.survive(n=250)
        pop3 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        with raises(ValueError):
            pop3.survive()


class TestPopulationBreed(TestPopulation):

    def test_breed_amount_works(self):
        pop1 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        pop1.survive(n=50).breed(parent_picker=lambda population: choices(population, k=2),
                                 combiner=lambda mom, dad: (mom + dad) / 2)
        assert len(pop1) == 200
        pop2 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        pop2.survive(n=50).breed(parent_picker=lambda population: choices(population, k=2),
                                 combiner=lambda mom, dad: (mom + dad) / 2, population_size=400)
        assert len(pop2) == 400
        assert pop2.intended_size == 400

    def test_breed_works_with_kwargs(self):
        pop1 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        pop1.survive(n=50).breed(parent_picker=self.pick_n_random_parents,
                                 combiner=lambda mom, dad: (mom + dad) / 2,
                                 n_parents=2)
        assert len(pop1) == 200
        pop2 = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        pop2.survive(n=50).breed(parent_picker=self.pick_n_random_parents,
                                 combiner=lambda *parents: sum(parents)/len(parents),
                                 population_size=400, n_parents=3)
        assert len(pop2) == 400
        assert pop2.intended_size == 400


class TestPopulationMutate(TestPopulation):

    def test_mutate_lambda(self):
        pop = self.population.mutate_with(lambda x: x + 1)
        for chromosome in pop.chromosomes:
            assert chromosome == 2
        assert len(pop) == 100

    def test_mutate_inplace(self):
        population = self.population
        population.mutate_with(lambda x: x + 1)
        for chromosome in population.chromosomes:
            assert chromosome == 2

    def test_mutate_func(self):
        def mutate_func(x):
            return -x
        population = self.population
        population.mutate_with(mutate_func)
        for chromosome in population.chromosomes:
            assert chromosome == -1
        assert len(self.population) == 100

    def test_mutate_probability(self):
        seed(0)
        pop = self.population.mutate_with(lambda x: x + 1, probability=0.5).evaluate()
        assert min(individual.chromosome for individual in pop.individuals) == 1
        assert max(individual.chromosome for individual in pop.individuals) == 2
        assert pop.current_best.fitness == 2
        assert pop.documented_best.fitness == 2
        assert len(pop) == 100

    def test_mutate_zero_probability(self):
        pop = self.population.mutate_with(lambda x: x + 1, probability=0)
        for chromosome in pop.chromosomes:
            assert chromosome == 1

    def test_mutate_func_kwargs(self):
        def mutate_func(x, y=0):
            return x+y
        pop = self.population.mutate_with(mutate_func, y=16)
        for chromosome in pop.chromosomes:
            assert chromosome == 17


class TestPopulationBest(TestPopulation):

    def test_current_best(self):
        for maximize, best in ((True, 199), (False, 0)):
            pop = Population(chromosomes=self.chromosomes, eval_function=self.eval_func, maximize=maximize)
            assert pop.current_best is None
            pop.evaluate()
            assert pop.current_best.chromosome == best

    def test_current_worst(self):
        for maximize, worst in ((False, 199), (True, 0)):
            pop = Population(chromosomes=self.chromosomes, eval_function=self.eval_func, maximize=maximize)
            assert pop.current_worst is None
            pop.evaluate()
            assert pop.current_worst.chromosome == worst

    def test_mutate_resets(self):
        pop = self.population
        assert pop.current_best is None and pop.current_worst is None
        pop.evaluate()
        assert pop.current_best.fitness == 1 and pop.current_worst.fitness == 1
        pop.mutate_with(lambda x: x)
        assert pop.current_best is None and pop.current_worst is None

    def test_documented_best(self):
        pop = Population(chromosomes=self.chromosomes, eval_function=self.eval_func)
        assert pop.documented_best is None
        pop.evaluate()
        assert pop.documented_best.fitness == pop.current_best.fitness
        pop.mutate_with(mutate_func=lambda x: x - 10, probability=1).evaluate()
        assert pop.documented_best.fitness - 20 == pop.current_best.fitness


class TestContestPopulation(TestPopulation):

    def test_init(self):
        cp = ContestPopulation([0, 1, 2], lambda x: x, contests_per_round=15, individuals_per_contest=15)
        assert cp.contests_per_round == 15
        assert cp.individuals_per_contest == 15

    @staticmethod
    def check_no_fitness(population):
        for individual in population:
            assert individual.fitness is None


class TestContestPopulationBest(TestPopulation):

    def test_no_documented(self):
        pop = ContestPopulation([0, 1, 2], lambda x, y: [0, 0], contests_per_round=100, individuals_per_contest=2)
        pop.evaluate()
        assert pop.documented_best is None
