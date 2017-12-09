from itertools import cycle, islice
from random import randint

from .base import Population


class ContestPopulation(Population):
    """Population which is evaluated through contests.

    This variant of the Population is used when individuals cannot be
    evaluated on a one-by-one basis, but instead can only be compared to
    each other. This is typically the case for AI that performs some task
    (i.e. plays a game), but can be useful in many other cases.

    For each round of evaluation, each individual participates in a given
    number of contests, in which a given number of individuals take part.
    The resulting scores of these contests are summed to form the fitness.

    Since the fitness of an individual is dependent on the other individuals
    in the population, the fitness of all individuals is recalculated when
    new individuals are present, and the fitness of all individuals is reset
    when the population is modified (e.g. by calling survive, mutate etc).

    :param chromosomes: Collection of initial chromosomes of the Population.
    :type chromosomes: Collection[chromosome]
    :param eval_function: Function that reduces multiple chromosomes to a
        set of scores.
    :type eval_function: Callable[*chromosomes] -> tuple[float]
    :param contests_per_round: Number of contests each individual takes part
        in for each evaluation round. Defaults to 10.
    :type contests_per_round: int
    :param individuals_per_contest: Number of individuals that take part in
        each contest. The size of the population must be divisible by this
        number. Defaults to 2.
    :type individuals_per_contest: int
    :param maximize: If True, fitness will be maximized, otherwise minimized.
        Defaults to True.
    :type maximize: bool
    """
    def __init__(self, chromosomes, eval_function, contests_per_round=10, individuals_per_contest=2, maximize=True):
        Population.__init__(self, chromosomes=chromosomes, eval_function=eval_function, maximize=maximize)
        self.contests_per_round = contests_per_round
        self.individuals_per_contest = individuals_per_contest

    def evaluate(self, lazy: bool=False) -> 'ContestPopulation':
        """Evaluate the individuals in the population.

        This evaluates the fitness of all individuals. If lazy is True, the
        fitness is only evaluated when a fitness value is not yet known for
        all individuals.
        In most situations adding an explicit evaluation step is not needed, as
        lazy evaluation is implicitly included in the operations that need it
        (most notably in the survive operation).

        :param lazy: If True, do no re-evaluate the fitness if the fitness is known.
        :type lazy: bool
        :return: self
        """
        if lazy and all(individual.fitness is not None for individual in self):
            return self
        for individual in self.individuals:
            individual.fitness = 0
        for _ in range(self.contests_per_round):
            offsets = [0] + [randint(0, len(self.individuals) - 1) for _ in range(self.individuals_per_contest - 1)]
            generators = [islice(cycle(self.individuals), offset, None) for offset in offsets]
            for competitors in islice(zip(*generators), len(self.individuals)):
                scores = self.eval_function(*competitors)
                for competitor, score in zip(competitors, scores):
                    competitor.fitness += score
        return self

    def map(self, func, **kwargs) -> 'Population':
        """Apply the provided function to each individual in the population.

        Resets the fitness of all individuals.

        :param func: Function to apply to the individuals in the population.
        :type func: Callable[Individual] -> Individual
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        Population.map(self, func=func, **kwargs)
        self.reset_fitness()
        return self

    def filter(self, func, **kwargs) -> 'Population':
        """Add a filter step to the Evolution.

        Filters the individuals in the population using the provided function.
        Resets the fitness of all individuals.

        :param func: Function to filter the individuals in the population by.
        :type func: Callable[Individual] -> bool
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        Population.filter(self, func=func, **kwargs)
        self.reset_fitness()
        return self

    def survive(self, fraction=None, n=None, luck=False) -> 'ContestPopulation':
        """Let part of the population survive.

        Remove part of the population. If both fraction and n are specified,
        the minimum resulting population size is taken. Resets the fitness
        of all individuals.

        :param fraction: Fraction of the original population that survives.
            Defaults to None.
        :type fraction: float/None
        :param n: Number of individuals of the population that survive.
            Defaults to None.
        :type n: int/None
        :param luck: If True, individuals randomly survive (with replacement!)
            with chances proportional to their fitness. Defaults to False.
        :type luck: bool
        :return: self
        """
        Population.survive(self, fraction=fraction, n=n, luck=luck)
        self.reset_fitness()
        return self  # If we return the result of Population.survive PyCharm complains that it is of type 'Population'

    def reset_fitness(self):
        """Reset the fitness of all individuals."""
        for individual in self:
            individual.fitness = None
