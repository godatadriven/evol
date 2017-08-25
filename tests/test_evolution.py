from unittest import TestCase

from evol import Evolution, Population


class TestEvolution(TestCase):

    def test_add_step(self):
        evo = Evolution()
        self.assertListEqual(evo.chain, [])
        evo_step = evo._add_step('step')
        self.assertListEqual(evo.chain, [])  # original unchanged
        self.assertListEqual(evo_step.chain, ['step'])  # copy with extra step


