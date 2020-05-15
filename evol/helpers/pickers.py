from random import choice
from typing import Callable, Sequence, Tuple

from evol import Individual


def pick_random(n_parents: int = 2) -> Callable[[Sequence[Individual]], Tuple[Individual, ...]]:
    """Returns a parent-picker that randomly samples parents with replacement.

    Typical usage:
        Evolution().breed(parent_picker=pick_random(n_parents=2), combiner=some_combiner)

    :param n_parents: The number of parents the picker should return.
    :return: Callable
    """
    def picker(parents: Sequence[Individual]) -> Tuple[Individual, ...]:
        return tuple(choice(parents) for _ in range(n_parents))

    return picker
