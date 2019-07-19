from itertools import islice, tee
from random import choice
from typing import Any, Tuple

from .utils import select_node, construct_neighbors, identify_cycles, cycle_parity
from ..utils import select_partition


def order_one_crossover(parent_1: Tuple, parent_2: Tuple) -> Tuple:
    """Combine two chromosomes using order-1 crossover.

    http://www.rubicite.com/Tutorials/GeneticAlgorithms/CrossoverOperators/Order1CrossoverOperator.aspx

    :param parent_1: First parent.
    :param parent_2: Second parent.
    :return: Child chromosome.
    """
    start, end = select_partition(len(parent_1))
    selected_partition = parent_1[start:end + 1]
    remaining_elements = filter(lambda element: element not in selected_partition, parent_2)
    return tuple(islice(remaining_elements, 0, start)) + selected_partition + tuple(remaining_elements)


def edge_recombination(*parents: Tuple) -> Tuple:
    """Combine multiple chromosomes using edge recombination.

    http://www.rubicite.com/Tutorials/GeneticAlgorithms/CrossoverOperators/EdgeRecombinationCrossoverOperator.aspx

    :param parents: Chromosomes to combine.
    :return: Child chromosome.
    """
    return tuple(select_node(
        start_node=choice([chromosome[0] for chromosome in parents]),
        neighbors=construct_neighbors(*parents)
    ))


def cycle_crossover(parent_1: Tuple, parent_2: Tuple) -> Tuple[Tuple[Any, ...], ...]:
    """Combine two chromosomes using cycle crossover.

    http://www.rubicite.com/Tutorials/GeneticAlgorithms/CrossoverOperators/CycleCrossoverOperator.aspx

    :param parent_1: First parent.
    :param parent_2: Second parent.
    :return: Child chromosome.
    """
    cycles = identify_cycles(parent_1, parent_2)
    parity = cycle_parity(cycles=cycles)
    it_a, it_b = tee((b, a) if parity[i] else (a, b) for i, (a, b) in enumerate(zip(parent_1, parent_2)))
    yield tuple(x[0] for x in it_a)
    yield tuple(y[1] for y in it_b)
