import math
from typing import Sequence

from evol.helpers.utils import sliding_window
from evol.problems.problem import Problem


class FunctionProblem(Problem):
    def __init__(self, size=2):
        self.size = size

    def check_solution(self, solution: Sequence[float]) -> Sequence[float]:
        if len(solution) > self.size:
            raise ValueError(f"{self.__class__.__name__} has size {self.size}, \
                               got solution of size: {len(solution)}")
        return solution

    def value(self, solution):
        return sum(solution)

    def eval_function(self, solution: Sequence[float]) -> float:
        self.check_solution(solution)
        return self.value(solution)


class Sphere(FunctionProblem):
    def value(self, solution: Sequence[float]) -> float:
        """
        The optimal value can be found when a sequence of zeros is given.
        :param solution: a sequence of x_i values
        :return: the value of the Sphere function
        """
        return sum([_**2 for _ in solution])


class Rosenbrock(FunctionProblem):
    def value(self, solution: Sequence[float]) -> float:
        """
        The optimal value can be found when a sequence of ones is given.
        :param solution: a sequence of x_i values
        :return: the value of the Rosenbrock function
        """
        result = 0
        for x_i, x_j in sliding_window(solution):
            result += 100*(x_j - x_i**2)**2 + (1 - x_i)**2
        return result


class Rastrigin(FunctionProblem):
    def value(self, solution: Sequence[float]) -> float:
        """
        The optimal value can be found when a sequence of zeros is given.
        :param solution: a sequence of x_i values
        :return: the value of the Rosenbrock function
        """
        return (10 * self.size) + sum([_**2 - 10 * math.cos(2*math.pi*_) for _ in solution])
