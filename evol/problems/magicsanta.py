import math
from typing import List, Union

from .problem import Problem
from evol.helpers._utils import flatten, sliding_window


class MagicSanta(Problem):
    def __init__(self, city_coordinates, home_coordinate, gift_weight=None, sleigh_weight=1):
        """
        This problem is based on this kaggle competition: https://www.kaggle.com/c/santas-stolen-sleigh#evaluation.
        :param distance_matrix:
        :param gift_weight:
        """
        self.city_coordinates = city_coordinates
        self.home_coordinate = home_coordinate
        self.gift_weight = gift_weight
        if gift_weight is None:
            self.gift_weight = [1 for _ in city_coordinates]
        self.sleigh_weight = sleigh_weight

        # calculate the distance matrix only once
        self.distance_matrix = [[0 for i in city_coordinates] for j in city_coordinates]
        for i, coord_i in enumerate(city_coordinates):
            for j, coord_j in enumerate(city_coordinates):
                dist = math.sqrt(sum([(z[0] - z[1]) ** 2 for z in zip(coord_i, coord_j)]))
                self.distance_matrix[i][j] = dist
                self.distance_matrix[j][i] = dist

    def check_solution(self, solution: List[List[int]]):
        """
        Check if the solution for the problem is valid.
        :param solution: List of lists containing integers representing visited cities.
        :return: None, unless errors are raised.
        """
        set_visited = set(flatten(solution))
        set_problem = set(range(len(self.city_coordinates)))
        if set_visited != set_problem:
            missing = set_problem.difference(set_visited)
            extra = set_visited.difference(set_problem)
            raise RuntimeError(f"Not all cities are visited! Missing: {missing} Extra: {extra}")

    def eval_function(self, solution: List[List[int]]) -> Union[float, int]:
        """
        Calculates the cost of the current solution for the TSP problem.
        :param solution: List of integers which refer to cities.
        :return:
        """
        self.check_solution(solution=solution)
        cost = 0
        for route in solution:
            total_route_weight = sum([self.gift_weight[t] for t in route]) + self.sleigh_weight
            cost += self.distance_matrix[0][route[0]] * total_route_weight
            for t1, t2 in sliding_window(route):
                total_route_weight -= self.gift_weight[t1]
                cost += self.distance_matrix[t1][t2] * total_route_weight
            cost += self.sleigh_weight * self.distance_matrix[route[-1]][0]
        return cost
