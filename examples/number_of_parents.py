"""
There are a few worthwhile things to notice in this example:

1. you can pass hyperparams into functions from the `.breed` and `.mutate` step
2. the algorithm does not care how many parents it will use in the `breed` step
"""

import random
import math
import argparse

from evol import Population, Evolution


def run_evolutionary(opt_value=1, population_size=100, n_parents=2, workers=1,
                     num_iter=200, survival=0.5, noise=0.1, seed=42, verbose=True):
    random.seed(seed)

    def init_func():
        return (random.random() - 0.5) * 20 + 10

    def eval_func(x, opt_value=opt_value):
        return -((x - opt_value) ** 2) + math.cos(x - opt_value)

    def random_parent_picker(pop):
        return [random.choice(pop) for i in range(n_parents)]

    def mean_parents(*parents):
        return sum(parents) / len(parents)

    def add_noise(chromosome, sigma):
        return chromosome + (random.random() - 0.5) * sigma

    pop = Population(chromosomes=[init_func() for _ in range(population_size)],
                     eval_function=eval_func, maximize=True, concurrent_workers=workers).evaluate()

    evo = (Evolution()
           .survive(fraction=survival)
           .breed(parent_picker=random_parent_picker, combiner=mean_parents)
           .mutate(mutate_function=add_noise, sigma=noise)
           .evaluate())

    for i in range(num_iter):
        pop = pop.evolve(evo)

    if verbose:
        print(f"iteration:{i} best: {pop.current_best.fitness} worst: {pop.current_worst.fitness}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run an example evol algorithm against a simple continuous function.')
    parser.add_argument('--opt-value', type=int, default=0,
                        help='the true optimal value of the problem')
    parser.add_argument('--population-size', type=int, default=20,
                        help='the number of candidates to start the algorithm with')
    parser.add_argument('--n-parents', type=int, default=2,
                        help='the number of parents the algorithm with use to generate new indivuals')
    parser.add_argument('--num-iter', type=int, default=20,
                        help='the number of evolutionary cycles to run')
    parser.add_argument('--survival', type=float, default=0.7,
                        help='the fraction of individuals who will survive a generation')
    parser.add_argument('--noise', type=float, default=0.5,
                        help='the amount of noise the mutate step will add to each individual')
    parser.add_argument('--seed', type=int, default=42,
                        help='the random seed for all this')
    parser.add_argument('--workers', type=int, default=1,
                        help='the number of workers to run the command in')

    args = parser.parse_args()
    run_evolutionary(opt_value=args.opt_value, population_size=args.population_size,
                     n_parents=args.n_parents, num_iter=args.num_iter,
                     noise=args.noise, seed=args.seed, workers=args.workers)
