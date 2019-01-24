from pytest import fixture

from evol import Individual, Population, ContestPopulation


@fixture(scope='module')
def simple_chromosomes():
    return list(range(-50, 50))


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


@fixture(scope='function', params=range(2))
def any_population(request, simple_population, simple_contestpopulation):
    if request.param == 0:
        return simple_population
    elif request.param == 1:
        return simple_contestpopulation
    else:
        raise ValueError("invalid internal test config")
