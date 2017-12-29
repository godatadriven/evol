"""
Individual objects in `evol` are a wrapper around a chromosome.
Internally we work with individuals because that allows us to 
seperate the fitness calculation from the datastructure. This 
saves a lot of CPU power.
"""

from random import random
from uuid import uuid4


class Individual:
    """Represents an individual in a population. The individual has a chromosome."""

    def __init__(self, chromosome, fitness=None):
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

    def evaluate(self, eval_function, lazy=False):
        """Evaluate the fitness of the individual.

        :param eval_function: Function that reduces a chromosome to a fitness.
        :type eval_function: Callable[chromosome] -> float
        :param lazy: If True, do no re-evaluate the fitness if the fitness is known.
        :type lazy: bool
        """
        if self.fitness is None or not lazy:
            self.fitness = eval_function(self.chromosome)

    def mutate(self, func, probability=1.0, **kwargs):
        """Mutate the chromosome of the individual.

        :param func: Function that accepts a chromosome and returns a mutated chromosome.
        :type func: Callable[chromosome, **kwargs] -> chromosome
        :param probability: Probability that the individual mutates.
            The function is only applied in the given fraction of cases.
            Defaults to 1.0.
        :type probability: float
        :param kwargs: Arguments to pass to the mutation function.
        """
        if probability == 1.0 or random() < probability:
            self.chromosome = func(self.chromosome, **kwargs)
            self.fitness = None
