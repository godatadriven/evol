from inspect import signature
from typing import Callable, Generator, List

from evol import Individual


def offspring_generator(parents: List[Individual],
                        parent_picker: Callable,
                        combiner: Callable,
                        **kwargs) -> Generator[Individual, None, None]:
    """Generator for offspring.

    This helps create the right number of offspring,
    especially in the case of of multiple offspring.

    :param parents: List of parents.
    :param parent_picker: Function that selects parents.
        Must accept all kwargs passed (i.e. must be decorated by select_arguments).
    :param combiner: Function that combines chromosomes.
        Must accept all kwargs passed (i.e. must be decorated by select_arguments).
    :param kwargs: Arguments
    :returns: Children
    """
    while True:
        # Obtain parent chromosomes
        parents = parent_picker(parents, **kwargs)
        chromosomes = tuple(individual.chromosome for individual in parents)
        # Create children
        if getattr(combiner, 'multiple_offspring', False):
            for child in combiner(*chromosomes, **kwargs):
                yield Individual(chromosome=child)
        else:
            yield Individual(chromosome=combiner(*chromosomes, **kwargs))


def select_arguments(func: Callable) -> Callable:
    """Decorate a function such that it accepts any keyworded arguments.

    The resulting function accepts any arguments, but only arguments that
    the original function accepts are passed. This allows keyworded 
    arguments to be passed to multiple (decorated) functions, even if they
    do not (all) accept these arguments.

    :param func: Function to decorate.
    :return: Callable
    """
    def result(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError:
            return func(*args, **{k: v for k, v in kwargs.items() if k in signature(func).parameters})
    return result


def ensure_list(func: Callable) -> Callable:
    """
    Decorate a function such that it always return a list

    This is useful when the caller needs an iterable but the function might return a
    single element under certain conditions.

    :param func: A function that returns a single element or a list
    :return: A function that always returns a list
    """
    def result(*args, **kwargs):
        try:
            return list(func(*args, **kwargs))
        except TypeError:
            return [func(*args, **kwargs)]
    return result