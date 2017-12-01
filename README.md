
[![Build Status](https://travis-ci.org/koaning/evol.svg?branch=master)](https://travis-ci.org/koaning/evol)

# evol.py


`Evol` is functional dsl for composable evolutionary algorithms written in python.

## Installation

We currently support python3.6 and you can install it via pip.

```
pip install evol
```

## The Gist

The main idea is that you should be able to define an evolutionary algorithm with a tool such that you can write complex algorithms in a composable way.

Here's a brief example of what the code might look like.

```
from evol import Population, Evolution

population = Population(init_func=init_func, eval_func=eval_func, size=100)

evo1 = (Evolution(name="evo1")
       .survive(0.6)
       .breed(parentpicker=parent_picker, create_chromosome=combiner, n_max=100)
       .mutate(lambda x: change(x, 0.1)))

evo2 = (Evolution(name="evo2")
       .survive(0.3)
       .breed(parentpicker=parent_picker, create_chromosome=combiner, n_max=100)
       .mutate(lambda x: change(x, 0.01)))

for i in range(10):
    population.evolve(evo1, n=10).evolve(evo2, n=100)
```

For more details you can read the [docs](https://godatadriven.github.io/evol/) but we advice everyone to get start by first checking out the examples in the `/examples` directory. These stand alone examples should show the spirit of usage better than the docs.

## How does it compare to ...

- [... deap?](https://github.com/DEAP/deap) We think our library is more composable and pythonic while not removing any functionality. Our library may be a bit slower though.
- [... hyperopt?](http://jaberg.github.io/hyperopt/) Since we force the user to make the actual algorithm we are less black boxy. Hyperopt is meant for hyperparameter tuning for machine learning and has better support for search in scikit learn.
