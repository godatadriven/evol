"""
python example_annealing.py
python example_annealing.py --num-towns=40 --population-size=50 --num-iter=1000 --start-temperature=50
"""

import random
import math
import fire
import matplotlib.pylab as plt

from evol import Population


def run_annealing(num_towns=21, population_size=100, num_iter=1000, start_temperature=100, decay=0.99, seed=42):
    """Runs a simulated annealing on a simple TSP."""
    num_towns = num_towns
    coordinates = [(random.random(), random.random()) for i in range(num_towns)]
    random.seed(seed)
    temperature = start_temperature

    def init_func():
        order = list(range(num_towns))
        random.shuffle(order)
        return order

    def eval_func(order):
        return sum([dist(coordinates[order[i]], coordinates[order[i - 1]]) for i, t in enumerate(order)])

    def dist(t1, t2):
        return math.sqrt((t1[0] - t2[0]) ** 2 + (t1[1] - t2[1]) ** 2)

    def accept_prob(score_old, score_new, temperature):
        return math.exp((score_old - score_new) / temperature)

    def anneal(order, temperature):
        t1, t2 = random.choice(range(len(order))), random.choice(range(len(order)))
        new_order = order[:]
        new_order[t1], new_order[t2] = order[t2], order[t1]
        orig_score, new_score = eval_func(order), eval_func(new_order)
        if accept_prob(orig_score, new_score, temperature) > random.random():
            return new_order
        return order

    pop = Population(init_function=init_func,
                     eval_function=eval_func,
                     size=population_size, maximize=False).evaluate()

    scores = []
    temperatures = []
    for iter in range(num_iter):
        pop.mutate(anneal, temperature=temperature).evaluate()
        for indiviual in pop:
            scores.append(indiviual.fitness)
            temperatures.append(iter)
        print(f"iteration: {iter} temperature: {temperature} score:{min([i.fitness for i in pop])}")
        temperature = temperature * decay

    plt.scatter(temperatures, scores, s=1, alpha=0.1)
    plt.title("population fitness vs. iteration")
    plt.show()

if __name__ == "__main__":
    fire.Fire(run_annealing)