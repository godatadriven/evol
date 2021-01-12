[![Documentation Status](https://readthedocs.org/projects/evol/badge/?version=latest)](https://evol.readthedocs.io/en/latest/?badge=latest)[![Downloads](https://pepy.tech/badge/evol)](https://pepy.tech/project/evol)
[![Build Status](https://dev.azure.com/godatadriven/evol/_apis/build/status/godatadriven.evol?branchName=master)](https://dev.azure.com/godatadriven/evol/_build/latest?definitionId=9&branchName=master) [![Documentation Status](https://readthedocs.org/projects/evol/badge/?version=latest)](https://evol.readthedocs.io/en/latest/?badge=latest)[![Downloads](https://pepy.tech/badge/evol)](https://pepy.tech/project/evol)


![Imgur](https://i.imgur.com/7MHcIq1.png)

`Evol` is clear dsl for composable evolutionary algorithms that optimised for joy.

## Installation

We currently support python3.6 and python3.7 and you can install it via pip.

```
pip install evol
```

## Documentation

For more details you can read the [docs](https://evol.readthedocs.io/en/latest/) but we advice everyone to get start by first checking out the examples in the `/examples` directory. These stand alone examples should show the spirit of usage better than the docs.

## The Gist

The main idea is that you should be able to define a complex algorithm
in a composable way. To explain what we mean by this:  let's consider
two evolutionary algorithms for travelling salesman problems.

The first approach takes a collections of solutions and applies:

1. a survival where only the top 50% solutions survive
2. the population reproduces using a crossover of genes
3. certain members mutate
4. repeat this, maybe 1000 times or more!

<img src="https://i.imgur.com/is9g07u.png" alt="Drawing" style="width: 100%;"/>

We can also think of another approach:

1. pick the best solution of the population
2. make random changes to this parent and generate new solutions
3. repeat this, maybe 1000 times or more!

<img src="https://i.imgur.com/JRSWbTd.png" alt="Drawing" style="width: 100%;"/>

One could even combine the two algorithms into a new one:

1. run algorithm 1 50 times
2. run algorithm 2 10 times
3. repeat this, maybe 1000 times or more!

<img src="https://i.imgur.com/SZTBWX2.png" alt="Drawing" style="width: 100%;"/>

You might notice that many parts of these algorithms are similar and it
is the goal of this library is to automate these parts. We hope to
provide an API that is fun to use and easy to tweak your heuristics in.

A working example of something silimar to what is depicted above is shown below. You can also find this code as an example in the `/examples/simple_nonlinear.py`. 

```python
import random
from evol import Population, Evolution

random.seed(42)

def random_start():
    """
    This function generates a random (x,y) coordinate
    """
    return (random.random() - 0.5) * 20, (random.random() - 0.5) * 20

def func_to_optimise(xy):
    """
    This is the function we want to optimise (maximize)
    """
    x, y = xy
    return -(1-x)**2 - 2*(2-x**2)**2

def pick_random_parents(pop):
    """
    This is how we are going to select parents from the population
    """
    mom = random.choice(pop)
    dad = random.choice(pop)
    return mom, dad

def make_child(mom, dad):
    """
    This function describes how two candidates combine into a new candidate
    Note that the output is a tuple, just like the output of `random_start`
    We leave it to the developer to ensure that chromosomes are of the same type
    """
    child_x = (mom[0] + dad[0])/2
    child_y = (mom[1] + dad[1])/2
    return child_x, child_y

def add_noise(chromosome, sigma):
    """
    This is a function that will add some noise to the chromosome.
    """
    new_x = chromosome[0] + (random.random()-0.5) * sigma
    new_y = chromosome[1] + (random.random()-0.5) * sigma
    return new_x, new_y

# We start by defining a population with candidates.
pop = Population(chromosomes=[random_start() for _ in range(200)],
                 eval_function=func_to_optimise, maximize=True)

# We define a sequence of steps to change these candidates
evo1 = (Evolution()
       .survive(fraction=0.5)
       .breed(parent_picker=pick_random_parents, combiner=make_child)
       .mutate(func=add_noise, sigma=1))

# We define another sequence of steps to change these candidates
evo2 = (Evolution()
       .survive(n=1)
       .breed(parent_picker=pick_random_parents, combiner=make_child)
       .mutate(func=add_noise, sigma=0.2))

# We are combining two evolutions into a third one. You don't have to
# but this approach demonstrates the flexibility of the library.
evo3 = (Evolution()
       .repeat(evo1, n=50)
       .repeat(evo2, n=10)
       .evaluate())

# In this step we are telling evol to apply the evolutions
# to the population of candidates.
pop = pop.evolve(evo3, n=5)
print(f"the best score found: {max([i.fitness for i in pop])}")
```

Getting Started
---------------------------------------

The best place to get started is the `/examples` folder on github.
This folder contains self contained examples that work out of the
box.

## How does it compare to ...

- [... deap?](https://github.com/DEAP/deap) We think our library is more composable and pythonic while not removing any functionality. Our library may be a bit slower though.
- [... hyperopt?](http://jaberg.github.io/hyperopt/) Since we force the user to make the actual algorithm we are less black boxy. Hyperopt is meant for hyperparameter tuning for machine learning and has better support for search in scikit learn.
- [... inspyred?](https://pypi.org/project/inspyred/) The library offers a simple way to get started but it seems the project is less actively maintained than ours. 
