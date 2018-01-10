from os import listdir
from pytest import raises

from evol import Population, Evolution
from evol.serialization import SimpleSerializer


class TestPickleCheckpoint:
    method = 'pickle'
    extension = '.pkl'
    exception = AttributeError

    def test_checkpoint(self, tmpdir):
        directory = tmpdir.mkdir("ckpt")
        pop = Population([{'x': 1, 'y': 2} for _ in range(100)], lambda x: x['x'])
        pop.checkpoint(target=directory, method=self.method)
        assert len(listdir(directory)) == 1
        assert listdir(directory)[0].endswith(self.extension)

    def test_unserializable_chromosome(self, tmpdir):
        directory = tmpdir.mkdir("ckpt")

        class UnSerializableChromosome:
            def __init__(self, x):
                self.x = x

        pop = Population([UnSerializableChromosome(i) for i in range(10)], lambda x: x.x)
        with raises(self.exception):
            pop.checkpoint(target=directory, method=self.method)

    def test_load(self, tmpdir):
        directory = tmpdir.mkdir("ckpt")
        pop = Population([{'x': 1, 'y': 2} for _ in range(100)], lambda x: x['x'])
        pop.checkpoint(target=directory, method=self.method)
        lpop = Population.load(directory, lambda x: x['x'])
        assert len(pop) == len(lpop)
        assert all(x.__dict__ == y.__dict__ for x, y in zip(pop, lpop))

    def test_load_invalid_target(self, tmpdir):
        directory = tmpdir.mkdir('ckpt')
        with raises(FileNotFoundError):
            Population.load(directory.join('no_file'), lambda x: x)
        with raises(FileNotFoundError):
            Population.load(directory, lambda x: x)
        txt_file = directory.join('file.txt')
        txt_file.write('Something')
        with raises(ValueError):
            Population.load(txt_file.strpath, lambda x: x)

    def test_checkpoint_invalid_target(self, tmpdir):
        directory = tmpdir.mkdir("ckpt")
        pop = Population([{'x': 1, 'y': 2} for _ in range(100)], lambda x: x['x'])
        with raises(ValueError):
            pop.checkpoint(target=None)
        txt_file = directory.join('file.txt')
        txt_file.write('Something')
        with raises(FileNotFoundError):
            pop.checkpoint(target=txt_file)
        # FileExistsError is difficult to test due to timing

    def test_override_default_path(self, tmpdir):
        # With checkpoint_target init
        directory1 = tmpdir.mkdir("ckpt1")
        pop1 = Population([list(range(100))], lambda x: x, checkpoint_target=directory1)
        pop1.checkpoint()
        assert len(listdir(directory1)) == 1
        # With serializer init
        directory2 = tmpdir.mkdir("ckpt2")
        pop2 = Population([list(range(100))], lambda x: x, serializer=SimpleSerializer(target=directory2))
        pop2.checkpoint()
        assert len(listdir(directory2)) == 1
        # With override
        directory3 = tmpdir.mkdir("ckpt3")
        pop1.checkpoint(target=directory3)
        pop2.checkpoint(target=directory3)
        assert len(listdir(directory3)) == 2

    def test_evolution(self, tmpdir):
        directory = tmpdir.mkdir("ckpt")
        evo = Evolution().mutate(lambda x: x+1).checkpoint(target=directory, method=self.method, every=1)
        pop = Population(range(100), lambda x: x)
        pop.evolve(evolution=evo, n=100)
        assert len(listdir(directory)) == 100

    def test_every(self, tmpdir):
        directory = tmpdir.mkdir('ckpt')
        evo = Evolution().mutate(lambda x: x+1).checkpoint(target=directory, method=self.method, every=10)
        pop = Population(range(100), lambda x: x)
        pop.evolve(evolution=evo, n=9)
        assert len(listdir(directory)) == 0
        pop.evolve(evolution=evo, n=11)
        assert len(listdir(directory)) == 2


class TestJsonCheckpoint(TestPickleCheckpoint):

    method = 'json'
    extension = '.json'
    exception = TypeError
