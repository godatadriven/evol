from evol import Evolution, Population


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
