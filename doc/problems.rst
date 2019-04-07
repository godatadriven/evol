Problem Guide
=============

Certain problems are general enough, if only for educational
purposes, to include into our API. This guide will demonstrate
some of problems that are included in evol.

General Idea
------------

In general a problem in evol is nothing more than an object
that has `.eval_function()` implemented. This object can
usually be initialised in different ways but the method
must always be implemented.

Function Problems
-----------------

There are a few hard functions out there that can be optimised
with heuristics. Our library offers a few objects with this
implementation.

The following functions are implemented.

.. code-block:: python

    from evol.problems.functions import Rastrigin, Sphere, Rosenbrock

    Rastrigin(size=1).eval_function([1])
    Sphere(size=2).eval_function([2, 1])
    Rosenbrock(size=3).eval_function([3, 2, 1])

You may notice that we pass a size parameter apon initialisation; this
is because these functions can also be defined in higher dimensions.
Feel free to check the wikipedia_ article for more explanation on these functions.


Routing Problems
----------------

Traveling Salesman Problem
**************************

It's a classic problem so we've included it here.

.. code-block:: python

    import random
    from evol.problems.routing import TSPProblem, coordinates

    us_cities = coordinates.united_states_capitols
    problem = TSPProblem.from_coordinates(coordinates=us_cities)

    order = list(range(len(us_cities)))
    for i in range(3):
        random.shuffle(order)
        print(problem.eval_function(order))

Note that you can also create an instance of a TSP problem
from a distance matrix instead. Also note that you can get
such a distance matrix from the object.

.. code:: python

    same_problem = TSPProblem(problem.distance_matrix)
    print(same_problem.eval_function(order))

Magic Santa
***********

This problem was inspired by a kaggle_ competition. It involves the logistics
of delivering gifts all around the world from the north pole. The costs of
delivering a gift depend on how tired santa's reindeer get while delivering
a sleigh full of gifts during a trip.


It is better explained on the website than here but the goal is to
minimize the weighed reindeer weariness defined below:

:math:`WRW = \sum\limits_{j=1}^{m} \sum\limits_{i=1}^{n} \Big[ \big( \sum\limits_{k=1}^{n} w_{kj} - \sum\limits_{k=1}^{i} w_{kj} \big) \cdot Dist(Loc_i, Loc_{i-1})`

In terms of setting up the problem it is very similar to a TSP except that
we now also need to attach the weight of a gift per location.

.. code:: python

    import random
    from evol.problems.routing import MagicSanta, coordinates

    us_cities = coordinates.united_states_capitols
    problem = TSPProblem.from_coordinates(coordinates=us_cities)

    MagicSanta(city_coordinates=us_cities,
               home_coordinate=(0, 0),
               gift_weight=[random.random() for _ in us_cities])

.. _wikipedia: https://en.wikipedia.org/wiki/Test_functions_for_optimization
.. _kaggle: https://www.kaggle.com/c/santas-stolen-sleigh#evaluation