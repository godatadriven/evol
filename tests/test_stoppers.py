from pytest import mark

from evol import Evolution, Population
from evol.helpers.pickers import pick_random
from evol.stoppers import MinimumProgressStopper, NoProgressStopper


class TestNoProgressStopper:

    @mark.parametrize('patience', [1, 5, 10])
    def test_stop(self, patience):
        pop = Population([1]*10, eval_function=lambda x: x**2, maximize=False)
        stopper = NoProgressStopper(patience=patience)
        evo = (Evolution().survive(fraction=0.5).breed(parent_picker=pick_random, combiner=lambda x: x, n_parents=1)
               .mutate(lambda x: x - 1).stop(stopper))
        pop = pop.evolve(evo, n=100)
        assert pop.generation == 1 + patience


class TestMinimumProgressStopper:

    @mark.parametrize('window', [1, 5, 10])
    def test_stop(self, window):
        pop = Population([1] * 10, eval_function=lambda x: x ** 2, maximize=False)
        stopper = MinimumProgressStopper(window=window, minimum_change=0.5)
        evo = (Evolution().survive(fraction=0.5).breed(parent_picker=pick_random, combiner=lambda x: x, n_parents=1)
               .mutate(lambda x: x - 1).stop(stopper))
        pop = pop.evolve(evo, n=100)
        assert pop.generation == 1 + window
