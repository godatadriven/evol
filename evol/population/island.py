from copy import deepcopy
from typing import List

from evol import Individual
from .base import PopulationBase


class IslandPopulation(PopulationBase):
    """Population which is split up into multiple isolated groups."""
    def __init__(self, populations: 'List[PopulationBase]', generation=0, maximize=True):
        if len(populations) == 0:
            raise ValueError('An IslandPopulation must have at least one island.')
        self.generation = generation
        self.populations = populations
        self.maximize = maximize

    def __iter__(self):
        for population in self.populations:
            for individual in population:
                yield individual

    def __len__(self):
        return sum(len(population) for population in self.populations)

    def add(self, *individuals: Individual):
        for population in self.populations:
            population.add(*individuals)

    def apply(self, func, **kwargs) -> 'IslandPopulation':
        """Apply the provided function to the population.

        :param func: Function to apply to the population.
        :type func: Callable[Population]
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        return func(self, **kwargs)

    def evolve(self, evolution: 'Evolution', n: int = 1) -> 'IslandPopulation':
        """Evolve the population according to an Evolution.

        :param evolution: Evolution to follow
        :type evolution: Evolution
        :param n: Times to apply the evolution. Defaults to 1.
        :type n: int
        :return: Population
        """
        result = deepcopy(self)
        for evo_batch in range(n):
            for step in evolution:
                step.apply(result)
        return result

    def evaluate(self, lazy: bool=False) -> 'IslandPopulation':
        """Evaluate the individuals in all populations.

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
        for population in self.populations:
            population.evaluate(lazy=lazy)
        return self

    def map(self, func, **kwargs) -> 'IslandPopulation':
        """Apply the provided function to each individual in each population.

        :param func: Function to apply to the individuals in each population.
        :type func: Callable[Individual] -> Individual
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        for population in self.populations:
            population.map(func=func, **kwargs)
        return self

    def filter(self, func, **kwargs) -> 'IslandPopulation':
        """Filter the individuals of each population.

        Filters the individuals in the population using the provided function.

        :param func: Function to filter the individuals in the population by.
        :type func: Callable[Individual] -> bool
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        for population in self.populations:
            population.filter(func=func, **kwargs)
        return self

    def survive(self, fraction=None, n=None, luck=False) -> 'IslandPopulation':
        """Let part of each population survive.

        Remove part of the population. If both fraction and n are specified,
        the minimum resulting population size is taken.

        :param fraction: Fraction of each original population that survives.
            Defaults to None.
        :type fraction: float/None
        :param n: Number of individuals of each population that survive.
            Defaults to None.
        :type n: int/None
        :param luck: If True, individuals randomly survive (with replacement!)
            with chances proportional to their fitness. Defaults to False.
        :type luck: bool
        :return: self
        """
        for population in self.populations:
            population.survive(fraction=fraction, n=n, luck=luck)
        return self

    def breed(self, parent_picker, combiner, population_size=None, **kwargs) -> 'IslandPopulation':
        """Create new individuals in each population by combining existing individuals.

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
        for population in self.populations:
            population.breed(parent_picker=parent_picker, combiner=combiner,
                             population_size=population_size, **kwargs)
        return self

    def mutate(self, func, probability=1.0, **kwargs) -> 'IslandPopulation':
        """Mutate the chromosome of each individual in each population.

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
        for population in self.populations:
            population.mutate(func, probability=probability, **kwargs)
        return self

    def duplicate(self, n_islands) -> 'IslandPopulation':
        return IslandPopulation(
            populations=[deepcopy(self) for _ in range(n_islands)],
            maximize=self.maximize
        )

    def join(self) -> 'PopulationBase':
        result = self.populations[0]
        for pop in self.populations[1:]:
            for individual in pop:
                result.add(individual)
        return result
