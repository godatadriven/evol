from random import seed, shuffle

from pytest import fixture

from evol import Individual, Population, ContestPopulation, Evolution
from evol.helpers.pickers import pick_random


@fixture(scope='module')
def simple_chromosomes():
    return list(range(-50, 50))


@fixture(scope='module')
def shuffled_chromosomes():
    chromosomes = list(range(0, 100)) + list(range(0, 100)) + list(range(0, 100)) + list(range(0, 100))
    seed(0)
    shuffle(chromosomes)
    return chromosomes


@fixture(scope='function')
def simple_individuals(simple_chromosomes):
    result = [Individual(chromosome=chromosome) for chromosome in simple_chromosomes]
    for individual in result:
        individual.fitness = 0
    return result


@fixture(scope='module')
def simple_evaluation_function():
    def eval_func(x):
        return -x ** 2
    return eval_func


@fixture(scope='function')
def evaluated_individuals(simple_chromosomes, simple_evaluation_function):
    result = [Individual(chromosome=chromosome) for chromosome in simple_chromosomes]
    for individual in result:
        individual.fitness = individual.chromosome
    return result


@fixture(scope='module')
def simple_contest_evaluation_function():
    def eval_func(x, y, z):
        return [1, -1, 0] if x > y else [-1, 1, 0]
    return eval_func


@fixture(scope='module')
def simple_evolution():
    return (
        Evolution()
        .survive(fraction=0.5)
        .breed(parent_picker=pick_random(n_parents=2), combiner=lambda x, y: x + y)
        .mutate(lambda x: x + 1, probability=0.1)
    )


@fixture(scope='function')
def simple_population(simple_chromosomes, simple_evaluation_function):
    return Population(chromosomes=simple_chromosomes, eval_function=simple_evaluation_function)


@fixture(scope='function')
def simple_contestpopulation(simple_chromosomes, simple_contest_evaluation_function):
    return ContestPopulation(chromosomes=simple_chromosomes, eval_function=simple_contest_evaluation_function,
                             contests_per_round=35, individuals_per_contest=3)


@fixture(scope='function', params=range(2))
def any_population(request, simple_population, simple_contestpopulation):
    if request.param == 0:
        return simple_population
    elif request.param == 1:
        return simple_contestpopulation
    else:
        raise ValueError("invalid internal test config")
