"""
python examples/example_pheromone.py
python examples/example_pheromone.py --population-size=35 --num-iter=1000
python examples/example_pheromone.py --population-size=100 --num-iter=1000
"""

import random
import math
import fire
import itertools as it
import matplotlib.pylab as plt

from evol import Population, Evolution


def run_pheromone(num_towns=42, population_size=100, num_iter=200, seed=42):
    """Runs a pheromone tactic against a simple TSP."""
    random.seed(seed)
    coordinates = [(random.random(), random.random()) for i in range(num_towns)]

    def init_func(num_towns):
        order = list(range(num_towns))
        random.shuffle(order)
        return order

    def dist(t1, t2):
        return math.sqrt((t1[0] - t2[0]) ** 2 + (t1[1] - t2[1]) ** 2)

    def eval_func(order):
        return sum([dist(coordinates[order[i]], coordinates[order[i - 1]]) for i, t in enumerate(order)])

    def sliding_window(iter):
        for i in range(len(iter) - 1):
            yield iter[i], iter[i+1]

    def pick_random(parents):
        return random.choice(parents), random.choice(parents)

    def partition(lst, n_crossover):
        division = len(lst) / n_crossover
        return [lst[round(division * i):round(division * (i + 1))] for i in range(n_crossover)]

    def crossover_ox(mom_order, dad_order, n_crossover=2):
        idx_split = partition(range(len(mom_order)), n_crossover=n_crossover)
        dad_idx = sum([list(d) for i, d in enumerate(idx_split) if i % 2 == 0], [])
        path = [-1 for _ in range(len(mom_order))]
        for idx in dad_idx:
            path[idx] = dad_order[idx]
        cities_visited = {p for p in path if p != -1}
        for i, d in enumerate(path):
            if d == -1:
                city = [p for p in mom_order if p not in cities_visited][0]
                path[i] = city
                cities_visited.add(city)
        return path

    def random_flip(chromosome):
        result = chromosome[:]
        idx1, idx2 = random.choices(list(range(len(chromosome))), k =2)
        result[idx1], result[idx2] = result[idx2], result[idx1]
        return result

    pop = Population(chromosomes=[init_func(num_towns) for _ in range(population_size)],
                     eval_function=eval_func, maximize=False).evaluate()

    evo = (
        Evolution()
            .survive(fraction=0.1)
            .breed(parent_picker=pick_random, combiner=crossover_ox)
            .mutate(random_flip)
            .evaluate()
    )

    scores = []
    iterations = []
    for iter in range(num_iter):
        print(f"iteration: {iter} best score: {min([individual.fitness for individual in pop])}")
        for indiviual in pop:
            scores.append(indiviual.fitness)
            iterations.append(iter)
        pop = evo.evolve(pop)

    plt.scatter(iterations, scores, s=1, alpha=0.3)
    plt.title("population fitness vs. iteration")
    plt.show()

if __name__ == "__main__":
    fire.Fire(run_pheromone)