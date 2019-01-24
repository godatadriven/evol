from random import sample
from typing import Any, Tuple

from ..utils import select_partition


def inversion(chromosome: Tuple[Any, ...], min_size: int = 2, max_size: int = None) -> Tuple[Any, ...]:
    """Mutate a chromosome using inversion.

    Inverts a random partition of the chromosome.

    :param chromosome: Original chromosome.
    :param min_size: Minimum partition size. Defaults to 2.
    :param max_size: Maximum partition size. Defaults to length - 1.
    :return: Mutated chromosome.
    """
    start, end = select_partition(len(chromosome), min_size, max_size)
    return chromosome[:start] + tuple(reversed(chromosome[start:end])) + chromosome[end:]


def swap_elements(chromosome: Tuple[Any, ...]) -> Tuple[Any, ...]:
    """Randomly swap two elements of the chromosome.

    :param chromosome: Original chromosome.
    :return: Mutated chromosome.
    """
    result = list(chromosome)
    index_1, index_2 = sample(range(len(chromosome)), 2)
    result[index_1], result[index_2] = result[index_2], result[index_1]
    return tuple(result)
