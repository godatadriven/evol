from abc import ABCMeta, abstractmethod
from typing import Callable, Optional, TYPE_CHECKING

from evol.population import BasePopulation

if TYPE_CHECKING:
    from evol.evolution import Evolution


class EvolutionStep(metaclass=ABCMeta):

    def __init__(self, name: Optional[str], **kwargs):
        self.name = name
        self.kwargs = kwargs

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name or ''})"

    @abstractmethod
    def apply(self, population: BasePopulation) -> BasePopulation:
        pass


class EvaluationStep(EvolutionStep):

    def apply(self, population: BasePopulation) -> BasePopulation:
        return population.evaluate(**self.kwargs)


class CheckpointStep(EvolutionStep):

    def __init__(self, name, every=1, **kwargs):
        EvolutionStep.__init__(self, name, **kwargs)
        self.count = 0
        self.every = every

    def apply(self, population: BasePopulation) -> BasePopulation:
        self.count += 1
        if self.count >= self.every:
            self.count = 0
            return population.checkpoint(**self.kwargs)
        return population


class MapStep(EvolutionStep):

    def apply(self, population: BasePopulation) -> BasePopulation:
        return population.map(**self.kwargs)


class FilterStep(EvolutionStep):

    def apply(self, population: BasePopulation) -> BasePopulation:
        return population.filter(**self.kwargs)


class SurviveStep(EvolutionStep):

    def apply(self, population: BasePopulation) -> BasePopulation:
        return population.survive(**self.kwargs)


class BreedStep(EvolutionStep):

    def apply(self, population: BasePopulation) -> BasePopulation:
        return population.breed(**self.kwargs)


class MutateStep(EvolutionStep):

    def apply(self, population: BasePopulation) -> BasePopulation:
        return population.mutate(**self.kwargs)


class RepeatStep(EvolutionStep):

    def __init__(self, name: str, evolution: 'Evolution', n: int,
                 grouping_function: Optional[Callable] = None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.evolution = evolution
        self.n = n
        self.grouping_function = grouping_function

    def apply(self, population: BasePopulation) -> BasePopulation:
        if self.grouping_function is None:
            if len(self.kwargs) > 0:
                raise ValueError(f'Unexpected argument(s) for non-grouped repeat step: {self.kwargs}')
            return population.evolve(evolution=self.evolution, n=self.n)
        else:
            return self._apply_grouped(population=population)

    def _apply_grouped(self, population: BasePopulation) -> BasePopulation:
        groups = population.group(grouping_function=self.grouping_function, **self.kwargs)
        if population.pool:
            results = population.pool.map(lambda group: group.evolve(evolution=self.evolution, n=self.n), groups)
        else:
            results = [group.evolve(evolution=self.evolution, n=self.n) for group in groups]
        return population.combine(*results, intended_size=population.intended_size, pool=population.pool)

    def __repr__(self):
        result = f"{self.__class__.__name__}({self.name or ''}) with evolution ({self.n}x):\n  "
        result += repr(self.evolution).replace('\n', '\n  ')
        return result


class CallbackStep(EvolutionStep):
    def __init__(self, name, every: int = 1, **kwargs):
        EvolutionStep.__init__(self, name, **kwargs)
        self.count = 0
        self.every = every

    def apply(self, population: BasePopulation) -> BasePopulation:
        self.count += 1
        if self.count >= self.every:
            self.count = 0
            return population.callback(**self.kwargs)
        return population
