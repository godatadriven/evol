from evol import Population, Evolution, Algorithm
import random

## first algorithm
def eval_func(chromosome):
    return chromosome


def init_func():
    return random.random()


def parent_picker(population):
    mom, dad = random.choice(population), random.choice(population)
    return mom, dad


def combiner(mom, dad):
    return random.choice([mom.chromosome, dad.chromosome])


population = Population(eval_func=eval_func, init_func=init_func, size=100)
evo = (Evolution()
       .survive(0.1)
       .breed(parentpicker=parent_picker, create_chromosome=combiner, n_max=100)
       .mutate(lambda x: x.chromosome + (random.random() - 0.5) / 10))

alg = Algorithm(population=population, evolution=evo, verbose=True)
alg.run()

## second algorithm
def eval_func(chromosome):
    return sum(chromosome)


def init_func():
    return [round(random.random()) for _ in range(100)]


def combiner(mom, dad):
    chromosome = [_[0] if _[0]==_[1] else round(random.random()) for _ in zip(mom.chromosome, dad.chromosome)]
    return chromosome


def change(child, prob=0.02):
    res = []
    for c in child.chromosome:
        if random.random() < prob:
            res.append(round(random.random()))
        else:
            res.append(c)
    return res


population = Population(eval_func=eval_func, init_func=init_func, size=100)
evo = (Evolution()
       .survive(0.5)
       .breed(parentpicker=parent_picker, create_chromosome=combiner, n_max=100)
       .mutate(change))

alg = Algorithm(population=population, evolution=evo, verbose=False)
alg.run()

## demo composable algorithm

population = Population(eval_func=eval_func, init_func=init_func, size=100)

evo1 = (Evolution(name="evo1")
       .survive(0.6)
       .breed(parentpicker=parent_picker, create_chromosome=combiner, n_max=100)
       .mutate(lambda x: change(x, 0.1)))

evo2 = (Evolution(name="evo2")
       .survive(0.3)
       .breed(parentpicker=parent_picker, create_chromosome=combiner, n_max=100)
       .mutate(lambda x: change(x, 0.01)))

alg = Algorithm(population=population, evolution=evo1, verbose=True)
alg.run(100).change_evolution(evo2).run(50)

## demo sexless reproduction

evo_sexless = (Evolution(name = "sexless")
               .survive(0.2)
               .breed(parentpicker=parent_picker, create_chromosome=lambda mom, dad: mom.chromosome, n_max=100)
               .mutate(lambda x: change(x, 0.1)))

alg = Algorithm(population=population, evolution=evo_sexless, verbose=True)
alg.run(100)
