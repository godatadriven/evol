from evol import Evolution, Population

from evol import CurrentPopulation

pop = Population()


def calc_pheromone(pop, n):
    return n


evo = Evolution().group(n=4).apply(calc_pheromone, pop=CurrentPopulation, n=4)


def apply(self, fct, **kwargs):
    return fct(**{key: self if value is CurrentPopulation else value for key, value in kwargs.items()})

