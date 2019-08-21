from time import monotonic

from pytest import raises

from evol import Population
from evol.conditions import Condition, MinimumProgress, TimeLimit
from evol.exceptions import StopEvolution


class TestCondition:

    def test_context(self):
        with Condition(lambda pop: False):
            assert len(Condition.conditions) == 1
            with TimeLimit(60):
                assert len(Condition.conditions) == 2
        assert len(Condition.conditions) == 0

    def test_check(self, simple_population):
        with Condition(lambda pop: False):
            with raises(StopEvolution):
                Condition.check(simple_population)
        Condition.check(simple_population)

    def test_evolve(self, simple_population, simple_evolution):
        with Condition(lambda pop: False):
            result = simple_population.evolve(simple_evolution, n=3)
        assert result.generation == 0


class TestMinimumProgress:

    def test_evolve(self, simple_evolution):
        # The initial population contains the optimal solution.
        pop = Population(list(range(100)), eval_function=lambda x: x**2, maximize=False)
        with MinimumProgress(window=10):
            pop = pop.evolve(simple_evolution, n=100)
        assert pop.generation == 10


class TestTimeLimit:

    def test_evolve(self, simple_population, simple_evolution):
        start_time = monotonic()
        with TimeLimit(seconds=1):
            pop = simple_population.evolve(simple_evolution, n=10000)
        assert monotonic() - start_time > 1
        assert pop.generation < 10000
