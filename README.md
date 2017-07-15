# evol.py

> A few good composable functions is better than a lot of static ones.

`Evol` is functional dsl for composable evolutionary algorithms written in python.


## The Gist

The main idea is that you should be able to define an evolutionary algorithm with a language such that you can write complex algorithms rather simply.

Here's a nice example.

```
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
```

## How does it compare to ...

- [... deap?](https://github.com/DEAP/deap) We think our library is more composable and pythonic while not removing any functionality. Our library may be a bit slower though.