from os import listdir
from pytest import raises

from evol import Population, Evolution


class TestCheckpoint:

    @property
    def methods(self):
        return 'pickle', 'json'

    def test_checkpoint(self, tmpdir):
        directory = tmpdir.mkdir("ckpt")
        for method in self.methods:
            pop = Population([{'x': 1, 'y': 2} for _ in range(100)], lambda x: x['x'])
            pop.checkpoint(directory=directory, method=method)
        assert len(listdir(directory)) == 2
        assert sorted(listdir(directory))[0].endswith('.pkl')
        assert sorted(listdir(directory))[1].endswith('.json')

    def test_unserializable_chromosome(self, tmpdir):
        directory = tmpdir.mkdir("ckpt")

        class UnSerializableChromosome:
            def __init__(self, x):
                self.x = x

        pop = Population([UnSerializableChromosome(i) for i in range(10)], lambda x: x.x)
        with raises(AttributeError):
            pop.checkpoint(directory=directory, method='pickle')
        with raises(TypeError):
            pop.checkpoint(directory=directory, method='json')

    def test_load(self, tmpdir):
        directory = tmpdir.mkdir("ckpt")
        for method in self.methods:
            pop = Population([{'x': 1, 'y': 2} for _ in range(100)], lambda x: x['x'])
            pop.checkpoint(directory=directory, method=method)
            lpop = Population.load(directory, lambda x: x['x'])
            assert len(pop) == len(lpop)
            assert all(x.__dict__ == y.__dict__ for x, y in zip(pop, lpop))

    def test_evolution(self, tmpdir):
        directory = tmpdir.mkdir("ckpt")
        evo = Evolution().mutate(lambda x: x+1).checkpoint(directory=directory)
        pop = Population(range(100), lambda x: x)
        pop.evolve(evolution=evo, n=100)
        assert len(listdir(directory)) == 100
