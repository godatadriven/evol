from random import shuffle
from typing import List

from evol import Individual
from evol.exceptions import PopulationIsNotEvaluatedException

"""
Below are functions that allocate individuals to the
island populations. It will be passed a list of individuals plus
the kwargs passed to this method, and must return a list of lists
of integers, each sub-list representing an island and the integers
representing the index of an individual in the list. Each island
must contain at least one individual, and individual may be copied
to multiple islands.
"""


def group_duplicate(individuals: List[Individual], n_groups: int = 4) -> List[List[int]]:
    """
    Group individuals into groups that each contain all individuals.

    :param individuals: List of individuals to group.
    :param n_groups: Number of groups to make.
    :return: List of lists of ints
    """
    return [list(range(len(individuals))) for _ in range(n_groups)]


def group_random(individuals: List[Individual], n_groups: int = 4) -> List[List[int]]:
    """
    Group individuals randomly into groups of roughly equal size.

    :param individuals: List of individuals to group.
    :param n_groups: Number of groups to make.
    :return: List of lists of ints
    """
    indexes = list(range(len(individuals)))
    shuffle(indexes)
    return [indexes[i::n_groups] for i in range(n_groups)]


def group_stratified(individuals: List[Individual], n_groups: int = 4) -> List[List[int]]:
    """
    Group individuals into groups of roughly equal size in a stratified manner.

    This function groups such that each group contains individuals of
    higher as well as lower fitness. This requires the individuals to have a fitness.

    :param individuals: List of individuals to group.
    :param n_groups: Number of groups to make.
    :return: List of lists of ints
    """
    _ensure_evaluated(individuals)
    indexes = list(map(
        lambda index_and_individual: index_and_individual[0],
        sorted(enumerate(individuals), key=lambda index_and_individual: index_and_individual[1].fitness)
    ))
    return [indexes[i::n_groups] for i in range(n_groups)]


def _ensure_evaluated(individuals: List[Individual]):
    """
    Helper function to ensure individuals are evaluated.

    :param individuals: List of individuals
    :raises RuntimeError: When at least one of the individuals is not evaluated.
    """
    for individual in individuals:
        if individual.fitness is None:
            raise PopulationIsNotEvaluatedException('Population must be evaluated.')
