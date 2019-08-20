from evol import Evolution, Population
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

    def test_stop(self):
        pop = Population([0 for _ in range(10)], lambda x: x, maximize=True)
        evo = (
            Evolution()
            .survive(fraction=0.5)
            .breed(parent_picker=pick_random, combiner=lambda x: x, n_parents=1)
            .mutate(lambda x: x + 1)  # Every generation we become exactly one better
            .evaluate(lazy=True)
            .stop(lambda p: p.documented_best.fitness == 5)
        )
        pop = pop.evolve(evo, n=100)
        assert pop.generation == 5
