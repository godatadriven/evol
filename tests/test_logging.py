from uuid import uuid4

import os
import random

from evol import Population, Evolution
from evol.helpers.pickers import pick_random
from evol.logger import BaseLogger, SummaryLogger


class TestPopulationSimple:

    def test_baselogger_can_write_file(self, simple_chromosomes, simple_evaluation_function):
        filepath = f"/tmp/evol-{str(uuid4())[:6]}.log"
        logger = BaseLogger(file=filepath, stdout=False)
        pop = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function, logger=logger)
        # we should see that a file was created with an appropriate number of rows
        pop.log()
        with open(filepath, "r") as f:
            assert len(f.readlines()) == len(simple_chromosomes)
        # we should see that a file was created with an appropriate number of rows
        pop.log()
        with open(filepath, "r") as f:
            assert len(f.readlines()) == (2*len(simple_chromosomes))
        os.remove(filepath)

    def test_baselogger_can_accept_kwargs(self, simple_chromosomes, simple_evaluation_function):
        filepath = f"/tmp/evol-{str(uuid4())[:6]}.log"
        logger = BaseLogger(file=filepath, stdout=False)
        pop = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function, logger=logger)
        for i in range(10):
            pop = (pop
                   .survive(fraction=0.5)
                   .breed(parent_picker=pick_random,
                          combiner=lambda mom, dad: (mom + dad)/2 + (random.random() - 0.5),
                          n_parents=2)
                   .log(foo='bar', baz=i))
        with open(filepath, "r") as f:
            read_file = [item.replace("\n", "") for item in f.readlines()]
            # size of the log should be appropriate
            assert len(read_file) == 10*len(simple_chromosomes)
            # bar needs to be in every single line
            assert all(['bar' in row for row in read_file])
            # last item in first row must be zero for i starts at zero
            assert read_file[0][-1] == '0'
            # last item in first row must be nine for i ends at nine
            assert read_file[-1][-1] == '9'
        os.remove(filepath)

    def test_baselogger_works_via_evolution(self, simple_chromosomes, simple_evaluation_function):
        filepath = f"/tmp/evol-{str(uuid4())[:6]}.log"
        logger = BaseLogger(file=filepath, stdout=False)
        pop = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function, logger=logger)
        evo = (Evolution()
               .survive(fraction=0.5)
               .breed(parent_picker=pick_random,
                      combiner=lambda mom, dad: (mom + dad)/2 + (random.random() - 0.5),
                      n_parents=2)
               .log(foo='bar'))
        _ = pop.evolve(evolution=evo, n=10)
        with open(filepath, "r") as f:
            read_file = [item.replace("\n", "") for item in f.readlines()]
            # size of the log should be appropriate
            assert len(read_file) == 10*len(simple_chromosomes)
            # bar needs to be in every single line
            assert all(['bar' in row for row in read_file])
        os.remove(filepath)

    def test_summary_logger_can_write_file(self):
        filepath = f"/tmp/evol-summary-{str(uuid4())[:6]}.log"
        pop = Population(chromosomes=range(10), eval_function=lambda x: x,
                         logger=SummaryLogger(file=filepath, stdout=True))
        for i in range(10):
            pop.mutate(lambda x: x + random.random()).log(value1='lamarl', value2='kumar')
        with open(filepath, "r") as f:
            read_file = [item.replace("\n", "") for item in f.readlines()]
            print(filepath, read_file)
            # size of the log should be appropriate
            assert len(read_file) == 10
            # kwargs needs to be in every single line
            assert all(['lamarl' in row for row in read_file])
            assert all(['kumar' in row for row in read_file])
            # there need to be 5 entries per row
            assert all([len(row.split(",")) for row in read_file])
        os.remove(filepath)
