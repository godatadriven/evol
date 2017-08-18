from copy import copy

from .population import Population
from .step import EvaluationStep, ApplyStep, MapStep, FilterStep, UpdateStep
from .step import SurviveStep, BreedStep, MutateStep


class Evolution:

    def __init__(self):
        self.chain = []

    def __iter__(self):
        return self.chain.__iter__()

    def evaluate(self, name=None, lazy=False) -> 'Evolution':
        return self._add_step(EvaluationStep(name=name, lazy=lazy))

    def apply(self, func, name=None, **kwargs) -> 'Evolution':
        return self._add_step(ApplyStep(name=name, func=func, **kwargs))

    def map(self, func, name=None, **kwargs) -> 'Evolution':
        return self._add_step(MapStep(name=name, func=func, **kwargs))

    def filter(self, func, name=None, **kwargs) -> 'Evolution':
        return self._add_step(FilterStep(name=name, func=func, **kwargs))

    def update(self, func, name=None, **kwargs) -> 'Evolution':
        return self._add_step(UpdateStep(name=name, func=func, **kwargs))

    def survive(self, fraction=None, n=None, luck=False, name=None) -> 'Evolution':
        return self._add_step(SurviveStep(name=name, fraction=fraction, n=n, luck=luck))

    def breed(self, parent_picker, combiner, population_size=None, name=None, **kwargs) -> 'Evolution':
        return self._add_step(BreedStep(name=name, parent_picker=parent_picker, combiner=combiner,
                                        population_size=population_size, **kwargs))

    def mutate(self, func, name=None, **kwargs) -> 'Evolution':
        return self._add_step(MutateStep(name=name, func=func, **kwargs))

    def evolve(self, population: Population, n: int=1):
        result = copy(population)  # Should this be deepcopy?
        for i in range(n):
            for step in self.chain:
                result = step.apply(result)
        return result

    def _add_step(self, step):
        result = copy(self)
        result.chain.append(step)
        return result

    def __repr__(self):
        result = "<Evolution object with steps>"
        return result + "\n".join([f"  -{step.name}" for step in self.chain])
