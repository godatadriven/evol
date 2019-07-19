from inspect import signature
from typing import List, Callable, Union, Sequence, Any, Generator

from evol import Individual


def offspring_generator(parents: List[Individual],
                        parent_picker: Callable[..., Union[Individual, Sequence]],
                        combiner: Callable[..., Any],
                        **kwargs) -> Generator[Individual, None, None]:
    """Generator for offspring.

    This helps create the right number of offspring,
    especially in the case of of multiple offspring.

    :param parents: List of parents.
    :param parent_picker: Function that selects parents. Must accept a sequence of
        individuals and must return a single individual or a sequence of individuals.
        Must accept all kwargs passed (i.e. must be decorated by select_arguments).
    :param combiner: Function that combines chromosomes. Must accept a tuple of
        chromosomes and either return a single chromosome or yield multiple chromosomes.
        Must accept all kwargs passed (i.e. must be decorated by select_arguments).
    :param kwargs: Arguments
    :returns: Children
    """
    while True:
        # Obtain parent chromosomes
        selected_parents = parent_picker(parents, **kwargs)
        if isinstance(selected_parents, Individual):
            chromosomes = (selected_parents.chromosome,)
        else:
            chromosomes = tuple(individual.chromosome for individual in selected_parents)
        # Create children
        combined = combiner(*chromosomes, **kwargs)
        if isinstance(combined, Generator):
            for child in combined:
                yield Individual(chromosome=child)
        else:
            yield Individual(chromosome=combined)


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
