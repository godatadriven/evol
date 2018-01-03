"""
Population objects in `evol` are a collection of chromosomes
at some point in an evolutionary algorithm. You can apply 
evolutionary steps by directly calling methods on the population
or by appyling an `evol.Evolution` object. 
"""

from copy import copy
from itertools import islice
from random import choices
from random import choices, randint
from copy import deepcopy, copy
from itertools import cycle, islice
from uuid import uuid4
import datetime as dt

from evol import Individual
from evol.logger import BaseLogger
from evol.helpers.utils import select_arguments, offspring_generator
from .base import PopulationBase
from .island import IslandPopulation


class Population(PopulationBase):
    """Population of Individuals

    :param chromosomes: Collection of initial chromosomes of the Population.
    :type chromosomes: Collection[chromosome]
    :param eval_function: Function that reduces a chromosome to a fitness.
    :type eval_function: Callable[chromosome] -> float
    :param maximize: If True, fitness will be maximized, otherwise minimized.
        Defaults to True.
    :type maximize: bool
    """
    def __init__(self, chromosomes, eval_function, maximize=True, logger=BaseLogger(), generation=0, intended_size=None):
        self.id = str(uuid4())[:6]
        self.documented_best = None
        self.eval_function = eval_function
        self.generation = generation
        self.individuals = [Individual(chromosome=chromosome) for chromosome in chromosomes]
        self.intended_size = len(chromosomes) if intended_size is None else intended_size
        self.maximize = maximize
        self.logger = logger

    def __copy__(self):
        result = self.__class__(chromosomes=self.chromosomes,
                                eval_function=self.eval_function,
                                generation=self.generation,
                                maximize=self.maximize,
                                intended_size=self.intended_size)
        return result

    def __iter__(self):
        return self.individuals.__iter__()

    def __getitem__(self, i):
        return self.individuals[i]

    def __len__(self):
        return len(self.individuals)

    def __repr__(self):
        return f"<Population object with size {len(self)}>"

    def add(self, *individuals: Individual):
        self.individuals += individuals

    @property
    def current_best(self):
        evaluated_individuals = tuple(filter(lambda x: x.fitness is not None, self.individuals))
        if len(evaluated_individuals) > 0:
            return max(evaluated_individuals, key=lambda x: x.fitness if self.maximize else -x.fitness)

    @property
    def current_worst(self):
        evaluated_individuals = tuple(filter(lambda x: x.fitness is not None, self.individuals))
        if len(evaluated_individuals) > 0:
            return min(evaluated_individuals, key=lambda x: x.fitness if self.maximize else -x.fitness)

    @property
    def chromosomes(self):
        for individual in self.individuals:
            yield individual.chromosome

    @classmethod
    def generate(cls, init_func, eval_func, size=100) -> 'Population':
        chromosomes = [init_func() for _ in range(size)]
        return cls(chromosomes=chromosomes, eval_function=eval_func)

    def evolve(self, evolution: 'Evolution', n: int = 1) -> 'Population':
        """Evolve the population according to an Evolution.

        :param evolution: Evolution to follow
        :type evolution: Evolution
        :param n: Times to apply the evolution. Defaults to 1.
        :type n: int
        :return: Population
        """
        result = copy(self)
        for evo_batch in range(n):
            for step in evolution:
                step.apply(result)
        return result

    def evaluate(self, lazy: bool=False) -> 'Population':
        """Evaluate the individuals in the population.

        This evaluates the fitness of all individuals. If lazy is True, the
        fitness is only evaluated when a fitness value is not yet known. In
        most situations adding an explicit evaluation step is not needed, as
        lazy evaluation is implicitly included in the operations that need it
        (most notably in the survive operation).

        :param lazy: If True, do no re-evaluate the fitness if the fitness is known.
        :type lazy: bool
        :return: self
        """
        for individual in self.individuals:
            individual.evaluate(eval_function=self.eval_function, lazy=lazy)
        self._update_documented_best()
        return self

    def apply(self, func, **kwargs) -> 'Population':
        """Apply the provided function to the population.

        :param func: Function to apply to the population.
        :type func: Callable[Population]
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        return func(self, **kwargs)

    def map(self, func, **kwargs) -> 'Population':
        """Apply the provided function to each individual in the population.

        :param func: Function to apply to the individuals in the population.
        :type func: Callable[Individual] -> Individual
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        self.individuals = [func(individual, **kwargs) for individual in self.individuals]
        return self

    def filter(self, func, **kwargs) -> 'Population':
        """Add a filter step to the Evolution.

        Filters the individuals in the population using the provided function.

        :param func: Function to filter the individuals in the population by.
        :type func: Callable[Individual] -> bool
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        self.individuals = [individual for individual in self.individuals if func(individual, **kwargs)]
        return self

    def survive(self, fraction=None, n=None, luck=False) -> 'Population':
        """Let part of the population survive.

        Remove part of the population. If both fraction and n are specified,
        the minimum resulting population size is taken.

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
        if fraction is None:
            if n is None:
                raise ValueError('everyone survives! must provide either "fraction" and/or "n".')
            resulting_size = n
        elif n is None:
            resulting_size = round(fraction*len(self.individuals))
        else:
            resulting_size = min(round(fraction*len(self.individuals)), n)
        self.evaluate(lazy=True)
        if resulting_size == 0:
            raise RuntimeError('no one survived!')
        if resulting_size > len(self.individuals):
            raise ValueError('everyone survives! must provide "fraction" and/or "n" < population size')
        if luck:
            self.individuals = choices(self.individuals, k=resulting_size,
                                       weights=[individual.fitness for individual in self.individuals])
        else:
            sorted_individuals = sorted(self.individuals, key=lambda x: x.fitness, reverse=self.maximize)
            self.individuals = sorted_individuals[:resulting_size]
        return self

    def breed(self, parent_picker, combiner, population_size=None, **kwargs) -> 'Population':
        """Create new individuals by combining existing individuals.

        :param parent_picker: Function that selects parents.
        :type parent_picker: Callable[list[Individual]] -> tuple[Individual]
        :param combiner: Function that combines chromosomes into a new
            chromosome. Must be able to handle the number of chromosomes
            that the combiner returns.
        :type combiner: Callable[chromosome, ...] -> chromosome
        :param population_size: Intended population size after breeding.
            If None, take the previous intended population size.
            Defaults to None.
        :type population_size: int/None
        :param kwargs: Kwargs to pass to the parent_picker and combiner.
            Arguments are only passed to the functions if they accept them.
        :return: self
        """
        parent_picker = select_arguments(parent_picker)
        combiner = select_arguments(combiner)
        if population_size:
            self.intended_size = population_size
        offspring = offspring_generator(parents=self.individuals,
                                        parent_picker=select_arguments(parent_picker),
                                        combiner=select_arguments(combiner),
                                        **kwargs)
        self.individuals += list(islice(offspring, self.intended_size - len(self.individuals)))
        # TODO: increase generation and individual's ages
        return self

    def mutate(self, func, probability=1.0, **kwargs) -> 'Population':
        """Mutate the chromosome of each individual.

        :param func: Function that accepts a chromosome and returns
            a mutated chromosome.
        :type func: Callable[chromosome, **kwargs] -> chromosome
        :param probability: Probability that the individual mutates.
            The function is only applied in the given fraction of cases.
            Defaults to 1.0.
        :type probability: float
        :param kwargs: Arguments to pass to the mutation function.
        :return: self
        """
        for individual in self.individuals:
            individual.mutate(func, probability=probability, **kwargs)
        return self

    def duplicate(self, n_islands) -> IslandPopulation:
        return IslandPopulation(
            populations=[copy(self) for _ in range(n_islands)],
            maximize=self.maximize
        )
    def log(self, **kwargs) -> 'Population':
        """
        Logs a population. If a Population object was initialized with a logger
        object then you may specify how logging is handled. The base logging
        operation just logs to standard out.

        :return: self
        """
        self.evaluate(lazy=True)
        self.logger.log(population=self, **kwargs)
        return self

    def _update_documented_best(self):
        """Update the documented best"""
        current_best = self.current_best
        if (self.documented_best is None or
                (self.maximize and current_best.fitness > self.documented_best.fitness) or
                (not self.maximize and current_best.fitness < self.documented_best.fitness)):
            self.documented_best = copy(current_best)


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
