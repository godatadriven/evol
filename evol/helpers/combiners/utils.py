from collections import defaultdict
from itertools import tee, islice, cycle

from random import choice
from typing import Iterable, Generator, Any, Set, List, Dict, Tuple


def construct_neighbors(*chromosome: Tuple[Any]) -> defaultdict:
    result = defaultdict(set)
    for element in chromosome:
        for x, y in _neighbors_in(element):
            result[x].add(y)
            result[y].add(x)
    return result


def _neighbors_in(x: Tuple[Any], cyclic=True) -> Iterable[Tuple[Any, Any]]:
    a, b = tee(islice(cycle(x), 0, len(x) + (1 if cyclic else 0)))
    next(b, None)
    return zip(a, b)


def _remove_from_neighbors(neighbors, node):
    del neighbors[node]
    for _, element in neighbors.items():
        element.difference_update({node})


def select_node(start_node: Any, neighbors: defaultdict) -> Generator[Any, None, None]:
    node = start_node
    yield node
    while len(neighbors) > 1:
        options = neighbors[node]
        _remove_from_neighbors(neighbors, node)
        if len(options) > 0:
            min_len = min([len(neighbors[option]) for option in options])
            node = choice([option for option in options if len(neighbors[option]) == min_len])
        else:
            node = choice(list(neighbors.keys()))
        yield node


def identify_cycles(chromosome_1: Tuple[Any], chromosome_2: Tuple[Any]) -> List[Set[int]]:
    """Identify all cycles between the chromosomes.

    A cycle is found by following this procedure: given an index, look up the
    value in the first chromosome. Then find the index of that value in the
    second chromosome. Repeat, until one returns to the original index.

    :param chromosome_1: First chromosome.
    :param chromosome_2: Second chromosome.
    :return: A list of cycles.
    """
    indices = set(range(len(chromosome_1)))
    cycles = []
    while len(indices) > 0:
        next_cycle = _identify_cycle(chromosome_1=chromosome_1, chromosome_2=chromosome_2, start_index=min(indices))
        indices.difference_update(next_cycle)
        cycles.append(next_cycle)
    return cycles


def _identify_cycle(chromosome_1: Tuple[Any], chromosome_2: Tuple[Any], start_index: int = 0) -> Set[int]:
    """Identify a cycle between the chromosomes starting at the provided index.

    A cycle is found by following this procedure: given an index, look up the
    value in the first chromosome. Then find the index of that value in the
    second chromosome. Repeat, until one returns to the original index.

    :param chromosome_1: First chromosome.
    :param chromosome_2: Second chromosome.
    :param start_index: Index to start. Defaults to 0.
    :return: The set of indices in the identified cycle.
    """
    indices = set()
    index = start_index
    while index not in indices:
        indices.add(index)
        value = chromosome_1[index]
        index = chromosome_2.index(value)
    return indices


def cycle_parity(cycles: List[Set[int]]) -> Dict[int, bool]:
    """Create a dictionary with the cycle parity of each index.

    Indices in all odd cycles have parity False, while
    indices in even cycles have parity True."""
    return {index: bool(i % 2) for i, c in enumerate(cycles) for index in c}
