from evol import Evolution


class TestEvolution:

    def test_add_step(self):
        evo = Evolution()
        assert len(evo.chain) == 0
        evo_step = evo._add_step('step')
        assert len(evo.chain) == 0  # original unchanged
        assert evo_step.chain == ['step']  # copy with extra step
