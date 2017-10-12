from copy import copy, deepcopy

from .population import Population
from .step import EvaluationStep, ApplyStep, MapStep, FilterStep, UpdateStep
from .step import SurviveStep, BreedStep, MutateStep, RepeatStep


class Evolution:
    """Describes the process a Population goes through when evolving."""

    def __init__(self):
        self.chain = []

    def __copy__(self):
        result = Evolution()
        result.chain = copy(self.chain)
        return result

    def __iter__(self):
        return self.chain.__iter__()

    def evaluate(self, name=None, lazy=False) -> 'Evolution':
        """Add an evaluation step to the Evolution.

        This evaluates the fitness of all individuals. If lazy is True, the
        fitness is only evaluated when a fitness value is not yet known. In
        most situations adding an explicit evaluation step is not needed, as
        lazy evaluation is implicitly included in the steps that need it (most
        notably in the survive step).

        :param name: Name of the evaluation step.
        :type name: str
        :param lazy: If True, do no re-evaluate the fitness if the fitness is known.
        :type lazy: bool
        :return: This Evolution with an additional step.
        :rtype: Evolution
        """
        return self._add_step(EvaluationStep(name=name, lazy=lazy))

    def apply(self, func, name=None, **kwargs) -> 'Evolution':
        """Add an apply step to the Evolution.

        This applies the provided function to the population.

        :param func: Function to apply to the population.
        :type func: Callable[Population]
        :param name: Name of the apply step.
        :type name: str
        :param kwargs: Arguments to pass to the function.
        :return: This Evolution with an additional step.
        :rtype: Evolution
        """
        return self._add_step(ApplyStep(name=name, func=func, **kwargs))

    def map(self, func, name=None, **kwargs) -> 'Evolution':
        """Add a map step to the Evolution.

        This applies the provided function to each individual in the
        population, in place.

        :param func: Function to apply to the individuals in the population.
        :type func: Callable[Individual] -> Individual
        :param name: Name of the map step.
        :type name: str
        :param kwargs: Arguments to pass to the function.
        :return: This Evolution with an additional step.
        :rtype: Evolution
        """
        return self._add_step(MapStep(name=name, func=func, **kwargs))

    def filter(self, func, name=None, **kwargs) -> 'Evolution':
        """Add a filter step to the Evolution.

        This filters the individuals in the population using the provided function.

        :param func: Function to filter the individuals in the population by.
        :type func: Callable[Individual] -> bool
        :param name: Name of the filter step.
        :type name: str
        :param kwargs: Arguments to pass to the function.
        :return: This Evolution with an additional step.
        :rtype: Evolution
        """
        return self._add_step(FilterStep(name=name, func=func, **kwargs))

    def survive(self, fraction=None, n=None, luck=False, name=None, evaluate=True) -> 'Evolution':
        """Add a survive step to the Evolution.

        This filters the individuals in the population according to fitness.

        :param fraction: Fraction of the original population that survives.
            Defaults to None.
        :type fraction: float/None
        :param n: Number of individuals of the population that survive.
            Defaults to None.
        :type n: int/None
        :param luck: If True, individuals randomly survive (with replacement!)
            with chances proportional to their fitness. Defaults to False.
        :type luck: bool
        :param name: Name of the filter step.
        :type name: str
        :return: This Evolution with an additional step.
        :rtype: Evolution
        """
        if evaluate:
            after_evaluate = self.evaluate(lazy=True)
        else:
            after_evaluate = self
        return after_evaluate._add_step(SurviveStep(name=name, fraction=fraction, n=n, luck=luck))

    def breed(self, parent_picker, combiner, population_size=None, name=None, **kwargs) -> 'Evolution':
        """Add a breed step to the Evolution.

        Create new individuals by combining existing individuals.

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
        :param name: Name of the breed step.
        :type name: str
        :param kwargs: Kwargs to pass to the parent_picker and combiner.
            Arguments are only passed to the functions if they accept them.
        :return: self
        """
        return self._add_step(BreedStep(name=name, parent_picker=parent_picker, combiner=combiner,
                                        population_size=population_size, **kwargs))

    def mutate(self, func, probability=1.0, name=None, **kwargs) -> 'Evolution':
        """Add a mutate step to the Evolution.

        This mutates the chromosome of each individual.

        :param func: Function that accepts a chromosome and returns
            a mutated chromosome.
        :type func: Callable[chromosome, **kwargs] -> chromosome
        :param probability: Probability that the individual mutates.
            The function is only applied in the given fraction of cases.
            Defaults to 1.0.
        :type probability: float
        :param name: Name of the mutate step.
        :type name: str
        :param kwargs: Kwargs to pass to the parent_picker and combiner.
            Arguments are only passed to the functions if they accept them.
        :return: self
        """
        return self._add_step(MutateStep(name=name, probability=probability, func=func, **kwargs))

    def evolve(self, population: Population, n: int=1, inplace=True) -> 'Population':
        if inplace:
            result = population
        else:
            result = deepcopy(population)  # TODO: write a proper Population.__copy__
        for i in range(n):
            for step in self.chain:
                result = step.apply(result)
        return result

    def repeat(self, evolution: 'Evolution', n:int = 1, name=None) -> 'Evolution':
        return self._add_step(RepeatStep(name=name, evolution=evolution, n=n))

    def _add_step(self, step):
        result = copy(self)
        result.chain.append(step)
        return result

    def __repr__(self):
        result = "<Evolution object with steps>\n"
        return result + "\n".join([f"  -{str(step)}" for step in self.chain])
