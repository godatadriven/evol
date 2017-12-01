from ._utils import select_node, construct_neighbors
from random import choice


def edge_recombination(*chromosomes: tuple) -> tuple:
    """Combine multiple chromosomes using edge recombination.

    http://www.rubicite.com/Tutorials/GeneticAlgorithms/CrossoverOperators/EdgeRecombinationCrossoverOperator.aspx

    :param chromosomes: Chromosomes to combine.
    :return: New chromosome.
    """
    return tuple(select_node(
        start_node=choice([chromosome[0] for chromosome in chromosomes]),
        neighbors=construct_neighbors(*chromosomes)
    ))
