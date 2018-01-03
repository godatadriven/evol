from collections import Counter
from random import choice, random, seed

import fire
import matplotlib.pylab as plt
import pandas as pd

from evol import Evolution, ContestPopulation
from evol.helpers.pickers import pick_random


class RockPaperScissorsPlayer:
    arbitrariness = 0.0
    elements = ('rock', 'paper', 'scissors')

    def __init__(self, preference=None):
        self.preference = preference if preference else choice(('rock', 'paper', 'scissors'))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.preference)

    def play(self):
        if random() >= self.arbitrariness:
            return self.preference
        else:
            return choice(('rock', 'paper', 'scissors'))

    def mutate(self, volatility=0.1):
        if random() < volatility:
            return self.__class__(choice(self.elements))
        else:
            return self.__class__(self.preference)

    def combine(self, other):
        return self.__class__(choice([self.preference, other.preference]))


def evaluation_func(player_1, player_2):
    choice_1, choice_2 = player_1.chromosome.play(), player_2.chromosome.play()
    if choice_1 == choice_2:
        return [0, 0]
    elif choice_1 == 'rock':
        return [-1, 1] if choice_2 == 'paper' else [1, -1]
    elif choice_1 == 'paper':
        return [-1, 1] if choice_2 == 'scissors' else [1, -1]
    else:
        return [-1, 1] if choice_2 == 'rock' else [1, -1]


def run_rock_paper_scissors(population_size=100, n_iterations=200, random_seed=42,
                            survive_fraction=0.90, arbitrariness=0.0):
    seed(random_seed)

    RockPaperScissorsPlayer.arbitrariness = arbitrariness

    pop = ContestPopulation(chromosomes=[RockPaperScissorsPlayer() for _ in range(population_size)],
                            eval_function=evaluation_func, maximize=True).evaluate()

    evo = (
        Evolution()
        .survive(fraction=survive_fraction)
        .breed(parent_picker=pick_random, combiner=lambda x, y: x.combine(y), n_parents=2)
        .mutate(lambda x: x.mutate())
        .evaluate()
    )

    preferences_over_time = []
    for _ in range(n_iterations):
        preferences = Counter()
        for individual in pop:
            preferences.update([individual.chromosome.preference])
        pop = pop.evolve(evo)
        preferences_over_time.append(preferences)

    ax = pd.DataFrame(preferences_over_time).fillna(0).plot(figsize=(10, 4))
    ax.set_ylim([0, population_size])
    ax.set_xlabel('iteration')
    ax.set_ylabel('# individuals with preference')
    plt.show()


if __name__ == "__main__":
    fire.Fire(run_rock_paper_scissors)
