from random import randint
from typing import Tuple


def select_partition(length: int, min_size: int = 1, max_size: int = None) -> Tuple[int, int]:
    """Select a partition of a chromosome.

    :param length: Length of the chromosome.
    :param min_size: Minimum length of the partition. Defaults to 1.
    :param max_size: Maximum length of the partition. Defaults to length - 1.
    :return: Start and end index of the partition.
    """
    partition_size = randint(min_size, length - 1 if max_size is None else max_size)
    partition_start = randint(0, length - partition_size)
    return partition_start, partition_start + partition_size


def rotating_window(arr):
    """rotating_window([1,2,3,4]) -> [(4,1), (1,2), (2,3), (3,4)]"""
    for i, city in enumerate(arr):
        yield arr[i - 1], arr[i]


def sliding_window(arr):
    """sliding_window([1,2,3,4]) -> [(1,2), (2,3), (3,4)]"""
    for i, city in enumerate(arr[:-1]):
        yield arr[i], arr[i + 1]
