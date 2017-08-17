from copy import copy
from .population import Population
from .step import EvaluationStep

class Evolution:

    def __init__(self):
        self.steps = []

    def __iter__(self):
        return self.steps.__iter__()

    def evaluate(self, name=None) -> 'Evolution':
        if not name:
            name = f"step-{len(self.steps)+1}-evaluate"
        result = copy(self)
        result.steps.append(EvaluationStep(name=name))
        return result

    def evolve(self, population: Population):
        for step in self.chain:
            population = step.apply(population, *step.args, **step.kwargs)

    def __repr__(self):
        result = "<Evolution object with steps>"
        return result + "\n".join([f"  -{step.name} for step in self.steps"])
