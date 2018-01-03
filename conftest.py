from pytest import fixture

from evol import Population


@fixture(scope='module')
def simple_chromosomes():
    return list(range(-5, 5))


@fixture(scope='module')
def simple_evaluation_function():
    def eval_func(x):
        return -x ** 2
    return eval_func


@fixture(scope='module')
def simple_population(simple_chromosomes, simple_evaluation_function):
    return Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)
