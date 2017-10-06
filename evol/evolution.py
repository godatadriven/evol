from copy import copy, deepcopy

from .population import Population
from .step import EvaluationStep, ApplyStep, MapStep, FilterStep, UpdateStep
from .step import SurviveStep, BreedStep, MutateStep, RepeatStep


class Evolution:

    def __init__(self):
        self.chain = []

    def __copy__(self):
        result = Evolution()
        result.chain = copy(self.chain)
        return result

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

    def survive(self, fraction=None, n=None, luck=False, name=None, evaluate=True) -> 'Evolution':
        if evaluate:
            after_evaluate = self.evaluate(lazy=True)
        else:
            after_evaluate = self
        return after_evaluate._add_step(SurviveStep(name=name, fraction=fraction, n=n, luck=luck))

    def breed(self, parent_picker, combiner, population_size=None, name=None, **kwargs) -> 'Evolution':
        return self._add_step(BreedStep(name=name, parent_picker=parent_picker, combiner=combiner,
                                        population_size=population_size, **kwargs))

    def mutate(self, func, name=None, **kwargs) -> 'Evolution':
        return self._add_step(MutateStep(name=name, func=func, **kwargs))

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
