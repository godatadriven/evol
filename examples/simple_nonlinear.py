import random
from random import random as r
from evol import Population, Evolution

random.seed(42)


def random_start():
    """
    This function generates a random (x,y) coordinate
    """
    return (r() - 0.5) * 20, (r() - 0.5) * 20


def func_to_optimise(xy):
    """
    This is the function we want to optimise (maximize)
    """
    x, y = xy
    return -(1 - x) ** 2 - (2 - y ** 2) ** 2


def pick_random_parents(pop):
    """
    This is how we are going to select parents from the population
    """
    mom = random.choice(pop)
    dad = random.choice(pop)
    return mom, dad


def make_child(mom, dad):
    """
    This function describes how two candidates combine into a
    new candidate. Note that the output is a tuple, just like
    the output of `random_start`. We leave it to the developer
    to ensure that chromosomes are of the same type.
    """
    child_x = (mom[0] + dad[0]) / 2
    child_y = (mom[1] + dad[1]) / 2
    return child_x, child_y


def add_noise(chromosome, sigma):
    """
    This is a function that will add some noise to the chromosome.
    """
    new_x = chromosome[0] + (r() - 0.5) * sigma
    new_y = chromosome[1] + (r() - 0.5) * sigma
    return new_x, new_y


# We start by defining a population with candidates.
pop = Population(chromosomes=[random_start() for _ in range(200)],
                 eval_function=func_to_optimise, maximize=True)

# We do a single step here and out comes a new population
pop.survive(fraction=0.5)

# We do two steps here and out comes a new population
(pop
 .survive(fraction=0.5)
 .breed(parent_picker=pick_random_parents, combiner=make_child))

# We do a three steps here and out comes a new population
(pop
 .survive(fraction=0.5)
 .breed(parent_picker=pick_random_parents, combiner=make_child)
 .mutate(mutate_function=add_noise, sigma=1))

# This is inelegant but it works.
for i in range(5):
    pop = (pop
           .survive(fraction=0.5)
           .breed(parent_picker=pick_random_parents, combiner=make_child)
           .mutate(mutate_function=add_noise, sigma=1))

# We define a sequence of steps to change these candidates
evo1 = (Evolution()
        .survive(fraction=0.5)
        .breed(parent_picker=pick_random_parents, combiner=make_child)
        .mutate(mutate_function=add_noise, sigma=1))

# We define another sequence of steps to change these candidates
evo2 = (Evolution()
        .survive(n=1)
        .breed(parent_picker=pick_random_parents, combiner=make_child)
        .mutate(mutate_function=add_noise, sigma=0.2))

# We are combining two evolutions into a third one.
# You don't have to but this approach demonstrates
# the flexibility of the library.
evo3 = (Evolution()
        .repeat(evo1, n=50)
        .repeat(evo2, n=10)
        .evaluate())

# In this step we are telling evol to apply the evolutions
# to the population of candidates.
pop = pop.evolve(evo3, n=5)
print(f"the best score found: {max([i.fitness for i in pop])}")
