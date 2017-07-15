from uuid import uuid4
from copy import deepcopy
import random
import math


'''
A few good composable functions is better than a lot of static ones: 

.mutate(f(i,p,a) -> i, *attrs, **kwargs)
.survive(f(i,p,a) -> bool, *attrs, **kwargs)
.breed(f(p,a) -> seq[i], g(seq[i]) -> i)
.set_attr_individual(str_name, f(i,p,a) -> value)
.set_attr_population(str_name, f(i,p,a) -> value)
.set_attr_algorithm(str_name, f(i,p,a) -> value)

I'm in the air about these:
.groupby(f(i,p,a) -> hash)
.ungroup() -> removes group
.exchange(f(i,p,a) -> group) 
.clone(n_groups)

Can we implement these? 
- tabu list
- simulated annealing 
- cuckoo search 

Features: 
- logging (to tensorflow?) 
- parallelism (usefull for every expensive eval_funcs) 

'''

class Individual:
    def __init__(self, chromosome, eval_func):
        self.id = f"{str(uuid4())[:6]}"
        self.chromosome = chromosome
        self.value = eval_func(self.chromosome)
        self.age = 0
        self.eval_func = eval_func

    def change_chromosome(self, new):
        self.chromosome = new
        self.value = self.eval_func(self.chromosome)
        return self

    def __repr__(self):
        return f"<individual id:{self.id} value:{self.value}>"

class Population:
    def __init__(self, eval_func, init_func, size=100):
        self.individuals = [Individual(chromosome=init_func(), eval_func=eval_func) for _ in range(size)]
        self.eval_func = eval_func

    def __iter__(self):
        return self.individuals.__iter__()

    def __getitem__(self, i):
        return self.individuals[i]

    def __len__(self):
        return len(self.individuals)

    def __repr__(self):
        return f"<Population object with size {len(self)}>"

    @property
    def min_score(self):
        return min([i.value for i in self.individuals])

    @property
    def max_score(self):
        return max([i.value for i in self.individuals])

    def __len__(self):
        return len(self.individuals)

class Evolution:
    def __init__(self, name=None):
        self.chain = []
        self.name = f"{str(uuid4())[:6]}" if not name else name

    def apply(self, population):
        for func in self.chain:
            population = func(population)
            for i in population:
                i.age +=1
        return population

    def rename(self, name):
        self.name = name

    def mutate(self, mutate_func):
        def _mutate(population):
            population.individuals = [i.change_chromosome(mutate_func(i)) for i in population]
            return population
        self.chain.append(_mutate)
        return self


    def survive(self, percentage):
        def _survive(population):
            output = deepcopy(population)
            border_idx = int(math.floor(percentage*len(output)))
            border_val = sorted([i.value for i in output.individuals])[border_idx]
            output.individuals = [i for i in output.individuals if i.value >= border_val]
            return output
        self.chain.append(_survive)
        return self


    def breed(self, parentpicker, create_chromosome, n_max):
        def _breed(population):
            for new_individual in range(len(population), n_max):
                mom, dad = parentpicker(population)
                child_chromosome = create_chromosome(mom, dad)
                child = Individual(chromosome=child_chromosome, eval_func=population.eval_func)
                population.individuals.append(child)
            return population
        self.chain.append(_breed)
        return self

    def __repr__(self):
        res = "<evoltion obj> with steps: "
        for func in self.chain:
            func_name = str(func.__name__).replace("_","")
            res = f"{res}\n - {func_name}"
        return res


class Algorithm:
    def __init__(self, population, evolution, verbose=False, logging=False, name=None):
        self.population = population
        self.evolution = evolution
        self.verbose = verbose
        self.logging = logging
        self.id = f"{str(uuid4())[:6]}" if not name else name
        self.iteration = 0

    def change_evolution(self, evolution):
        self.evolution = evolution
        return self

    def run(self, n=100):
        for i in range(n):
            self.iteration += 1
            self.population = self.evolution.apply(self.population)
            if self.verbose:
                print(f"alg:{self.id} evo:{self.evolution.name} iteration:{self.iteration} min:{self.population.min_score} max:{self.population.max_score}")
        return self