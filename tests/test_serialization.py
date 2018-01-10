from os import listdir
from pytest import raises

from evol import Population, Evolution
from evol.serialization import SimpleSerializer


class TestPickleCheckpoint:
    method = 'pickle'
    extension = '.pkl'
    exception = AttributeError

    def test_checkpoint(self, tmpdir, simple_population):
        directory = tmpdir.mkdir("ckpt")
        simple_population.checkpoint(target=directory, method=self.method)
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

    def test_load(self, tmpdir, simple_population):
        directory = tmpdir.mkdir("ckpt")
        simple_population.checkpoint(target=directory, method=self.method)
        pop = Population.load(directory, lambda x: x['x'])
        assert len(simple_population) == len(pop)
        assert all(x.__dict__ == y.__dict__ for x, y in zip(simple_population, pop))

    def test_load_invalid_target(self, tmpdir):
        directory = tmpdir.mkdir('ckpt')
        with raises(FileNotFoundError):
            Population.load(directory.join('no_file' + self.extension), lambda x: x)
        with raises(FileNotFoundError):
            Population.load(directory, lambda x: x)
        txt_file = directory.join('file.txt')
        txt_file.write('Something')
        with raises(ValueError):
            Population.load(txt_file.strpath, lambda x: x)

    def test_checkpoint_invalid_target(self, tmpdir, simple_population):
        directory = tmpdir.mkdir("ckpt")
        with raises(ValueError):
            simple_population.checkpoint(target=None, method=self.method)
        txt_file = directory.join('file.txt')
        txt_file.write('Something')
        with raises(FileNotFoundError):
            simple_population.checkpoint(target=txt_file, method=self.method)
        # FileExistsError is difficult to test due to timing

    def test_override_default_path(self, tmpdir, simple_chromosomes, simple_evaluation_function):
        # With checkpoint_target init
        directory1 = tmpdir.mkdir("ckpt1")
        pop1 = Population(simple_chromosomes, simple_evaluation_function, checkpoint_target=directory1)
        pop1.checkpoint(method=self.method)
        assert len(listdir(directory1)) == 1
        # With serializer init
        directory2 = tmpdir.mkdir("ckpt2")
        pop2 = Population(simple_chromosomes, simple_evaluation_function,
                          serializer=SimpleSerializer(target=directory2))
        pop2.checkpoint(method=self.method)
        assert len(listdir(directory2)) == 1
        # With override
        directory3 = tmpdir.mkdir("ckpt3")
        pop1.checkpoint(target=directory3, method=self.method)
        pop2.checkpoint(target=directory3, method=self.method)
        assert len(listdir(directory3)) == 2

    def test_evolution(self, tmpdir, simple_population):
        directory = tmpdir.mkdir("ckpt")
        evo = Evolution().mutate(lambda x: x+1).checkpoint(target=directory, method=self.method, every=1)
        _ = simple_population.evolve(evolution=evo, n=100)
        assert len(listdir(directory)) == 100

    def test_every(self, tmpdir, simple_population):
        directory = tmpdir.mkdir('ckpt')
        evo = Evolution().mutate(lambda x: x+1).checkpoint(target=directory, method=self.method, every=10)
        _ = simple_population.evolve(evolution=evo, n=9)
        assert len(listdir(directory)) == 0
        _ = simple_population.evolve(evolution=evo, n=11)
        assert len(listdir(directory)) == 2


class TestJsonCheckpoint(TestPickleCheckpoint):

    method = 'json'
    extension = '.json'
    exception = TypeError
