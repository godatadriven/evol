from evol import Population, Evolution
from evol.exceptions import StopEvolution


class PopCounter:
    def __init__(self):
        self.count = 0
        self.sum = 0

    def add(self, pop):
        for i in pop:
            self.count += 1
            self.sum += i.chromosome


class TestPopulationSimple:
    def test_simple_counter_works(self, simple_chromosomes, simple_evaluation_function):
        counter = PopCounter()

        pop = Population(chromosomes=simple_chromosomes,
                         eval_function=simple_evaluation_function)
        evo = (Evolution()
               .mutate(lambda x: x)
               .callback(lambda p: counter.add(p)))

        pop.evolve(evolution=evo, n=1)
        assert counter.count == len(simple_chromosomes)
        assert counter.sum == sum(simple_chromosomes)
        pop.evolve(evolution=evo, n=10)
        assert counter.count == len(simple_chromosomes) * 11
        assert counter.sum == sum(simple_chromosomes) * 11

    def test_simple_counter_works_every(self, simple_chromosomes, simple_evaluation_function):
        counter = PopCounter()

        pop = Population(chromosomes=simple_chromosomes,
                         eval_function=simple_evaluation_function)
        evo = (Evolution()
               .mutate(lambda x: x)
               .callback(lambda p: counter.add(p), every=2))

        pop.evolve(evolution=evo, n=10)
        assert counter.count == len(simple_chromosomes) * 5
        assert counter.sum == sum(simple_chromosomes) * 5

    def test_is_evaluated(self, simple_population):
        def assert_is_evaluated(pop: Population):
            assert pop.current_best is not None

        simple_population.evaluate(lazy=True)
        simple_population.callback(assert_is_evaluated)

    def test_stop(self, simple_population, simple_evolution):

        def func(pop):
            if pop.generation == 5:
                raise StopEvolution

        evo = simple_evolution.callback(func)
        assert simple_population.evolve(evo, n=10).generation == 5
