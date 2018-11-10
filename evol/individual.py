"""
Individual objects in `evol` are a wrapper around a chromosome.
Internally we work with individuals because that allows us to
separate the fitness calculation from the data structure. This
saves a lot of CPU power.
"""

from typing import Any, Callable, Optional
from uuid import uuid4

from random import random


class Individual:
    """Represents an individual in a population. The individual has a chromosome.

    :param chromosome: The chromosome of the individual.
    :param fitness: The fitness of the individual, or None.
        Defaults to None.
    """

    def __init__(self, chromosome: Any, fitness: Optional[float]=None):
        self.age = 0
        self.chromosome = chromosome
        self.fitness = fitness
        self.id = f"{str(uuid4())[:6]}"

    def __repr__(self):
        return f"<individual id:{self.id} fitness:{self.fitness}>"

    @classmethod
    def from_dict(cls, data: dict) -> 'Individual':
        """Load an Individual from a dictionary.

        :param data: Dictionary containing the keys 'age', 'chromosome', 'fitness' and 'id'.
        :return: Individual
        """
        result = cls(chromosome=data['chromosome'], fitness=data['fitness'])
        result.age = data['age']
        result.id = data['id']
        return result

    def evaluate(self, eval_function: Callable[..., float], lazy: bool=False):
        """Evaluate the fitness of the individual.

        :param eval_function: Function that reduces a chromosome to a fitness.
        :param lazy: If True, do no re-evaluate the fitness if the fitness is known.
        """
        if self.fitness is None or not lazy:
            self.fitness = eval_function(self.chromosome)

    def mutate(self, mutate_function: Callable[..., Any], probability: float=1.0, **kwargs):
        """Mutate the chromosome of the individual.

        :param mutate_function: Function that accepts a chromosome and returns a mutated chromosome.
        :param probability: Probability that the individual mutates.
            The function is only applied in the given fraction of cases.
            Defaults to 1.0.
        :param kwargs: Arguments to pass to the mutation function.
        """
        if probability == 1.0 or random() < probability:
            self.chromosome = mutate_function(self.chromosome, **kwargs)
            self.fitness = None
