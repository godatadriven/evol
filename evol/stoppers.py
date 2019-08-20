from abc import ABCMeta, abstractmethod
from typing import List

from evol.population import Population


class BaseStopper(metaclass=ABCMeta):

    @abstractmethod
    def __call__(self, population: Population) -> bool:
        pass

    def reset(self) -> None:
        pass


class NoProgressStopper(BaseStopper):
    """Stop the Evolution if progress has halted.

    This Stopper stops the evolution if the best documented fitness
    does not change for a given number of iterations.

    :param patience: The number of times the fitness must stay the
        same before stopping. Defaults to 1.
    """

    def __init__(self, patience: int = 1):
        self.patience = patience
        self._count = 0
        self._last = None

    def __call__(self, population: Population) -> bool:
        current = population.evaluate(lazy=True).documented_best.fitness
        if current == self._last:
            self._count += 1
        else:
            self._count = 0
        self._last = current
        return self._count >= self.patience

    def reset(self):
        self._count = 0
        self._last = None


class MinimumProgressStopper(BaseStopper):
    """Stop the Evolution if not enough progress is made.

    This Stopper stops the evolution if the best documented fitness
    does not change enough within a given number of iterations.

    :param minimum_change: The minimum improvement that must be achieved in order not to stop.
    :param window: Number of iterations in which the minimum improvement must be made.
    """

    def __init__(self, minimum_change: float, window: int):
        self.minimum_change = minimum_change
        self.window = window
        self._history: List[float] = []

    def __call__(self, population: Population) -> bool:
        self._history = self._history[-self.window:]
        self._history.append(population.evaluate(lazy=True).documented_best.fitness)
        return len(self._history) > self.window and abs(self._history[0] - self._history[-1]) <= self.minimum_change

    def reset(self):
        self._history = []
