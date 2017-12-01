from typing import Any, Tuple

from .._utils import select_partition


def inversion(chromosome: Tuple[Any, ...], min_size: int=2, max_size: int=None) -> Tuple:
    """Mutate a chromosome using inversion.

    Inverts a random partition of the chromosome.

    :param chromosome: Original chromosome.
    :param min_size: Minimum partition size. Defaults to 2.
    :param max_size: Maximum partition size. Defaults to length - 1.
    :return: Mutated chromosome.
    """
    start, end = select_partition(len(chromosome), min_size, max_size)
    return chromosome[:start] + tuple(reversed(chromosome[start:end])) + chromosome[end:]
