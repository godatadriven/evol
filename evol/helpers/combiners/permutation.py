from itertools import tee
from random import choice
from typing import Any, Tuple

from ._utils import select_node, construct_neighbors, multiple_offspring, identify_cycles, cycle_parity


def edge_recombination(*parents: Tuple) -> Tuple:
    """Combine multiple chromosomes using edge recombination.

    http://www.rubicite.com/Tutorials/GeneticAlgorithms/CrossoverOperators/EdgeRecombinationCrossoverOperator.aspx

    :param parents: Chromosomes to combine.
    :return: New chromosome.
    """
    return tuple(select_node(
        start_node=choice([chromosome[0] for chromosome in parents]),
        neighbors=construct_neighbors(*parents)
    ))


@multiple_offspring
def cycle_crossover(parent_1: Tuple, parent_2: Tuple) -> Tuple[Tuple[Any, ...], ...]:
    """Combine two chromosomes using cycle crossover.

    http://www.rubicite.com/Tutorials/GeneticAlgorithms/CrossoverOperators/CycleCrossoverOperator.aspx

    :param parent_1: First parent.
    :param parent_2: Second parent.
    :return: Tuple of two child chromosomes.
    """
    cycles = identify_cycles(parent_1, parent_2)
    parity = cycle_parity(cycles=cycles)
    it_a, it_b = tee((b, a) if parity[i] else (a, b) for i, (a, b) in enumerate(zip(parent_1, parent_2)))
    return tuple(x[0] for x in it_a), tuple(y[1] for y in it_b)
