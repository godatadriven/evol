import math
from typing import List, Union

from .problem import Problem
from evol.helpers.utils import flatten, sliding_window


class MagicSanta(Problem):
    def __init__(self, city_coordinates, home_coordinate, gift_weight=None, sleigh_weight=1):
        """
        This problem is based on this kaggle competition: https://www.kaggle.com/c/santas-stolen-sleigh#evaluation.
        :param distance_matrix:
        :param gift_weight:
        """
        self.coordinates = city_coordinates
        self.home_coordinate = home_coordinate
        self.gift_weight = gift_weight
        if gift_weight is None:
            self.gift_weight = [1 for _ in city_coordinates]
        self.sleigh_weight = sleigh_weight

    @staticmethod
    def distance(coord_a, coord_b):
        return math.sqrt(sum([(z[0] - z[1]) ** 2 for z in zip(coord_a, coord_b)]))

    def check_solution(self, solution: List[List[int]]):
        """
        Check if the solution for the problem is valid.
        :param solution: List of lists containing integers representing visited cities.
        :return: None, unless errors are raised.
        """
        set_visited = set(flatten(solution))
        set_problem = set(range(len(self.coordinates)))
        if set_visited != set_problem:
            missing = set_problem.difference(set_visited)
            extra = set_visited.difference(set_problem)
            raise RuntimeError(f"Not all cities are visited! Missing: {missing} Extra: {extra}")
        visited_cities = []
        double_cities = []
        for route in solution:
            for city in route:
                if city in visited_cities:
                    double_cities.append(city)
                visited_cities.append(city)
        if double_cities:
            raise RuntimeError(f"Multiple occurrences found for cities: {set(double_cities)}")

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
            distance = self.distance(self.home_coordinate, self.coordinates[route[0]])
            cost += distance * total_route_weight
            for t1, t2 in sliding_window(route):
                total_route_weight -= self.gift_weight[t1]
                city1 = self.coordinates[t1]
                city2 = self.coordinates[t2]
                cost += self.distance(city1, city2) * total_route_weight
            last_leg_distance = self.distance(self.coordinates[route[-1]], self.home_coordinate)
            cost += self.sleigh_weight * last_leg_distance
        return cost
