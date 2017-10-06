from random import choice


def pick_random(parents, n_parents=2):
    return tuple(choice(parents) for _ in range(n_parents))
