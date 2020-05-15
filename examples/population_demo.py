import random
from evol import Population


def create_candidate():
    return random.random() - 0.5


def func_to_optimise(x):
    return x*2


def pick_random_parents(pop):
    return random.choice(pop),


random.seed(42)

pop1 = Population(chromosomes=[create_candidate() for _ in range(5)],
                  eval_function=func_to_optimise, maximize=True)

pop2 = Population.generate(init_function=create_candidate,
                           eval_function=func_to_optimise,
                           size=5,
                           maximize=False)


print("[i for i in pop1]:")
print([i for i in pop1])
print("[i.chromosome for i in pop1]:")
print([i.chromosome for i in pop1])
print("[i.fitness for i in pop1]:")
print([i.fitness for i in pop1])
print("[i.fitness for i in pop1.evaluate()]:")


def produce_clone(parent):
    return parent


def add_noise(x):
    return 0.1 * (random.random() - 0.5) + x


print("[i.fitness for i in pop1.survive(n=3)]:")
print([i.fitness for i in pop1.survive(n=3)])
print("[i.fitness for i in pop1.survive(n=3).mutate(add_noise)]:")
print([i.fitness for i in pop1.survive(n=3).mutate(add_noise)])
print("[i.fitness for i in pop1.survive(n=3).mutate(add_noise).evaluate()]:")
print([i.fitness for i in pop1.survive(n=3).mutate(add_noise).evaluate()])
