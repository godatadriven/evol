"""
python examples/example_evolutionary_01.py --help
python examples/example_evolutionary_01.py --num_towns 100
python examples/example_evolutionary_01.py --num_iter 200 --population_size 200
python examples/example_evolutionary_01.py --seed 43
"""

import random
import math
import argparse

from evol import Population, Evolution


def run_evolutionary(num_towns=42, population_size=100, num_iter=200, seed=42):
    """
    Runs a simple evolutionary algorithm against a simple TSP problem.
    The goal is to explain the `evol` library, this is not an algorithm
    that should perform well.
    """

    # First we generate random towns as candidates with a seed
    random.seed(seed)
    coordinates = [(random.random(), random.random()) for i in range(num_towns)]

    # Next we define a few functions that we will need in order to create an algorithm.
    # Think of these functions as if they are lego blocks.
    def init_func(num_towns):
        """
        This function generates an individual  
        """
        order = list(range(num_towns))
        random.shuffle(order)
        return order

    def dist(t1, t2):
        """
        Calculates the distance between two towns. 
        """
        return math.sqrt((t1[0] - t2[0]) ** 2 + (t1[1] - t2[1]) ** 2)

    def eval_func(order):
        """
        Evaluates a candidate chromosome, which is a list that represents town orders.
        """
        return sum([dist(coordinates[order[i]], coordinates[order[i - 1]]) for i, t in enumerate(order)])

    def sliding_window(iter):
        """
        This is a helper function that creates a sliding window over towns. 
        Example: sliding_window([4,3,2,1]) -> [(4,3), (3,2), (2,1)]
        """
        for i in range(len(iter) - 1):
            yield iter[i], iter[i+1]

    def pick_random(parents):
        """
        This function selects two parents  
        """
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

    print("will start the evolutionary program")
    scores = []
    iterations = []
    for i in range(num_iter):
        print(f"iteration: {i} best score: {min([individual.fitness for individual in pop])}")
        for indiviual in pop:
            scores.append(indiviual.fitness)
            iterations.append(i)
        pop = evo.evolve(pop)

    try:
        import matplotlib.pylab as plt
        plt.scatter(iterations, scores, s=1, alpha=0.3)
        plt.title("population fitness vs. iteration")
        plt.show()
    except ImportError:
        print("If you install matplotlib you will get a pretty plot.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run an example evol algorithm against a simple TSP problem.')
    parser.add_argument('--num_towns', type=int, default=42,
                        help='the number of towns to generate for the TSP problem')
    parser.add_argument('--population_size', type=int, default=100,
                        help='the number of candidates to start the algorithm with')
    parser.add_argument('--num_iter', type=int, default=100,
                        help='the number of evolutionary cycles to run')
    parser.add_argument('--seed', type=int, default=42,
                        help='the random seed for all this')

    args = parser.parse_args()
    print(f"i am aware of these arguments: {args}")
    run_evolutionary(num_towns=args.num_towns, population_size=args.population_size,
                     num_iter=args.num_iter, seed=args.seed)