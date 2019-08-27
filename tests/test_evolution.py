from pytest import mark

from evol import Evolution, Population
from evol.helpers.groups import group_random, group_duplicate, group_stratified
from evol.helpers.pickers import pick_random


class TestEvolution:

    def test_add_step(self):
        evo = Evolution()
        assert len(evo.chain) == 0
        evo_step = evo._add_step('step')
        assert len(evo.chain) == 0  # original unchanged
        assert evo_step.chain == ['step']  # copy with extra step


class TestPopulationEvolve:

    def test_repeat_step(self):
        pop = Population([0 for i in range(100)], lambda x: x)
        evo = Evolution().repeat(Evolution().survive(fraction=0.9), n=10)
        # Check whether an Evolution inside another Evolution is actually applied
        assert len(pop.evolve(evo, n=2)) < 50

    @mark.parametrize('n_groups', [2, 4, 5])
    @mark.parametrize('grouping_function', [group_stratified, group_duplicate, group_random])
    def test_repeat_step_grouped(self, n_groups, grouping_function):
        calls = []

        def callback(pop):
            calls.append(len(pop))

        sub_evo = (
            Evolution()
            .survive(fraction=0.5)
            .breed(parent_picker=pick_random,
                   combiner=lambda x, y: x + y)
            .callback(callback_function=callback)
        )

        pop = Population([0 for _ in range(100)], lambda x: x)
        evo = (
            Evolution()
            .evaluate(lazy=True)
            .repeat(sub_evo, grouping_function=grouping_function, n_groups=n_groups)
        )
        assert len(pop.evolve(evo, n=2)) == 100
        assert len(calls) == 2 * n_groups
