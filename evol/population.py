"""
Population objects in `evol` are a collection of chromosomes
at some point in an evolutionary algorithm. You can apply
evolutionary steps by directly calling methods on the population
or by appyling an `evol.Evolution` object.
"""
from itertools import cycle, islice
from typing import Any, Callable, Generator, Iterable, Iterator, Optional, Sequence
from uuid import uuid4

from copy import copy
from random import choices, randint

from evol import Individual
from evol.helpers.utils import select_arguments, offspring_generator
from evol.logger import BaseLogger
from evol.serialization import SimpleSerializer


class Population:
    """Population of Individuals

    :param chromosomes: Iterable of initial chromosomes of the Population.
    :param eval_function: Function that reduces a chromosome to a fitness.
    :param maximize: If True, fitness will be maximized, otherwise minimized.
        Defaults to True.
    :param logger: Logger object for the Population. If None, a new BaseLogger
        is created. Defaults to None.
    :param generation: Generation of the Population. Defaults to 0.
    :param intended_size: Intended size of the Population. The population will
        be replenished to this size by .breed(). Defaults to the number of
        chromosomes provided.
    :param checkpoint_target: Target for the serializer of the Population. If
        a serializer is provided, this target is ignored. Defaults to None.
    :param serializer: Serializer for the Population. If None, a new
        SimpleSerializer is created. Defaults to None.
    """
    def __init__(self,
                 chromosomes: Iterable,
                 eval_function: Callable[..., float],
                 maximize: bool=True,
                 logger=None,
                 generation: int=0,
                 intended_size: Optional[int]=None,
                 checkpoint_target: Optional[str]=None,
                 serializer=None):
        self.id = str(uuid4())[:6]
        self.documented_best = None
        self.eval_function = eval_function
        self.generation = generation
        self.individuals = [Individual(chromosome=chromosome) for chromosome in chromosomes]
        self.intended_size = intended_size or len(self.individuals)
        self.maximize = maximize
        self.logger = logger or BaseLogger()
        self.serializer = serializer or SimpleSerializer(target=checkpoint_target)

    def __copy__(self):
        result = self.__class__(chromosomes=self.chromosomes,
                                eval_function=self.eval_function,
                                maximize=self.maximize,
                                serializer=self.serializer,
                                intended_size=self.intended_size,
                                logger=self.logger,
                                generation=self.generation)
        result.documented_best = self.documented_best
        return result

    def __iter__(self) -> Iterator[Individual]:
        return self.individuals.__iter__()

    def __getitem__(self, i) -> Individual:
        return self.individuals[i]

    def __len__(self):
        return len(self.individuals)

    def __repr__(self):
        return f"<Population with size {len(self)} at {id(self)}>"

    @property
    def current_best(self) -> Individual:
        evaluated_individuals = tuple(filter(lambda x: x.fitness is not None, self.individuals))
        if len(evaluated_individuals) > 0:
            return max(evaluated_individuals, key=lambda x: x.fitness if self.maximize else -x.fitness)

    @property
    def current_worst(self) -> Individual:
        evaluated_individuals = tuple(filter(lambda x: x.fitness is not None, self.individuals))
        if len(evaluated_individuals) > 0:
            return min(evaluated_individuals, key=lambda x: x.fitness if self.maximize else -x.fitness)

    @property
    def chromosomes(self) -> Generator[Any, None, None]:
        for individual in self.individuals:
            yield individual.chromosome

    @classmethod
    def generate(cls,
                 init_function: Callable[[], Any],
                 eval_function: Callable[..., float],
                 size: int=100,
                 **kwargs) -> 'Population':
        """Generate a population from an initialisation function.

        :param init_function: Function that returns a chromosome.
        :param eval_function: Function that reduces a chromosome to a fitness.
        :param size: Number of individuals to generate. Defaults to 100.
        :return: Population
        """
        chromosomes = [init_function() for _ in range(size)]
        return cls(chromosomes=chromosomes, eval_function=eval_function, **kwargs)

    @classmethod
    def load(cls,
             target: str,
             eval_function: Callable[..., float],
             **kwargs) -> 'Population':
        """Load a population from a checkpoint.

        :param target: Path to checkpoint directory or file.
        :param eval_function: Function that reduces a chromosome to a fitness.
        :param kwargs: Any argument the init method accepts.
        :return: Population
        """
        result = cls(chromosomes=[], eval_function=eval_function, **kwargs)
        result.individuals = result.serializer.load(target=target)
        return result

    def checkpoint(self, target: Optional[str]=None, method: str='pickle') -> 'Population':
        """Checkpoint the population.

        :param target: Directory to write checkpoint to. If None, the Serializer default target is taken,
            which can be provided upon initialisation. Defaults to None.
        :param method: One of 'pickle' or 'json'. When 'json', the chromosomes need to be json-serializable.
            Defaults to 'pickle'.
        :return: Population
        """
        self.serializer.checkpoint(individuals=self.individuals, target=target, method=method)
        return self

    @property
    def _individual_weights(self):
        try:
            min_fitness = min(individual.fitness for individual in self)
            max_fitness = max(individual.fitness for individual in self)
        except TypeError:
            raise RuntimeError('Individual weights can not be computed if the individuals are not evaluated.')
        if min_fitness == max_fitness:
            return [1] * len(self)
        elif self.maximize:
            return [(individual.fitness - min_fitness) / (max_fitness - min_fitness) for individual in self]
        else:
            return [1 - (individual.fitness - min_fitness) / (max_fitness - min_fitness) for individual in self]

    def evolve(self, evolution: 'Evolution', n: int=1) -> 'Population':
        """Evolve the population according to an Evolution.

        :param evolution: Evolution to follow
        :param n: Times to apply the evolution. Defaults to 1.
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
        :return: self
        """
        for individual in self.individuals:
            individual.evaluate(eval_function=self.eval_function, lazy=lazy)
        self._update_documented_best()
        return self

    def apply(self, func: Callable[..., 'Population'], **kwargs) -> 'Population':
        """Apply the provided function to the population.

        :param func: A function to apply to the population, which returns the (modified) population.
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        return func(self, **kwargs)

    def map(self, func: Callable[..., Individual], **kwargs) -> 'Population':
        """Apply the provided function to each individual in the population.

        :param func: A function to apply to each individual in the population,
            which when called returns a modified individual.
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        self.individuals = [func(individual, **kwargs) for individual in self.individuals]
        return self

    def filter(self, func: Callable[..., bool], **kwargs) -> 'Population':
        """Add a filter step to the Evolution.

        Filters the individuals in the population using the provided function.

        :param func: Function to filter the individuals in the population by,
            which returns a boolean when called on an individual.
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        self.individuals = [individual for individual in self.individuals if func(individual, **kwargs)]
        return self

    def survive(self, fraction: Optional[float]=None, n: Optional[int]=None, luck: bool=False) -> 'Population':
        """Let part of the population survive.

        Remove part of the population. If both fraction and n are specified,
        the minimum resulting population size is taken.

        :param fraction: Fraction of the original population that survives.
            Defaults to None.
        :param n: Number of individuals of the population that survive.
            Defaults to None.
        :param luck: If True, individuals randomly survive (with replacement!)
            with chances proportional to their fitness. Defaults to False.
        :return: self
        """
        if fraction is None:
            if n is None:
                raise ValueError('everyone survives! must provide either "fraction" and/or "n".')
            resulting_size = n
        elif n is None:
            resulting_size = round(fraction * len(self.individuals))
        else:
            resulting_size = min(round(fraction * len(self.individuals)), n)
        self.evaluate(lazy=True)
        if resulting_size == 0:
            raise RuntimeError('no one survived!')
        if resulting_size > len(self.individuals):
            raise ValueError('everyone survives! must provide "fraction" and/or "n" < population size')
        if luck:
            self.individuals = choices(self.individuals, k=resulting_size, weights=self._individual_weights)
        else:
            sorted_individuals = sorted(self.individuals, key=lambda x: x.fitness, reverse=self.maximize)
            self.individuals = sorted_individuals[:resulting_size]
        return self

    def breed(self,
              parent_picker: Callable[..., Sequence[Individual]],
              combiner: Callable,
              population_size: Optional[int]=None,
              **kwargs) -> 'Population':
        """Create new individuals by combining existing individuals.

        :param parent_picker: Function that selects parents from a collection of individuals.
        :param combiner: Function that combines chromosomes into a new
            chromosome. Must be able to handle the number of chromosomes
            that the combiner returns.
        :param population_size: Intended population size after breeding.
            If None, take the previous intended population size.
            Defaults to None.
        :param kwargs: Kwargs to pass to the parent_picker and combiner.
            Arguments are only passed to the functions if they accept them.
        :return: self
        """
        if population_size:
            self.intended_size = population_size
        offspring = offspring_generator(parents=self.individuals,
                                        parent_picker=select_arguments(parent_picker),
                                        combiner=select_arguments(combiner),
                                        **kwargs)
        self.individuals += list(islice(offspring, self.intended_size - len(self.individuals)))
        return self

    def mutate(self,
               mutate_function: Callable[..., Any],
               probability: float=1.0, **kwargs) -> 'Population':
        """Mutate the chromosome of each individual.

        :param mutate_function: Function that accepts a chromosome and returns
            a mutated chromosome.
        :param probability: Probability that the individual mutates.
            The function is only applied in the given fraction of cases.
            Defaults to 1.0.
        :param kwargs: Arguments to pass to the mutation function.
        :return: self
        """
        for individual in self.individuals:
            individual.mutate(mutate_function, probability=probability, **kwargs)
        return self

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

    def callback(self, callback_function: Callable[['Population'], None],
                 **kwargs) -> 'Population':
        """
        Performs a callback function on the population. Can be used for
        custom logging/checkpointing.
        :param callback_function: Function that accepts the population
        as a first argument.
        :return:
        """
        self.evaluate(lazy=True)
        callback_function(copy(self), **kwargs)
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

    :param chromosomes: Iterable of initial chromosomes of the Population.
    :param eval_function: Function that reduces a chromosome to a fitness.
    :param maximize: If True, fitness will be maximized, otherwise minimized.
        Defaults to True.
    :param contests_per_round: Number of contests each individual takes part
        in for each evaluation round. Defaults to 10.
    :param individuals_per_contest: Number of individuals that take part in
        each contest. The size of the population must be divisible by this
        number. Defaults to 2.
    :param logger: Logger object for the Population. If None, a new BaseLogger
        is created. Defaults to None.
    :param generation: Generation of the Population. Defaults to 0.
    :param intended_size: Intended size of the Population. The population will
        be replenished to this size by .breed(). Defaults to the number of
        chromosomes provided.
    :param checkpoint_target: Target for the serializer of the Population. If
        a serializer is provided, this target is ignored. Defaults to None.
    :param serializer: Serializer for the Population. If None, a new
        SimpleSerializer is created. Defaults to None.
    """
    def __init__(self,
                 chromosomes: Iterable,
                 eval_function: Callable[[Iterable[Any]], Sequence[float]],
                 maximize: bool=True,
                 contests_per_round=10,
                 individuals_per_contest=2,
                 logger=None,
                 generation: int=0,
                 intended_size: Optional[int]=None,
                 checkpoint_target: Optional[int]=None,
                 serializer=None):
        Population.__init__(self, chromosomes=chromosomes, eval_function=eval_function, maximize=maximize,
                            logger=logger, generation=generation, intended_size=intended_size,
                            checkpoint_target=checkpoint_target, serializer=serializer)
        self.contests_per_round = contests_per_round
        self.individuals_per_contest = individuals_per_contest

    def __copy__(self):
        result = self.__class__(chromosomes=self.chromosomes,
                                eval_function=self.eval_function,
                                maximize=self.maximize,
                                contests_per_round=self.contests_per_round,
                                individuals_per_contest=self.individuals_per_contest,
                                serializer=self.serializer,
                                intended_size=self.intended_size,
                                logger=self.logger,
                                generation=self.generation)
        result.documented_best = None
        return result

    def evaluate(self,
                 lazy: bool=False,
                 contests_per_round: Optional[int]=None,
                 individuals_per_contest: Optional[int]=None) -> 'ContestPopulation':
        """Evaluate the individuals in the population.

        This evaluates the fitness of all individuals. For each round of
        evaluation, each individual participates in a given number of
        contests, in which a given number of individuals take part.
        The resulting scores of these contests are summed to form the fitness.
        This means that the score of the individual is influenced by other
        chromosomes in the population.

        Note that in the `ContestPopulation` two settings are passed at
        initialisation which affect how we are evaluating individuals:
        contests_per_round and individuals_per_contest. You may overwrite them
        here if you wish.

        If lazy is True, the fitness is only evaluated when a fitness value
        is not yet known for all individuals.
        In most situations adding an explicit evaluation step is not needed, as
        lazy evaluation is implicitly included in the operations that need it
        (most notably in the survive operation).

        :param lazy: If True, do no re-evaluate the fitness if the fitness is known.
        :param contests_per_round: If set, overwrites the population setting for the
        number of contests there will be every round.
        :param individuals_per_contest: If set, overwrites the population setting for
        number of individuals to have in a contest during the evaluation.
        :return: self
        """
        if contests_per_round is None:
            contests_per_round = self.contests_per_round
        if individuals_per_contest is None:
            individuals_per_contest = self.individuals_per_contest
        if lazy and all(individual.fitness is not None for individual in self):
            return self
        for individual in self.individuals:
            individual.fitness = 0
        for _ in range(contests_per_round):
            offsets = [0] + [randint(0, len(self.individuals) - 1) for _ in range(individuals_per_contest - 1)]
            generators = [islice(cycle(self.individuals), offset, None) for offset in offsets]
            for competitors in islice(zip(*generators), len(self.individuals)):
                scores = self.eval_function(*competitors)
                for competitor, score in zip(competitors, scores):
                    competitor.fitness += score
        return self

    def map(self, func: Callable[..., Individual], **kwargs) -> 'Population':
        """Apply the provided function to each individual in the population.

        Resets the fitness of all individuals.

        :param func: A function to apply to each individual in the population,
            which when called returns a modified individual.
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        Population.map(self, func=func, **kwargs)
        self.reset_fitness()
        return self

    def filter(self, func: Callable[..., bool], **kwargs) -> 'Population':
        """Add a filter step to the Evolution.

        Filters the individuals in the population using the provided function.
        Resets the fitness of all individuals.

        :param func: Function to filter the individuals in the population by,
            which returns a boolean when called on an individual.
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        Population.filter(self, func=func, **kwargs)
        self.reset_fitness()
        return self

    def survive(self,
                fraction: Optional[float]=None,
                n: Optional[int]=None,
                luck: bool=False) -> 'ContestPopulation':
        """Let part of the population survive.

        Remove part of the population. If both fraction and n are specified,
        the minimum resulting population size is taken. Resets the fitness
        of all individuals.

        :param fraction: Fraction of the original population that survives.
            Defaults to None.
        :param n: Number of individuals of the population that survive.
            Defaults to None.
        :param luck: If True, individuals randomly survive (with replacement!)
            with chances proportional to their fitness. Defaults to False.
        :return: self
        """
        Population.survive(self, fraction=fraction, n=n, luck=luck)
        self.reset_fitness()
        return self  # If we return the result of Population.survive PyCharm complains that it is of type 'Population'

    def reset_fitness(self):
        """Reset the fitness of all individuals."""
        for individual in self:
            individual.fitness = None
