import random
import os
from uuid import uuid4
from evol import Population, Evolution
from evol.logger import BaseLogger, SummaryLogger


class TestPopulation:

    @staticmethod
    def eval_func(x):
        return -x**2

    @staticmethod
    def pick_n_random_parents(population, n_parents=2):
        return random.choices(population, k=n_parents)

    @property
    def chromosomes(self):
        return [_ for _ in range(-10, 10)]


class TestPopulationSimple(TestPopulation):

    def test_baselogger_can_write_file(self):
        filepath = f"/tmp/evol-{str(uuid4())[:6]}.log"
        logger = BaseLogger(file=filepath, stdout=False)
        pop = Population(chromosomes=self.chromosomes, eval_function=self.eval_func, logger=logger)
        # we should see that a file was created with an appropriate number of rows
        pop.log()
        with open(filepath, "r") as f:
            assert len(f.readlines()) == len(self.chromosomes)
        # we should see that a file was created with an appropriate number of rows
        pop.log()
        with open(filepath, "r") as f:
            assert len(f.readlines()) == (2*len(self.chromosomes))
        os.remove(filepath)

    def test_baselogger_can_accept_kwargs(self):
        filepath = f"/tmp/evol-{str(uuid4())[:6]}.log"
        logger = BaseLogger(file=filepath, stdout=False)
        pop = Population(chromosomes=self.chromosomes, eval_function=self.eval_func, logger=logger)
        for i in range(10):
            pop = (pop
               .survive(fraction=0.5)
               .breed(parent_picker=self.pick_n_random_parents,
                      combiner=lambda mom, dad: (mom + dad)/2 + (random.random() - 0.5),
                      n_parents=2)
               .log(foo='bar', baz=i))
        with open(filepath, "r") as f:
            read_file = [item.replace("\n", "") for item in f.readlines()]
            # size of the log should be appropriate
            assert len(read_file) == 10*len(self.chromosomes)
            # bar needs to be in every single line
            assert all(['bar' in row for row in read_file])
            # last item in first row must be zero for i starts at zero
            assert read_file[0][-1] == '0'
            # last item in first row must be nine for i ends at nine
            assert read_file[-1][-1] == '9'
        os.remove(filepath)

    def test_baselogger_works_via_evolution(self):
        filepath = f"/tmp/evol-{str(uuid4())[:6]}.log"
        logger = BaseLogger(file=filepath, stdout=False)
        pop = Population(chromosomes=self.chromosomes, eval_function=self.eval_func, logger=logger)
        evo = (Evolution()
            .survive(fraction=0.5)
            .breed(parent_picker=self.pick_n_random_parents,
                   combiner=lambda mom, dad: (mom + dad)/2 + (random.random() - 0.5),
                   n_parents=2)
            .log(foo='bar'))
        pop = pop.evolve(evolution=evo, n=10)
        with open(filepath, "r") as f:
            read_file = [item.replace("\n", "") for item in f.readlines()]
            # size of the log should be appropriate
            assert len(read_file) == 10*len(self.chromosomes)
            # bar needs to be in every single line
            assert all(['bar' in row for row in read_file])
        os.remove(filepath)

    def test_summary_logger_can_write_file(self):
        filepath = f"/tmp/evol-{str(uuid4())[:6]}.log"
        logger = SummaryLogger(file=filepath, stdout=False)
        pop = Population(chromosomes=self.chromosomes, eval_function=self.eval_func, logger=logger)
        evo = (Evolution()
               .survive(fraction=0.5)
               .breed(parent_picker=self.pick_n_random_parents,
                      combiner=lambda mom, dad: (mom + dad) / 2 + (random.random() - 0.5),
                      n_parents=2)
               .log(bar='foo'))
        pop = pop.evolve(evolution=evo, n=100)
        with open(filepath, "r") as f:
            read_file = [item.replace("\n", "") for item in f.readlines()]
            # size of the log should be appropriate
            assert len(read_file) == 100
            # bar needs to be in every single line
            assert all(['foo' in row for row in read_file])
