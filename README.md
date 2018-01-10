
[![Build Status](https://travis-ci.org/godatadriven/evol.svg?branch=master)](https://travis-ci.org/godatadriven/evol)

![Imgur](https://i.imgur.com/7MHcIq1.png)

`Evol` is clear dsl for composable evolutionary algorithms optimised for joy.

## Installation

We currently support python3.6 and you can install it via pip.

```
pip install evol
```

## Documentation

For more details you can read the [docs hosted on github](https://godatadriven.github.io/evol/) but we advice everyone to get start by first checking out the examples in the `/examples` directory. These stand alone examples should show the spirit of usage better than the docs.

## The Gist

The main idea is that you should be able to define a complex algorithm
in a composable way. To explain what we mean by this:  let's consider
two evolutionary algorithms for travelling salesman problems.

The first approach takes a collections of solutions and applies:

1. a survival where only the top 50% solutions survive
2. the population reproduces using a crossover of genes
3. certain members mutate_with
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

You might notice that many parts of these algorithms are similar and it is
the goal of this library is to automate these parts. In fact, you can
expect the code for these algorithms to look something like this.

A pseudo-example of what is decribed about looks a bit like this:

    import random
    from evol import Population, Evolution

    population = Population(init_func=init_func, eval_func=eval_func, size=100)

    def pick_n_parents(population, num_parents):
        return [random.choice(population) for i in range(num_parents)]

    def crossover(*parents):
        ...

    def random_copy(parent):
        ...

    evo1 = (Evolution(name="first_algorithm")
           .survive(fraction=0.5)
           .breed(parentpicker=pick_n_parents,
                  combiner=combiner,
                  num_parents=2, n_max=100)
           .mutate_with(lambda x: add_noise(x, 0.1)))

    evo2 = (Evolution(name="second_algorithm")
           .survive(n=1)
           .breed(parentpicker=pick_n_parents,
                  combiner=random_copy,
                  num_parents=1, n_max=100))

    for i in range(1001):
        population.evolve(evo1, n=50).evolve(evo2, n=10)

Getting Started
---------------------------------------

The best place to get started is the `/examples` folder on github.
This folder contains self contained examples that work out of the
box.

## How does it compare to ...

- [... deap?](https://github.com/DEAP/deap) We think our library is more composable and pythonic while not removing any functionality. Our library may be a bit slower though.
- [... hyperopt?](http://jaberg.github.io/hyperopt/) Since we force the user to make the actual algorithm we are less black boxy. Hyperopt is meant for hyperparameter tuning for machine learning and has better support for search in scikit learn.
