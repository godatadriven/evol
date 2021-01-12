"""
Population objects in `evol` are a collection of chromosomes
at some point in an evolutionary algorithm. You can apply
evolutionary steps by directly calling methods on the population
or by applying an `evol.Evolution` object.
"""
from abc import ABCMeta, abstractmethod
from copy import copy
from itertools import cycle, islice
from math import ceil
from random import choices, randint
from typing import Any, Callable, Generator, Iterable, Iterator, List, Optional, Sequence, TYPE_CHECKING
from uuid import uuid4

from multiprocess.pool import Pool

from evol import Individual
from evol.conditions import Condition
from evol.exceptions import StopEvolution
from evol.helpers.groups import group_random
from evol.utils import offspring_generator, select_arguments
from evol.serialization import SimpleSerializer

if TYPE_CHECKING:
    from .evolution import Evolution


class BasePopulation(metaclass=ABCMeta):

    def __init__(self,
                 chromosomes: Iterable[Any],
                 eval_function: Callable,
                 checkpoint_target: Optional[str] = None,
                 concurrent_workers: Optional[int] = 1,
                 maximize: bool = True,
                 generation: int = 0,
                 intended_size: Optional[int] = None,
                 serializer=None):
        self.concurrent_workers = concurrent_workers
        self.documented_best = None
        self.eval_function = eval_function
        self.generation = generation
        self.id = str(uuid4())[:6]
        self.individuals = [Individual(chromosome=chromosome) for chromosome in chromosomes]
        self.intended_size = intended_size or len(self.individuals)
        self.maximize = maximize
        self.serializer = serializer or SimpleSerializer(target=checkpoint_target)
        self.pool = None if concurrent_workers == 1 else Pool(concurrent_workers)

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

    @property
    def is_evaluated(self) -> bool:
        return all(individual.fitness is not None for individual in self)

    @classmethod
    def generate(cls,
                 init_function: Callable[[], Any],
                 eval_function: Callable[..., float],
                 size: int = 100,
                 **kwargs) -> 'BasePopulation':
        """Generate a population from an initialisation function.

        :param init_function: Function that returns a chromosome.
        :param eval_function: Function that reduces a chromosome to a fitness.
        :param size: Number of individuals to generate. Defaults to 100.
        :return: BasePopulation
        """
        chromosomes = [init_function() for _ in range(size)]
        return cls(chromosomes=chromosomes, eval_function=eval_function, **kwargs)

    @classmethod
    def load(cls,
             target: str,
             eval_function: Callable[..., float],
             **kwargs) -> 'BasePopulation':
        """Load a population from a checkpoint.

        :param target: Path to checkpoint directory or file.
        :param eval_function: Function that reduces a chromosome to a fitness.
        :param kwargs: Any argument the init method accepts.
        :return: Population
        """
        result = cls(chromosomes=[], eval_function=eval_function, **kwargs)
        result.individuals = result.serializer.load(target=target)
        return result

    def checkpoint(self, target: Optional[str] = None, method: str = 'pickle') -> 'BasePopulation':
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

    def evolve(self, evolution: 'Evolution', n: int = 1) -> 'BasePopulation':  # noqa: F821
        """Evolve the population according to an Evolution.

        :param evolution: Evolution to follow
        :param n: Times to apply the evolution. Defaults to 1.
        :return: Population
        """
        result = copy(self)
        try:
            for _ in range(n):
                Condition.check(result)
                for step in evolution:
                    result = step.apply(result)
        except StopEvolution:
            pass
        return result

    @abstractmethod
    def evaluate(self, lazy: bool = False) -> 'BasePopulation':
        pass

    def breed(self,
              parent_picker: Callable[..., Sequence[Individual]],
              combiner: Callable,
              population_size: Optional[int] = None,
              **kwargs) -> 'BasePopulation':
        """Create new individuals by combining existing individuals.

        This increments the generation of the Population.

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
        self.generation += 1
        return self

    def mutate(self,
               mutate_function: Callable[..., Any],
               probability: float = 1.0,
               elitist: bool = False, **kwargs) -> 'BasePopulation':
        """Mutate the chromosome of each individual.

        :param mutate_function: Function that accepts a chromosome and returns
            a mutated chromosome.
        :param probability: Probability that the individual mutates.
            The function is only applied in the given fraction of cases.
            Defaults to 1.0.
        :param elitist: If True, do not mutate the current best individual(s).
            Note that this only applies to evaluated individuals. Any unevaluated
            individual will be treated as normal.
            Defaults to False.
        :param kwargs: Arguments to pass to the mutation function.
        :return: self
        """
        elite_fitness = self.current_best if elitist else None
        for individual in self.individuals:
            if elite_fitness is None or individual.fitness != elite_fitness:
                individual.mutate(mutate_function, probability=probability, **kwargs)
        return self

    def map(self, func: Callable[..., Individual], **kwargs) -> 'BasePopulation':
        """Apply the provided function to each individual in the population.

        :param func: A function to apply to each individual in the population,
            which when called returns a modified individual.
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        self.individuals = [func(individual, **kwargs) for individual in self.individuals]
        return self

    def filter(self, func: Callable[..., bool], **kwargs) -> 'BasePopulation':
        """Add a filter step to the Evolution.

        Filters the individuals in the population using the provided function.

        :param func: Function to filter the individuals in the population by,
            which returns a boolean when called on an individual.
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        self.individuals = [individual for individual in self.individuals if func(individual, **kwargs)]
        return self

    def survive(self, fraction: Optional[float] = None,
                n: Optional[int] = None, luck: bool = False) -> 'BasePopulation':
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
            raise RuntimeError(f'No individual out of {len(self.individuals)} survived!')
        if resulting_size > len(self.individuals):
            raise ValueError(f'everyone survives in population {self.id}: '
                             f'{resulting_size} out of {len(self.individuals)} must survive.')
        if luck:
            self.individuals = choices(self.individuals, k=resulting_size, weights=self._individual_weights)
        else:
            sorted_individuals = sorted(self.individuals, key=lambda x: x.fitness, reverse=self.maximize)
            self.individuals = sorted_individuals[:resulting_size]
        return self

    def callback(self, callback_function: Callable[..., None],
                 **kwargs) -> 'BasePopulation':
        """
        Performs a callback function on the population. Can be used for
        custom logging/checkpointing.
        :param callback_function: Function that accepts the population
        as a first argument.
        :return:
        """
        self.evaluate(lazy=True)
        callback_function(self, **kwargs)
        return self

    def group(self, grouping_function: Callable[..., List[List[int]]] = group_random,
              **kwargs) -> List['BasePopulation']:
        """
        Group a population into islands.

        Divides the population into multiple island populations, each of which
        contains a subset of the original population. An individual from the
        original population may end up in multiple (>= 0) island populations.

        :param grouping_function: Function that allocates individuals to the
            island populations. It will be passed a list of individuals plus
            the kwargs passed to this method, and must return a list of lists
            of integers, each sub-list representing an island and the integers
            representing the index of an individual in the list. Each island
            must contain at least one individual, and individual may be copied
            to multiple islands.
        :param kwargs: Additional keyworded arguments are passed to the
            grouping function.
        :return: List[Population]
        """
        group_indexes = grouping_function(self.individuals, **kwargs)
        if len(group_indexes) == 0:
            raise ValueError('Group yielded zero islands.')
        result = [self._subset(index=index, subset_id=str(i)) for i, index in enumerate(group_indexes)]
        return result

    @classmethod
    def combine(cls, *populations: 'BasePopulation',
                intended_size: Optional[int] = None,
                pool: Optional[Pool] = None) -> 'BasePopulation':
        """
        Combine multiple island populations into a single population.

        The resulting population is reduced to its intended size.

        :param populations: Populations to combine.
        :param intended_size: Intended size of the resulting population.
            Defaults to the sum of the intended sizes of the islands.
        :param pool: Optionally provide a multiprocessing pool to be
            used by the population.
        :return: Population
        """
        if len(populations) == 0:
            raise ValueError('Cannot combine zero islands into one.')
        result = copy(populations[0])
        for pop in populations[1:]:
            result.individuals += pop.individuals
        result.intended_size = intended_size or sum([pop.intended_size for pop in populations])
        result.pool = pool
        result.id = result.id.split('-')[0]
        return result.survive(n=result.intended_size)

    def _subset(self, index: List[int], subset_id: str) -> 'BasePopulation':
        """Create a new population that is a subset of this population."""
        if len(index) == 0:
            raise ValueError('Grouping yielded an empty island.')
        result = copy(self)
        result.individuals = [result.individuals[i] for i in index]
        result.intended_size = len(result.individuals)
        result.pool = None  # Subsets shouldn't parallelize anything
        result.id += '-' + subset_id
        return result

    def _update_documented_best(self):
        """Update the documented best"""
        current_best = self.current_best
        if (self.documented_best is None or
                (self.maximize and current_best.fitness > self.documented_best.fitness) or
                (not self.maximize and current_best.fitness < self.documented_best.fitness)):
            self.documented_best = copy(current_best)


class Population(BasePopulation):
    """Population of Individuals

    :param chromosomes: Iterable of initial chromosomes of the Population.
    :param eval_function: Function that reduces a chromosome to a fitness.
    :param maximize: If True, fitness will be maximized, otherwise minimized.
        Defaults to True.
    :param generation: Generation of the Population. This is incremented after
        each breed call. Defaults to 0.
    :param intended_size: Intended size of the Population. The population will
        be replenished to this size by .breed(). Defaults to the number of
        chromosomes provided.
    :param checkpoint_target: Target for the serializer of the Population. If
        a serializer is provided, this target is ignored. Defaults to None.
    :param serializer: Serializer for the Population. If None, a new
        SimpleSerializer is created. Defaults to None.
    :param concurrent_workers: If > 1, evaluate individuals in {concurrent_workers}
        separate processes. If None, concurrent_workers is set to n_cpus. Defaults to 1.
    """

    def __init__(self,
                 chromosomes: Iterable,
                 eval_function: Callable[..., float],
                 maximize: bool = True,
                 generation: int = 0,
                 intended_size: Optional[int] = None,
                 checkpoint_target: Optional[str] = None,
                 serializer=None,
                 concurrent_workers: Optional[int] = 1):
        super().__init__(chromosomes=chromosomes,
                         eval_function=eval_function,
                         checkpoint_target=checkpoint_target,
                         concurrent_workers=concurrent_workers,
                         maximize=maximize,
                         generation=generation,
                         intended_size=intended_size,
                         serializer=serializer)

    def __copy__(self):
        result = self.__class__(chromosomes=[],
                                eval_function=self.eval_function,
                                maximize=self.maximize,
                                serializer=self.serializer,
                                intended_size=self.intended_size,
                                generation=self.generation,
                                concurrent_workers=1)  # Prevent new pool from being made
        result.individuals = [copy(individual) for individual in self.individuals]
        result.concurrent_workers = self.concurrent_workers
        result.pool = self.pool
        result.documented_best = self.documented_best
        result.id = self.id
        return result

    def evaluate(self, lazy: bool = False) -> 'Population':
        """Evaluate the individuals in the population.

        This evaluates the fitness of all individuals. If lazy is True, the
        fitness is only evaluated when a fitness value is not yet known. In
        most situations adding an explicit evaluation step is not needed, as
        lazy evaluation is implicitly included in the operations that need it
        (most notably in the survive operation).

        :param lazy: If True, do no re-evaluate the fitness if the fitness is known.
        :return: self
        """
        if self.pool:
            f = self.eval_function  # We cannot refer to self in the map
            scores = self.pool.map(lambda i: i.fitness if (i.fitness and lazy) else f(i.chromosome), self.individuals)
            for individual, fitness in zip(self.individuals, scores):
                individual.fitness = fitness
        else:
            for individual in self.individuals:
                individual.evaluate(eval_function=self.eval_function, lazy=lazy)
        self._update_documented_best()
        return self


class Contest:
    """A single contest among a group of competitors.

    This is encapsulated in an object so that scores for many sets of
    competitors can be evaluated concurrently without resorting to a
    dict or some similar madness to correlate score vectors with an
    ever-widening matrix of contests and competitors.

    :param competitors: Iterable of Individuals in this Contest.
    """

    def __init__(self, competitors: Iterable[Individual]):
        self.competitors = list(competitors)

    def assign_scores(self, scores: Sequence[float]) -> None:
        for competitor, score in zip(self.competitors, scores):
            competitor.fitness += score

    @property
    def competitor_chromosomes(self):
        return [competitor.chromosome for competitor in self.competitors]

    @classmethod
    def generate(cls, individuals: Sequence[Individual],
                 individuals_per_contest: int, contests_per_round: int) -> List['Contest']:
        """Generate contests for a round of evaluations.

        :param individuals: A sequence of competing Individuals.
        :param individuals_per_contest: Number of Individuals participating in each Contest.
        :param contests_per_round: Minimum number of contests each individual
            takes part in for each evaluation round. The actual number of contests
            per round is a multiple of individuals_per_contest.
        :return: List of Contests
        """
        contests = []
        n_rounds = ceil(contests_per_round / individuals_per_contest)
        for _ in range(n_rounds):
            offsets = [0] + [randint(0, len(individuals) - 1) for _ in range(individuals_per_contest - 1)]
            generators = [islice(cycle(individuals), offset, None) for offset in offsets]
            for competitors in islice(zip(*generators), len(individuals)):
                contests.append(Contest(competitors))
        return contests


class ContestPopulation(BasePopulation):
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
    :param individuals_per_contest: Number of individuals that take part in
        each contest. The size of the population must be divisible by this
        number. Defaults to 2.
    :param contests_per_round: Minimum number of contests each individual
        takes part in for each evaluation round. The actual number of contests
        per round is a multiple of individuals_per_contest. Defaults to 10.
    :param generation: Generation of the Population. This is incremented after
        echo survive call. Defaults to 0.
    :param intended_size: Intended size of the Population. The population will
        be replenished to this size by .breed(). Defaults to the number of
        chromosomes provided.
    :param checkpoint_target: Target for the serializer of the Population. If
        a serializer is provided, this target is ignored. Defaults to None.
    :param serializer: Serializer for the Population. If None, a new
        SimpleSerializer is created. Defaults to None.
    :param concurrent_workers: If > 1, evaluate individuals in {concurrent_workers}
        separate processes. If None, concurrent_workers is set to n_cpus. Defaults to 1.
    """
    eval_function: Callable[..., Sequence[float]]  # This population expects a different eval signature

    def __init__(self,
                 chromosomes: Iterable,
                 eval_function: Callable[..., Sequence[float]],
                 maximize: bool = True,
                 individuals_per_contest=2,
                 contests_per_round=10,
                 generation: int = 0,
                 intended_size: Optional[int] = None,
                 checkpoint_target: Optional[int] = None,
                 serializer=None,
                 concurrent_workers: Optional[int] = 1):
        super().__init__(chromosomes=chromosomes,
                         eval_function=eval_function,
                         maximize=maximize,
                         generation=generation,
                         intended_size=intended_size,
                         checkpoint_target=checkpoint_target,
                         serializer=serializer,
                         concurrent_workers=concurrent_workers)
        self.contests_per_round = contests_per_round
        self.individuals_per_contest = individuals_per_contest

    def __copy__(self):
        result = self.__class__(chromosomes=[],
                                eval_function=self.eval_function,
                                maximize=self.maximize,
                                contests_per_round=self.contests_per_round,
                                individuals_per_contest=self.individuals_per_contest,
                                serializer=self.serializer,
                                intended_size=self.intended_size,
                                generation=self.generation,
                                concurrent_workers=1)
        result.individuals = [copy(individual) for individual in self.individuals]
        result.pool = self.pool
        result.concurrent_workers = self.concurrent_workers
        result.documented_best = None
        result.id = self.id
        return result

    def evaluate(self,
                 lazy: bool = False,
                 contests_per_round: Optional[int] = None,
                 individuals_per_contest: Optional[int] = None) -> 'ContestPopulation':
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
        contests = Contest.generate(individuals=self.individuals, individuals_per_contest=individuals_per_contest,
                                    contests_per_round=contests_per_round)
        if self.pool is None:
            for contest in contests:
                contest.assign_scores(self.eval_function(*contest.competitor_chromosomes))
        else:
            f = self.eval_function  # We cannot refer to self in the map
            results = self.pool.map(lambda c: f(*c.competitor_chromosomes), contests)
            for result, contest in zip(results, contests):
                contest.assign_scores(result)
        return self

    def map(self, func: Callable[..., Individual], **kwargs) -> 'ContestPopulation':
        """Apply the provided function to each individual in the population.

        Resets the fitness of all individuals.

        :param func: A function to apply to each individual in the population,
            which when called returns a modified individual.
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        BasePopulation.map(self, func=func, **kwargs)
        self.reset_fitness()
        return self

    def filter(self, func: Callable[..., bool], **kwargs) -> 'ContestPopulation':
        """Add a filter step to the Evolution.

        Filters the individuals in the population using the provided function.
        Resets the fitness of all individuals.

        :param func: Function to filter the individuals in the population by,
            which returns a boolean when called on an individual.
        :param kwargs: Arguments to pass to the function.
        :return: self
        """
        BasePopulation.filter(self, func=func, **kwargs)
        self.reset_fitness()
        return self

    def survive(self,
                fraction: Optional[float] = None,
                n: Optional[int] = None,
                luck: bool = False) -> 'ContestPopulation':
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
        BasePopulation.survive(self, fraction=fraction, n=n, luck=luck)
        self.reset_fitness()
        return self

    def reset_fitness(self):
        """Reset the fitness of all individuals."""
        for individual in self:
            individual.fitness = None
