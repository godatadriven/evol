from typing import Sequence, Tuple

from random import choice

from evol import Individual


def pick_random(parents: Sequence[Individual], n_parents: int=2) -> Tuple:
    """Randomly selects parents with replacement

    Accepted arguments:
      n_parents: Number of parents to select. Defaults to 2.
    """
    return tuple(choice(parents) for _ in range(n_parents))
