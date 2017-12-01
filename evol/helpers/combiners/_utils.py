from collections import defaultdict
from itertools import tee, islice, cycle
from random import choice
from typing import Iterable, Tuple, Generator, Any


def construct_neighbors(*chromosome: Tuple[Any]) -> defaultdict:
    result = defaultdict(set)
    for l in chromosome:
        for x, y in _neighbors_in(l):
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


def select_node(start_node: Any, neighbors: defaultdict) -> Generator[Any]:
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
