#!/usr/bin/env python
from argparse import ArgumentParser
from math import sqrt
from random import random, seed, shuffle
from typing import List, Optional

from evol import Evolution, Population
from evol.helpers.combiners.permutation import cycle_crossover
from evol.helpers.groups import group_stratified
from evol.helpers.mutators.permutation import swap_elements
from evol.helpers.pickers import pick_random


def run_travelling_salesman(population_size: int = 100,
                            n_iterations: int = 10,
                            random_seed: int = 0,
                            n_destinations: int = 50,
                            concurrent_workers: Optional[int] = None,
                            n_groups: int = 4,
                            silent: bool = False):
    seed(random_seed)
    # Generate some destinations
    destinations = [(random(), random()) for _ in range(n_destinations)]

    # Given a list of destination indexes, this is our cost function
    def evaluate(ordered_destinations: List[int]) -> float:
        total = 0
        for x, y in zip(ordered_destinations, ordered_destinations[1:]):
            coordinates_x = destinations[x]
            coordinates_y = destinations[y]
            total += sqrt((coordinates_x[0] - coordinates_y[1])**2 + (coordinates_x[1] - coordinates_y[1])**2)
        return total

    # This generates a random solution
    def generate_solution() -> List[int]:
        indexes = list(range(n_destinations))
        shuffle(indexes)
        return indexes

    def print_function(population: Population):
        if population.generation % 5000 == 0 and not silent:
            print(f'{population.generation}: {population.documented_best.fitness:1.2f} / '
                  f'{population.current_best.fitness:1.2f}')

    pop = Population.generate(generate_solution, eval_function=evaluate, maximize=False,
                              size=population_size * n_groups, concurrent_workers=concurrent_workers)

    island_evo = (Evolution()
                  .survive(fraction=0.5)
                  .breed(parent_picker=pick_random(n_parents=2), combiner=cycle_crossover)
                  .mutate(swap_elements))

    evo = (Evolution()
           .evaluate(lazy=True)
           .callback(print_function)
           .repeat(evolution=island_evo, n=100, grouping_function=group_stratified, n_groups=n_groups))

    result = pop.evolve(evolution=evo, n=n_iterations)

    if not silent:
        print(f'Shortest route: {result.documented_best.chromosome}')
        print(f'Route length: {result.documented_best.fitness}')


def parse_arguments():
    parser = ArgumentParser(description='Run the travelling salesman example.')
    parser.add_argument('--population-size', type=int, default=100,
                        help='the number of candidates to start the algorithm with')
    parser.add_argument('--n-iterations', type=int, default=10,
                        help='the number of iterations to run')
    parser.add_argument('--random-seed', type=int, default=42,
                        help='the random seed to set')
    parser.add_argument('--n-destinations', type=int, default=50,
                        help='Number of destinations in the route.')
    parser.add_argument('--n-groups', type=int, default=4,
                        help='Number of groups to group by.')
    parser.add_argument('--concurrent-workers', type=int, default=None,
                        help='Concurrent workers to use to evaluate the population.')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    run_travelling_salesman(**args.__dict__)
