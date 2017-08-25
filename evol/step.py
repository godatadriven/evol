from .population import Population


class EvolutionStep:

    def __init__(self, name, **kwargs):
        self.name = name
        self.kwargs = kwargs


class EvaluationStep(EvolutionStep):

    def apply(self, population) -> Population:
        return population.evaluate(**self.kwargs)


class ApplyStep(EvolutionStep):

    def apply(self, population) -> Population:
        return population.apply(**self.kwargs)


class MapStep(EvolutionStep):

    def apply(self, population) -> Population:
        return population.map(**self.kwargs)


class FilterStep(EvolutionStep):

    def apply(self, population) -> Population:
        return population.filter(**self.kwargs)


class UpdateStep(EvolutionStep):

    def apply(self, population) -> Population:
        return population.update(**self.kwargs)


class SurviveStep(EvolutionStep):

    def apply(self, population) -> Population:
        return population.survive(**self.kwargs)


class BreedStep(EvolutionStep):

    def apply(self, population) -> Population:
        return population.breed(**self.kwargs)


class MutateStep(EvolutionStep):

    def apply(self, population) -> Population:
        return population.breed(**self.kwargs)
