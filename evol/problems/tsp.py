import math
from typing import List, Union

from .problem import Problem


def _rotating_window(arr):
    for i, city in enumerate(arr):
        yield arr[i-1], arr[i]


class TSPProblem(Problem):
    def __init__(self, distance_matrix):
        self.distance_matrix = distance_matrix

    @classmethod
    def calc_distance_matrix(cls, coordinates: List[Union[tuple, list]]) -> List[List[Union[int, float]]]:
        """
        Creates a distance matrix from a list of city coordinates.
        :param coordinates: An iterable that contains tuples or lists representing a x,y coordinate.
        :return: A list of lists containing the distances between cities.
        """
        res = [[0 for i in coordinates] for j in coordinates]
        for i, coord_i in enumerate(coordinates):
            for j, coord_j in enumerate(coordinates):
                dist = math.sqrt(sum([(z[0] - z[1])**2 for z in zip(coord_i, coord_j)]))
                res[i][j] = dist
                res[j][i] = dist
        return res

    def check_solution(self, solution: List[int]):
        """
        Check if the solution for the TSP problem is valid.
        :param solution: List of integers which refer to cities.
        :return: None, unless errors are raised.
        """
        set_solution = set(solution)
        set_problem = set(range(len(self.distance_matrix)))
        if len(solution) > len(self.distance_matrix):
            raise RuntimeError("Solution is longer than number of towns!")
        if set_solution != set_problem:
            raise RuntimeError(f"Not all towns are visited! Am missing {set_problem.difference(set_solution)}")

    def eval_function(self, solution: List[int]) -> Union[float, int]:
        """
        Calculates the cost of the current solution for the TSP problem.
        :param solution: List of integers which refer to cities.
        :return:
        """
        self.check_solution(solution=solution)
        cost = 0
        for t1, t2 in _rotating_window(solution):
            cost += self.distance_matrix[t1][t2]
        return cost


_usa_capital_coords = [(-86.279118, 32.361538), (-134.419740, 58.301935), (-112.073844, 33.448457),
                       (-92.331122, 34.736009), (-121.468926, 38.555605), (-104.984167, 39.7391667),
                       (-72.677, 41.767), (-75.526755, 39.161921), (-84.27277, 30.4518), (-84.39, 33.76),
                       (-157.826182, 21.30895), (-116.237651, 43.613739), (-89.650373, 39.783250),
                       (-86.147685, 39.790942), (-93.620866, 41.590939), (-95.69, 39.04),
                       (-84.86311, 38.197274), (-91.140229, 30.45809), (-69.765261, 44.323535),
                       (-76.501157, 38.972945), (-71.0275, 42.2352), (-84.5467, 42.7335), (-93.094, 44.95),
                       (-90.207, 32.320), (-92.189283, 38.572954), (-112.027031, 46.595805),
                       (-96.675345, 40.809868), (-119.753877, 39.160949), (-71.549127, 43.220093),
                       (-74.756138, 40.221741), (-105.964575, 35.667231), (-73.781339, 42.659829),
                       (-78.638, 35.771), (-100.779004, 48.813343), (-83.000647, 39.962245),
                       (-97.534994, 35.482309), (-123.029159, 44.931109), (-76.875613, 40.269789),
                       (-71.422132, 41.82355), (-81.035, 34.000), (-100.336378, 44.367966),
                       (-86.784, 36.165), (-97.75, 30.266667), (-111.892622, 40.7547),
                       (-72.57194, 44.26639), (-77.46, 37.54), (-122.893077, 47.042418),
                       (-81.633294, 38.349497), (-89.384444, 43.074722), (-104.802042, 41.145548)]

USATSP = TSPProblem(TSPProblem.calc_distance_matrix(_usa_capital_coords))