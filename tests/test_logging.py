import random

from evol import Population, Evolution
from evol.helpers.pickers import pick_random
from evol.logger import BaseLogger, SummaryLogger


class TestLoggerSimple:

    def test_baselogger_can_write_file_without_stdout(self, tmpdir, capsys, simple_chromosomes, simple_evaluation_function):
        log_file = tmpdir.join('log.txt')
        logger = BaseLogger(target=log_file, stdout=False)
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
                         eval_function=lambda x: x,
                         logger=BaseLogger(target=None, stdout=True))
        pop.log()
        read_stdout = [line for line in capsys.readouterr().out.split('\n') if line != '']
        assert len(read_stdout) == len(pop)

    def test_baselogger_can_accept_kwargs(self, tmpdir, simple_chromosomes, simple_evaluation_function):
        log_file = tmpdir.join('log.txt')
        logger = BaseLogger(target=log_file, stdout=False)
        pop = Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function, logger=logger)
        # we should see that a file was created with an appropriate number of rows
        pop.log(foo="bar")
        with open(log_file, "r") as f:
            assert len(f.readlines()) == len(simple_chromosomes)
            assert all(["bar" in l for l in f.readlines()])
        # we should see that a file was created with an appropriate number of rows
        pop.log(foo="meh")
        with open(log_file, "r") as f:
            assert len(f.readlines()) == (2*len(simple_chromosomes))
            assert all(['meh' in l for l in f.readlines()[-10:]])

    def test_baselogger_works_via_evolution(self, tmpdir, capsys):
        log_file = tmpdir.join('log.txt')
        logger = BaseLogger(target=log_file, stdout=True)
        pop = Population(chromosomes=range(10), eval_function=lambda x: x, logger=logger)
        evo = (Evolution()
               .survive(fraction=0.5)
               .breed(parent_picker=pick_random,
                      combiner=lambda mom, dad: (mom + dad)/2 + (random.random() - 0.5),
                      n_parents=2)
               .log(foo='bar'))
        pop.evolve(evolution=evo, n=2)
        # check characteristics of the file
        with open(log_file, "r") as f:
            read_file = [item.replace("\n", "") for item in f.readlines()]
            # size of the log should be appropriate
            assert len(read_file) == 2*len(pop)
            # bar needs to be in every single line
            assert all(['bar' in row for row in read_file])
        # check characteristics of stoud
        read_stdout = [line for line in capsys.readouterr().out.split('\n') if line != '']
        assert len(read_stdout) == 2 * len(pop)
        assert all(['bar' in row for row in read_stdout])

    def test_summarylogger_can_write_file_without_stdout(self, tmpdir, capsys, simple_chromosomes, simple_evaluation_function):
        log_file = tmpdir.join('log.txt')
        logger = SummaryLogger(target=log_file, stdout=False)
        pop = Population(chromosomes=range(10), eval_function=lambda x: x, logger=logger)
        # we should see that a file was created with an appropriate number of rows
        pop.log()
        with open(log_file, "r") as f:
            assert len(f.readlines()) == 1
        # we should see that a file was created with an appropriate number of rows
        pop.log()
        with open(log_file, "r") as f:
            assert len(f.readlines()) == 2
        read_stdout = [line for line in capsys.readouterr().out.split('\n') if line != '']
        # there should be nothing printed
        assert len(read_stdout) == 0

    def test_summarylogger_can_write_to_stdout(self, capsys, simple_chromosomes, simple_evaluation_function):
        pop = Population(chromosomes=range(10),
                         eval_function=lambda x: x,
                         logger=SummaryLogger(target=None, stdout=True))
        pop.log().log()
        read_stdout = [line for line in capsys.readouterr().out.split('\n') if line != '']
        assert len(read_stdout) == 2

    def test_summary_logger_can_accept_kwargs(self, tmpdir, simple_chromosomes, simple_evaluation_function):
        log_file = tmpdir.join('log.txt')
        logger = SummaryLogger(target=log_file, stdout=False)
        pop = Population(chromosomes=simple_chromosomes,
                         eval_function=simple_evaluation_function, logger=logger)
        # lets make a first simple log
        pop.log(foo="bar", buzz="meh")
        with open(log_file, "r") as f:
            read_lines = f.readlines()
            assert len(read_lines) == 1
            first_line = read_lines[0]
            assert "bar" in first_line
            assert "meh" in first_line
            last_entry = first_line.split(",")
            assert len(last_entry) == 6
        # lets log another one
        pop.log(buzz="moh")
        with open(log_file, "r") as f:
            read_lines = f.readlines()
            assert len(read_lines) == 2
            first_line = read_lines[-1]
            assert "moh" in first_line
            last_entry = first_line.split(",")
            assert len(last_entry) == 5

    def test_summarylogger_works_via_evolution(self, tmpdir, capsys):
        log_file = tmpdir.join('log.txt')
        logger = SummaryLogger(target=log_file, stdout=True)
        pop = Population(chromosomes=list(range(10)), eval_function=lambda x: x, logger=logger)
        evo = (Evolution()
               .survive(fraction=0.5)
               .breed(parent_picker=pick_random,
                      combiner=lambda mom, dad: (mom + dad)/2 + (random.random() - 0.5),
                      n_parents=2)
               .log(foo='bar'))
        pop.evolve(evolution=evo, n=5)
        # check characteristics of the file
        with open(log_file, "r") as f:
            read_file = [item.replace("\n", "") for item in f.readlines()]
            # size of the log should be appropriate
            assert len(read_file) == 5
            # bar needs to be in every single line
            assert all(['bar' in row for row in read_file])
        # check characteristics of stoud
        read_stdout = [line for line in capsys.readouterr().out.split('\n') if line != '']
        assert len(read_stdout) == 5
        assert all(['bar' in row for row in read_stdout])

    def test_two_populations_can_use_same_logger(self, tmpdir, capsys):
        log_file = tmpdir.join('log.txt')
        logger = SummaryLogger(target=log_file, stdout=True)
        pop1 = Population(chromosomes=list(range(10)), eval_function=lambda x: x, logger=logger)
        pop2 = Population(chromosomes=list(range(10)), eval_function=lambda x: x, logger=logger)
        evo = (Evolution()
               .survive(fraction=0.5)
               .breed(parent_picker=pick_random,
                      combiner=lambda mom, dad: (mom + dad) + 1,
                      n_parents=2)
               .log(foo="dino"))
        pop1.evolve(evolution=evo, n=5)
        pop2.evolve(evolution=evo, n=5)
        # two evolutions have now been applied, lets check the output!
        with open(log_file, "r") as f:
            read_file = [item.replace("\n", "") for item in f.readlines()]
            # print(read_file)
            # size of the log should be appropriate
            assert len(read_file) == 10
            # dino needs to be in every single line
            assert all(['dino' in row for row in read_file])
        # check characteristics of stoud
        read_stdout = [line for line in capsys.readouterr().out.split('\n') if line != '']
        assert len(read_stdout) == 10
        assert all(['dino' in row for row in read_stdout])

    def test_every_mechanic_in_evolution_log(self, tmpdir, capsys):
        log_file = tmpdir.join('log.txt')
        logger = SummaryLogger(target=log_file, stdout=True)
        pop = Population(chromosomes=list(range(10)), eval_function=lambda x: x, logger=logger)
        evo = (Evolution()
               .survive(fraction=0.5)
               .breed(parent_picker=pick_random,
                      combiner=lambda mom, dad: (mom + dad) + 1,
                      n_parents=2)
               .log(every=2))
        pop.evolve(evolution=evo, n=100)
        with open(log_file, "r") as f:
            read_file = [item.replace("\n", "") for item in f.readlines()]
            assert len(read_file) == 50
        # check characteristics of stoud
        read_stdout = [line for line in capsys.readouterr().out.split('\n') if line != '']
        assert len(read_stdout) == 50
