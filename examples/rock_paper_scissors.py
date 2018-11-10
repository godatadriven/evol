from argparse import ArgumentParser

from collections import Counter
from random import choice, random, seed

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

    evo = (Evolution()
           .survive(fraction=survive_fraction)
           .breed(parent_picker=pick_random, combiner=lambda x, y: x.combine(y), n_parents=2)
           .mutate(lambda x: x.mutate())
           .evaluate())

    preferences_over_time = []
    for _ in range(n_iterations):
        preferences = Counter()
        for individual in pop:
            preferences.update([individual.chromosome.preference])
        pop = pop.evolve(evo)
        preferences_over_time.append(preferences)

    try:
        import matplotlib.pylab as plt
        import pandas as pd
    except ImportError:
        print("If you install matplotlib and pandas you will get a pretty plot.")
        return
    ax = pd.DataFrame(preferences_over_time).fillna(0).plot(figsize=(10, 4))
    ax.set_ylim([0, population_size])
    ax.set_xlabel('iteration')
    ax.set_ylabel('# individuals with preference')
    plt.show()


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
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    run_rock_paper_scissors(**args.__dict__)
