#!/usr/bin/env python

from argparse import ArgumentParser
from collections import Counter
from random import choice, random, seed
from typing import List

from evol import Evolution, ContestPopulation
from evol.helpers.pickers import pick_random


class RockPaperScissorsPlayer:
    arbitrariness = 0.0
    elements = ('rock', 'paper', 'scissors')

    def __init__(self, preference=None):
        self.preference = preference if preference else choice(self.elements)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.preference)

    def play(self):
        if random() >= self.arbitrariness:
            return self.preference
        else:
            return choice(self.elements)

    def mutate(self, volatility=0.1):
        if random() < volatility:
            return self.__class__(choice(self.elements))
        else:
            return self.__class__(self.preference)

    def combine(self, other):
        return self.__class__(choice([self.preference, other.preference]))


class RockPaperScissorsLizardSpockPlayer(RockPaperScissorsPlayer):
    elements = ('rock', 'paper', 'scissors', 'lizard', 'spock')


COMBINATIONS = [
    ('scissors', 'paper'),
    ('paper', 'rock'),
    ('rock', 'scissors'),
    ('rock', 'lizard'),
    ('lizard', 'spock'),
    ('spock', 'scissors'),
    ('scissors', 'lizard'),
    ('lizard', 'paper'),
    ('paper', 'spock'),
    ('spock', 'rock'),
]


def evaluate(player_1: RockPaperScissorsPlayer, player_2: RockPaperScissorsPlayer) -> List[float]:
    choice_1, choice_2 = player_1.play(), player_2.play()
    player_choices = {choice_1, choice_2}
    if len(player_choices) == 1:
        return [0, 0]
    for combination in COMBINATIONS:
        if set(combination) == player_choices:
            return [1, -1] if choice_1 == combination[0] else [-1, 1]


class History:

    def __init__(self):
        self.history = []

    def log(self, population: ContestPopulation):
        preferences = Counter()
        for individual in population:
            preferences.update([individual.chromosome.preference])
        self.history.append(preferences)

    def plot(self):
        try:
            import pandas as pd
            import matplotlib.pylab as plt
            population_size = sum(self.history[0].values())
            fig, ax = plt.subplots()
            pd.DataFrame(self.history).fillna(0).plot(figsize=(10, 4), ax=ax)
            ax.set_ylim([0, population_size])
            ax.set_xlabel('iteration')
            ax.set_ylabel('# individuals with preference')
            plt.show()
        except ImportError:
            print("If you install matplotlib and pandas you will get a pretty plot.")


def run_rock_paper_scissors(population_size: int = 100,
                            n_iterations: int = 200,
                            random_seed: int = 42,
                            survive_fraction: float = 0.90,
                            arbitrariness: float = 0.0,
                            concurrent_workers: int = 1,
                            lizard_spock: bool = False,
                            silent: bool = False):
    seed(random_seed)

    RockPaperScissorsPlayer.arbitrariness = arbitrariness

    player_class = RockPaperScissorsLizardSpockPlayer if lizard_spock else RockPaperScissorsPlayer
    pop = ContestPopulation(chromosomes=[player_class() for _ in range(population_size)],
                            eval_function=evaluate, maximize=True,
                            concurrent_workers=concurrent_workers).evaluate()
    history = History()

    evo = (Evolution()
           .survive(fraction=survive_fraction)
           .breed(parent_picker=pick_random, combiner=lambda x, y: x.combine(y), n_parents=2)
           .mutate(lambda x: x.mutate())
           .evaluate()
           .callback(history.log))

    pop.evolve(evo, n=n_iterations)

    if silent:
        return
    history.plot()


def parse_arguments():
    parser = ArgumentParser(description='Run the rock-paper-scissors example.')
    parser.add_argument('--population-size', dest='population_size', type=int, default=100,
                        help='the number of candidates to start the algorithm with')
    parser.add_argument('--n-iterations', dest='n_iterations', type=int, default=200,
                        help='the number of iterations to run')
    parser.add_argument('--random-seed', dest='random_seed', type=int, default=42,
                        help='the random seed to set')
    parser.add_argument('--survive-fraction', dest='survive_fraction', type=float, default=0.9,
                        help='the fraction of the population to survive each iteration')
    parser.add_argument('--arbitrariness', type=float, default=0.0,
                        help='arbitrariness of the players. if zero, player will always choose its preference')
    parser.add_argument('--concurrent_workers', type=int, default=None,
                        help='Concurrent workers to use to evaluate the population.')
    parser.add_argument('--lizard-spock', action='store_true', default=False,
                        help='Play rock-paper-scissors-lizard-spock.')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    run_rock_paper_scissors(**args.__dict__)
