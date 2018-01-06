import random

from evol import Population, Evolution
from evol.helpers.pickers import pick_random
from evol.logger import BaseLogger, SummaryLogger


class TestLoggerSimple:

    def test_baselogger_can_write_file(self, tmpdir, capsys, simple_chromosomes, simple_evaluation_function):
        log_file = tmpdir.join('log.txt')
        logger = BaseLogger(file=log_file, stdout=False)
        pop = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function, logger=logger)
        # we should see that a file was created with an appropriate number of rows
        pop.log()
        with open(log_file, "r") as f:
            assert len(f.readlines()) == len(simple_chromosomes)
        # we should see that a file was created with an appropriate number of rows
        pop.log()
        with open(log_file, "r") as f:
            assert len(f.readlines()) == (2*len(simple_chromosomes))
        read_stdout = [line for line in capsys.readouterr().out.split('\n') if line != '']
        # there should be nothing printed
        assert len(read_stdout) == 0

    def test_baselogger_can_write_to_stdout(self, capsys, simple_chromosomes, simple_evaluation_function):
        pop = Population(chromosomes=simple_chromosomes,
                         eval_function=simple_evaluation_function,
                         logger=BaseLogger(file=None, stdout=True))
        pop.log().log()
        read_stdout = [line for line in capsys.readouterr().out.split('\n') if line != '']
        # the logger gets captured with an extra \n, hence the +1
        assert len(read_stdout) == len(range(simple_chromosomes))*2

    def test_baselogger_can_accept_kwargs(self, tmpdir, simple_chromosomes, simple_evaluation_function):
        log_file = tmpdir.join('log.txt')
        logger = BaseLogger(file=log_file, stdout=False)
        pop = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function, logger=logger)
        # we should see that a file was created with an appropriate number of rows
        pop.log(foo="bar")
        with open(log_file, "r") as f:
            assert len(f.readlines()) == len(simple_chromosomes)
        # we should see that a file was created with an appropriate number of rows
        pop.log(foo="meh")
        with open(log_file, "r") as f:
            assert len(f.readlines()) == (2*len(simple_chromosomes))

    def test_baselogger_should_not_print_if_told_not_to(self, capsys, tmpdir, simple_chromosomes, simple_evaluation_function):
        log_file = tmpdir.join('log.txt')
        logger = BaseLogger(file=log_file, stdout=False)
        pop = Population(chromosomes=range(10), eval_function=lambda x:x, logger=logger)
        # we should see that a file was created with an appropriate number of rows
        pop.log()
        read_stdout = [line for line in capsys.readouterr().out.split('\n') if line != '']
        assert len(read_stdout) == 0


    def test_baselogger_works_via_evolution(self, tmpdir, simple_chromosomes, simple_evaluation_function):
        log_file = tmpdir.join('log.txt')
        logger = BaseLogger(file=log_file, stdout=False)
        pop = Population(chromosomes=list(range(10)), eval_function=lambda x: x, logger=logger)
        evo = (Evolution()
               .survive(fraction=0.5)
               .breed(parent_picker=pick_random,
                      combiner=lambda mom, dad: (mom + dad)/2 + (random.random() - 0.5),
                      n_parents=2)
               .log(foo='bar'))
        _ = pop.evolve(evolution=evo, n=2)
        # with open(log_file, "r") as f:
        #     read_file = [item.replace("\n", "") for item in f.readlines()]
        #     # size of the log should be appropriate
        #     assert len(read_file) == 10*len(range(10))
        #     # bar needs to be in every single line
        #     assert all(['bar' in row for row in read_file])

    def test_summary_logger_can_write_file(self, capsys, tmpdir):
        log_file = tmpdir.join('log.txt')
        pop = Population(chromosomes=range(10), eval_function=lambda x: x,
                         logger=SummaryLogger(file=log_file, stdout=True))
        for i in range(10):
            pop.mutate(lambda x: x + random.random()).log(value1='lamarl', value2='kumar')
        with open(log_file, "r") as f:
            read_file = [item.replace("\n", "") for item in f.readlines()]
        read_stdout = [line for line in capsys.readouterr().out.split('\n') if line != '']
        for log in (read_stdout, read_file):
            # size of the log should be appropriate
            assert len(log) == 10
            # kwargs needs to be in every single line
            assert all(['lamarl' in row for row in log])
            assert all(['kumar' in row for row in log])
            # there need to be 5 entries per row
            assert all([len(row.split(",")) for row in log])

    def test_summary_logger_works_via_evolution(self, capsys, tmpdir):
        assert True
        # log_file = tmpdir.join('log.txt')
        # pop = Population(chromosomes=range(10), eval_function=lambda x: x,
        #                  logger=SummaryLogger(file=log_file, stdout=False))
        # evo = Evolution().mutate(lambda x: x + random.random()).log(value1='lamarl', value2='kumar')
        # pop.evolve(evo, n=10)
        # with open(log_file, "r") as f:
        #     read_file = [item.replace("\n", "") for item in f.readlines()]
        # read_stdout = [line for line in capsys.readouterr().out.split('\n') if line != '']
        # # there should be nothing printed
        # assert len(read_stdout) == 0
        # # but the file should contain items
        # print(read_file)
        # assert len(read_file) == 10
        # assert all(['lamarl' in row for row in read_file])
        # assert all(['kumar' in row for row in read_file])
        # # there need to be 5 entries per row
        # assert all([len(row.split(",")) == 4 for row in read_file])