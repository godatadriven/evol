# Population Object

## Base

### evaluate

```
evaluate(lazy=False)
```


### apply

```
apply(f(Population, **kwargs) -> Population, **kwargs)
```


### map

```
map(f(Individual, **kwargs) -> Individual, **kwargs)
```

### filter

```
filter(f(Individual, **kwargs) -> bool, **kwargs)
```

## Simple

### set_attr

```
set_attr(attr_name: str, f(**kwargs), **kwargs)
```

### update

```
update(f(**kwargs), **kwargs)
```

It helps if this function `f` is written such that it respects globals.

```
time = 0

def f():
  global time
  time = time + 1
```

### survive

```
survive(fraction=None, n=None, luck=True)
```

### breed

```
breed(parent_picker=f(Population) -> seq[chromosome],
       f(*seq[chromosome]) -> chromosome,
       population_size=None, **kwargs)
```

### mutate_with

```
mutate_with(f(chromosome) -> chromosome, **kwargs)
```

## Group

### group_by

```
group_by(f(Population) -> {key: Population})
```

### group

```
group(num: int, how="random"/"iterative")
```

### clone

```
clone(num: int)
```

### combine

```
combine(*[Population] -> Population)
```

## Logging

### log

```
log(logger: EvolLogger)
```

# GroupedPopulation Object

This is the same as above. All these functions will run on each group independantly. Except for the `log` function.

## group

### exchange

```
exchange(f(from=Population, to=Population) -> seq[Individuals]), clone=True)
```

Note that function `f` will be run for every combination of groups.

### swap

Randomly selects from each population and swaps! 

```
swap(num=2, picker=None: f(Population) -> [Individuals])
```
If picker is None, pick randomly (or set random picker as default).

### merge

```
merge()
```

### perservere

Working title!

```
perservere(fraction=None, n=None, luck=True)
```

### produce_groups

```
produce_groups(seq[Population] -> Population, n_groups=10, **kwargs)
```

# Evolution

All of the above, plus:

## Store

Store the population somewhere
