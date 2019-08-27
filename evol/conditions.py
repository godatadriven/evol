from time import monotonic
from typing import Callable, Optional, TYPE_CHECKING

from evol.exceptions import StopEvolution

if TYPE_CHECKING:
    from evol.population import BasePopulation


class Condition:
    """Stop the evolution until a condition is no longer met.

    :param condition: A function that accepts a Population and returns a boolean.
        If the condition does not evaluate to True, then the evolution is stopped.
    """
    conditions = set()

    def __init__(self, condition: Optional[Callable[['BasePopulation'], bool]]):
        self.condition = condition

    def __enter__(self):
        self.conditions.add(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conditions.remove(self)

    def __call__(self, population: 'BasePopulation') -> None:
        if self.condition and not self.condition(population):
            raise StopEvolution()

    @classmethod
    def check(cls, population: 'BasePopulation'):
        for condition in cls.conditions:
            condition(population)


class MinimumProgress(Condition):
    """Stop the evolution if not enough progress is made.

    This condition stops the evolution if the best documented fitness
    does not improve enough within a given number of iterations.

    :param window: Number of iterations in which the minimum improvement must be made.
    :param change: Require more change in fitness than this value.
        Defaults to 0, meaning any change is good enough.
    """

    def __init__(self, window: int, change: float = 0):
        super().__init__(condition=None)
        self._history = []
        self.change = change
        self.window = window

    def __call__(self, population: 'BasePopulation') -> None:
        self._history = self._history[-self.window:]
        self._history.append(population.evaluate(lazy=True).documented_best.fitness)
        if len(self._history) > self.window and abs(self._history[0] - self._history[-1]) <= self.change:
            raise StopEvolution()


class TimeLimit(Condition):
    """Stop the evolution after a given amount of time.

    This condition stops the evolution after a given amount of time
    has elapsed. Note that the time is only checked between iterations.
    If your iterations take long, the evolution may potentially run
    for much longer than anticipated.

    :param seconds: The time in seconds that the evolution may run.
    """

    def __init__(self, seconds: float):
        super().__init__(condition=None)
        self.time = None
        self.seconds = seconds

    def __call__(self, population: 'BasePopulation'):
        if self.time is None:
            self.time = monotonic()
        elif monotonic() - self.time > self.seconds:
            raise StopEvolution()
