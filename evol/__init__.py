"""
![Imgur](https://i.imgur.com/7MHcIq1.png)

`Evol` is clear dsl for composable evolutionary algorithms that optimised for joy.

Evol is a library that helps you make evolutionary algorithms. The
goal is to have a library that is fun and clear to use, but not fast.

If you're looking at the library for the first time we recommend
that you first take a look at the examples in the /examples folder
on github. It is usually a better starting point to get started.

Any details can be discovered on the docs. We hope that this
library makes it fun to write heuristics again.

The Gist
---------------------------------------

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

You might notice that many parts of these algorithms are similar and it is
the goal of this library is to automate these parts. In fact, you can
expect the code for these algorithms to look something like this.

A speudo-example of what is decribed about looks a bit like this:

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
           .mutate(lambda x: add_noise(x, 0.1)))

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

Contributing Guide
---------------------------------------

### Local development

Python can help you. Don't reinstall all the time, rather use a
virtulenv that has a link to the code.

    python setup.py develop

When you submit a pull request it will be tested in travis. Once
the build is green the review can start. Please try to keep your
branch up to date to ensure you're not missing any tests. Larger
commits need to be discussed in github before we can accept them.

### Generating New Documentation

Updating documentation is currently a manual step. From the `docs` folder:

    pdoc --html --overwrite evol
    cp -rf evol/* .
    rm -rf evol

If you want to confirm that it works you can open the `index.html` file.
"""

from .individual import Individual
from .population import Population, ContestPopulation
from .evolution import Evolution
from .logger import BaseLogger

__version__ = "0.5.2"
