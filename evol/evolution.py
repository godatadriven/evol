"""
Evolution objects in `evol` are objects that describe how the
evolutionary algorithm will change members of a population.
Evolution objects contain the same methods as population objects
but because an evolution is separate from a population you can
play around with them more easily.
"""

from copy import copy
from typing import Any, Callable, Iterator, List, Optional, Sequence

from evol import Individual
from .step import CheckpointStep, CallbackStep, EvolutionStep
from .step import EvaluationStep, MapStep, FilterStep
from .step import SurviveStep, BreedStep, MutateStep, RepeatStep


class Evolution:
    """Describes the process a Population goes through when evolving."""

    def __init__(self):
        self.chain: List[EvolutionStep] = []

    def __copy__(self) -> 'Evolution':
        result = Evolution()
        result.chain = copy(self.chain)
        return result

    def __iter__(self) -> Iterator[EvolutionStep]:
        return self.chain.__iter__()

    def __repr__(self) -> str:
        result = 'Evolution('
        for step in self:
            result += '\n  ' + repr(step).replace('\n', '\n  ')
        result += ')'
        return result.strip('\n')

    def evaluate(self, lazy: bool = False, name: Optional[str] = None) -> 'Evolution':
        """Add an evaluation step to the Evolution.

        This evaluates the fitness of all individuals. If lazy is True, the
        fitness is only evaluated when a fitness value is not yet known. In
        most situations adding an explicit evaluation step is not needed, as
        lazy evaluation is implicitly included in the steps that need it (most
        notably in the survive step).

        :param lazy: If True, do no re-evaluate the fitness if the fitness is known.
        :param name: Name of the evaluation step.
        :return: This Evolution with an additional step.
        """
        return self._add_step(EvaluationStep(name=name, lazy=lazy))

    def checkpoint(self,
                   target: Optional[str] = None,
                   method: str = 'pickle',
                   name: Optional[str] = None,
                   every: int = 1) -> 'Evolution':
        """Add a checkpoint step to the Evolution.

        :param target: Directory to write checkpoint to. If None, the Serializer default target is taken,
            which can be provided upon initialisation. Defaults to None.
        :param method: One of 'pickle' or 'json'. When 'json', the chromosomes need to be json-serializable.
            Defaults to 'pickle'.
        :param name: Name of the map step.
        :param every: Checkpoint once every 'every' iterations. Defaults to 1.
        """
        return self._add_step(CheckpointStep(name=name, target=target, method=method, every=every))

    def map(self, func: Callable[..., Individual], name: Optional[str] = None, **kwargs) -> 'Evolution':
        """Add a map step to the Evolution.

        This applies the provided function to each individual in the
        population, in place.

        :param func: Function to apply to the individuals in the population.
        :param name: Name of the map step.
        :param kwargs: Arguments to pass to the function.
        :return: This Evolution with an additional step.
        """
        return self._add_step(MapStep(name=name, func=func, **kwargs))

    def filter(self, func: Callable[..., bool], name: Optional[str] = None, **kwargs) -> 'Evolution':
        """Add a filter step to the Evolution.

        This filters the individuals in the population using the provided function.

        :param func: Function to filter the individuals in the population by.
        :param name: Name of the filter step.
        :param kwargs: Arguments to pass to the function.
        :return: This Evolution with an additional step.
        """
        return self._add_step(FilterStep(name=name, func=func, **kwargs))

    def survive(self,
                fraction: Optional[float] = None,
                n: Optional[int] = None,
                luck: bool = False,
                name: Optional[str] = None,
                evaluate: bool = True) -> 'Evolution':
        """Add a survive step to the Evolution.

        This filters the individuals in the population according to fitness.

        :param fraction: Fraction of the original population that survives.
            Defaults to None.
        :param n: Number of individuals of the population that survive.
            Defaults to None.
        :param luck: If True, individuals randomly survive (with replacement!)
            with chances proportional to their fitness. Defaults to False.
        :param name: Name of the filter step.
        :param evaluate: If True, add a lazy evaluate step before the survive step.
            Defaults to True.
        :return: This Evolution with an additional step.
        """
        if evaluate:
            after_evaluate = self.evaluate(lazy=True)
        else:
            after_evaluate = self
        return after_evaluate._add_step(SurviveStep(name=name, fraction=fraction, n=n, luck=luck))

    def breed(self,
              parent_picker: Callable[..., Sequence[Individual]],
              combiner: Callable,
              population_size: Optional[int] = None,
              name: Optional[str] = None,
              **kwargs) -> 'Evolution':
        """Add a breed step to the Evolution.

        Create new individuals by combining existing individuals.

        :param parent_picker: Function that selects parents.
        :param combiner: Function that combines chromosomes into a new
            chromosome. Must be able to handle the number of chromosomes
            that the combiner returns.
        :param population_size: Intended population size after breeding.
            If None, take the previous intended population size.
            Defaults to None.
        :param name: Name of the breed step.
        :param kwargs: Kwargs to pass to the parent_picker and combiner.
            Arguments are only passed to the functions if they accept them.
        :return: self
        """
        return self._add_step(BreedStep(name=name, parent_picker=parent_picker, combiner=combiner,
                                        population_size=population_size, **kwargs))

    def mutate(self,
               mutate_function: Callable[..., Any],
               probability: float = 1.0,
               elitist: bool = False,
               name: Optional[str] = None,
               **kwargs) -> 'Evolution':
        """Add a mutate step to the Evolution.

        This mutates the chromosome of each individual.

        :param mutate_function: Function that accepts a chromosome and returns
            a mutated chromosome.
        :param probability: Probability that the individual mutates.
            The function is only applied in the given fraction of cases.
            Defaults to 1.0.
        :param elitist: If True, do not mutate the current best individual(s).
            Note that this only applies to evaluated individuals. Any unevaluated
            individual will be treated as normal.
            Defaults to False.
        :param name: Name of the mutate step.
        :param kwargs: Kwargs to pass to the parent_picker and combiner.
            Arguments are only passed to the functions if they accept them.
        :return: self
        """
        return self._add_step(MutateStep(name=name, probability=probability, elitist=elitist,
                                         mutate_function=mutate_function, **kwargs))

    def repeat(self, evolution: 'Evolution', n: int = 1, name: Optional[str] = None,
               grouping_function: Optional[Callable] = None, **kwargs) -> 'Evolution':
        """Add an evolution as a step to this evolution.

        This will add a step to the evolution that repeats another evolution
        several times. Optionally this step can be performed in groups.

        Note: if your population uses multiple concurrent workers and you use grouping,
        any callbacks inside the evolution you apply here may not have the desired effect.

        :param evolution: Evolution to apply.
        :param n: Number of times to perform the evolution. Defaults to 1.
        :param name: Name of the repeat step.
        :param grouping_function: Optional function to use for grouping the population.
            You can find built-in grouping functions in evol.helpers.groups.
        :param kwargs: Kwargs to pass to the grouping function, for example n_groups.
        :return: self
        """
        return self._add_step(RepeatStep(name=name, evolution=evolution, n=n,
                                         grouping_function=grouping_function, **kwargs))

    def callback(self, callback_function: Callable[..., Any],
                 every: int = 1, name: Optional[str] = None, **kwargs) -> 'Evolution':
        """Call a function as a step in this evolution.

        This will call the provided function with the population as argument.

        Note that you can raise evol.exceptions.StopEvolution from within the
        callback to stop further evolution.

        :param callback_function: Function to call.
        :param every: Only call the function once per `every` iterations.
            Defaults to 1; every iteration.
        :param name: Name of the callback step.
        :return: self
        """
        return self._add_step(CallbackStep(name=name, every=every, callback_function=callback_function, **kwargs))

    def _add_step(self, step: EvolutionStep) -> 'Evolution':
        result = copy(self)
        result.chain.append(step)
        return result
