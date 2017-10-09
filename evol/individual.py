from uuid import uuid4


class Individual:
    """Represents an individual in a population. The individual has a chromosome."""

    def __init__(self, chromosome):
        self.age = 0
        self.chromosome = chromosome
        self.fitness = None
        self.id = f"{str(uuid4())[:6]}"

    def __repr__(self):
        return f"<individual id:{self.id} fitness:{self.fitness}>"

    def evaluate(self, eval_function, lazy=False):
        """Evaluate the fitness of the individual.

        :param eval_function: Function that reduces a chromosome to a fitness.
        :type eval_function: Callable[float]
        :param lazy: If True, do no re-evaluate the fitness if the fitness is known.
        :type lazy: bool
        """
        if self.fitness is None or not lazy:
            self.fitness = eval_function(self.chromosome)

    def mutate(self, func, **kwargs):
        """Mutate the chromosome of the individual.

        :param func: Function that accepts a chromosome and returns a mutated chromosome.
        :type func: Callable[chromosome, **kwargs] -> chromosome
        :param kwargs: Arguments to pass to the mutation function.
        """
        self.chromosome = func(self.chromosome, **kwargs)
        self.fitness = None
