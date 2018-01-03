from os import listdir
from pytest import raises

from evol import Population, Evolution


class TestPickleCheckpoint:
    method = 'pickle'
    extension = '.pkl'
    exception = AttributeError

    def test_checkpoint(self, tmpdir):
        directory = tmpdir.mkdir("ckpt")
        pop = Population([{'x': 1, 'y': 2} for _ in range(100)], lambda x: x['x'])
        pop.checkpoint(directory=directory, method=self.method)
        assert len(listdir(directory)) == 1
        assert listdir(directory)[0].endswith(self.extension)

    def test_unserializable_chromosome(self, tmpdir):
        directory = tmpdir.mkdir("ckpt")

        class UnSerializableChromosome:
            def __init__(self, x):
                self.x = x

        pop = Population([UnSerializableChromosome(i) for i in range(10)], lambda x: x.x)
        with raises(self.exception):
            pop.checkpoint(directory=directory, method=self.method)

    def test_load(self, tmpdir):
        directory = tmpdir.mkdir("ckpt")
        pop = Population([{'x': 1, 'y': 2} for _ in range(100)], lambda x: x['x'])
        pop.checkpoint(directory=directory, method=self.method)
        lpop = Population.load(directory, lambda x: x['x'])
        assert len(pop) == len(lpop)
        assert all(x.__dict__ == y.__dict__ for x, y in zip(pop, lpop))

    def test_evolution(self, tmpdir):
        directory = tmpdir.mkdir("ckpt")
        evo = Evolution().mutate(lambda x: x+1).checkpoint(directory=directory, method=self.method, every=1)
        pop = Population(range(100), lambda x: x)
        pop.evolve(evolution=evo, n=100)
        assert len(listdir(directory)) == 100

    def test_every(self, tmpdir):
        directory = tmpdir.mkdir('ckpt')
        evo = Evolution().mutate(lambda x: x+1).checkpoint(directory=directory, method=self.method, every=10)
        pop = Population(range(100), lambda x: x)
        pop.evolve(evolution=evo, n=9)
        assert len(listdir(directory)) == 0
        pop.evolve(evolution=evo, n=11)
        assert len(listdir(directory)) == 2


class TestJsonCheckpoint(TestPickleCheckpoint):

    method = 'json'
    extension = '.json'
    exception = TypeError
