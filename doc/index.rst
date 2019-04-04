.. evol documentation master file, created by
   sphinx-quickstart on Thu Apr  4 09:34:54 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**Evol** is clear dsl for composable evolutionary algorithms that optimised for joy.

.. image:: _static/evol.png
   :align: center

.. code-block:: bash

   pip install evol

The Gist
********

The main idea is that you should be able to define a complex algorithm
in a composable way. To explain what we mean by this:  let's consider
two evolutionary algorithms for travelling salesman problems.

The first approach takes a collections of solutions and applies:

1. a survival where only the top 50% solutions survive
2. the population reproduces using a crossover of genes
3. certain members mutate
4. repeat this, maybe 1000 times or more!

.. image:: https://i.imgur.com/is9g07u.png
   :align: center

We can also think of another approach:

1. pick the best solution of the population
2. make random changes to this parent and generate new solutions
3. repeat this, maybe 1000 times or more!

.. image:: https://i.imgur.com/JRSWbTd.png
   :align: center

One could even combine the two algorithms into a new one:

1. run algorithm 1 50 times
2. run algorithm 2 10 times
3. repeat this, maybe 1000 times or more!

.. image:: https://i.imgur.com/SZTBWX2.png
   :align: center

You might notice that many parts of these algorithms are similar and it
is the goal of this library is to automate these parts. We hope to
provide an API that is fun to use and easy to tweak your heuristics in.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   population
   evolution
   contests
   problems
   parallel
   development

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
