from uuid import uuid4


class Individual:

    def __init__(self, chromosome):
        self.age = 0
        self.chromosome = chromosome
        self.fitness = None
        self.id = f"{str(uuid4())[:6]}"

    def __repr__(self):
        return f"<individual id:{self.id} fitness:{self.fitness}>"

    def evaluate(self, eval_function, lazy=False):
        if self.fitness is None or not lazy:
            self.fitness = eval_function(self.chromosome)

    def mutate(self, func, **kwargs):
        self.chromosome = func(self.chromosome, **kwargs)
        self.fitness = None
