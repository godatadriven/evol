from .population import Population


class EvolutionStep:

    def __init__(self, name, **kwargs):
        self.name = name
        self.kwargs = kwargs


class EvaluationStep(EvolutionStep):

    def __init__(self, name, lazy=False):
        EvolutionStep.__init__(self, name=name, lazy=lazy)

    def apply(self, population) -> Population:
        return population.evaluate(**self.kwargs)


class ApplyStep(EvolutionStep):

    def __init__(self, name):
        EvolutionStep.__init__(self, name=name)

    def apply(self, population) -> Population:
        return population.apply(**self.kwargs)


class MapStep(EvolutionStep):

    def __init__(self, name):
        EvolutionStep.__init__(self, name=name)

    def apply(self, population) -> Population:
        return population.map(**self.kwargs)


class FilterStep(EvolutionStep):

    def __init__(self, name):
        EvolutionStep.__init__(self, name=name)

    def apply(self, population) -> Population:
        return population.filter(**self.kwargs)


class UpdateStep(EvolutionStep):

    def __init__(self, name):
        EvolutionStep.__init__(self, name=name)

    def apply(self, population) -> Population:
        return population.update(**self.kwargs)


class SurviveStep(EvolutionStep):

    def __init__(self, name):
        EvolutionStep.__init__(self, name=name)

    def apply(self, population) -> Population:
        return population.survive(**self.kwargs)


class BreedStep(EvolutionStep):

    def __init__(self, name):
        EvolutionStep.__init__(self, name=name)

    def apply(self, population) -> Population:
        return population.breed(**self.kwargs)


class MutateStep(EvolutionStep):
    def __init__(self, name):
        EvolutionStep.__init__(self, name=name)

    def apply(self, population) -> Population:
        return population.breed(**self.kwargs)
