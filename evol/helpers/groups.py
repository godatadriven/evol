from typing import List

from evol import Individual


def group_duplicate(individuals: List[Individual], n_groups: int = 4) -> List[List[int]]:
    return [list(range(len(individuals))) for _ in range(n_groups)]


def group_random(individuals: List[Individual], n_groups: int = 4) -> List[List[int]]:
    # TODO: make random
    return [
        list(range(group, len(individuals), n_groups))
        for group in range(n_groups)
    ]
