from pytest import fixture

from evol import Population, ContestPopulation


@fixture(scope='module')
def simple_chromosomes():
    return list(range(-50, 50))


@fixture(scope='module')
def simple_evaluation_function():
    def eval_func(x):
        return -x ** 2
    return eval_func


@fixture(scope='module')
def simple_contest_evaluation_function():
    def eval_func(x, y, z):
        return [1, -1, 0] if x > y else [-1, 1, 0]
    return eval_func


@fixture(scope='function')
def simple_population(simple_chromosomes, simple_evaluation_function):
    return Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)


@fixture(scope='function')
def simple_contestpopulation(simple_chromosomes, simple_contest_evaluation_function):
    return ContestPopulation(chromosomes=simple_chromosomes, eval_function=simple_contest_evaluation_function,
                             contests_per_round=35, individuals_per_contest=3)
