def select_min_fitness(*parents):
    return min(parents, key=lambda parent: parent.fitness)


def select_max_fitness(*parents):
    return max(parents, key=lambda parent: parent.fitness)
