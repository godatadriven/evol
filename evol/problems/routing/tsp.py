import math
from typing import List, Union

from evol.problems.problem import Problem
from evol.helpers.utils import rotating_window


class TSPProblem(Problem):
    def __init__(self, distance_matrix):
        self.distance_matrix = distance_matrix

    @classmethod
    def from_coordinates(cls, coordinates: List[Union[tuple, list]]) -> 'TSPProblem':
        """
        Creates a distance matrix from a list of city coordinates.
        :param coordinates: An iterable that contains tuples or lists representing a x,y coordinate.
        :return: A list of lists containing the distances between cities.
        """
        res = [[0 for i in coordinates] for j in coordinates]
        for i, coord_i in enumerate(coordinates):
            for j, coord_j in enumerate(coordinates):
                dist = math.sqrt(sum([(z[0] - z[1])**2 for z in zip(coord_i[:2], coord_j[:2])]))
                res[i][j] = dist
                res[j][i] = dist
        return TSPProblem(distance_matrix=res)

    def check_solution(self, solution: List[int]):
        """
        Check if the solution for the TSP problem is valid.
        :param solution: List of integers which refer to cities.
        :return: None, unless errors are raised.
        """
        set_solution = set(solution)
        set_problem = set(range(len(self.distance_matrix)))
        if len(solution) > len(self.distance_matrix):
            raise ValueError("Solution is longer than number of towns!")
        if set_solution != set_problem:
            raise ValueError(f"Not all towns are visited! Am missing {set_problem.difference(set_solution)}")

    def eval_function(self, solution: List[int]) -> Union[float, int]:
        """
        Calculates the cost of the current solution for the TSP problem.
        :param solution: List of integers which refer to cities.
        :return:
        """
        self.check_solution(solution=solution)
        cost = 0
        for t1, t2 in rotating_window(solution):
            cost += self.distance_matrix[t1][t2]
        return cost
