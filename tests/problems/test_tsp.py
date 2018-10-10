import math
import pytest
from evol.problems.tsp import TSPProblem


class TestTsp:

    def test_distance_func(self):
        distances = TSPProblem.calc_distance_matrix([(0,0), (0,1), (1,0), (1,1)])
        assert distances[0][0] == 0
        assert distances[1][0] == 1
        assert distances[0][1] == 1
        assert distances[1][1] == 0
        assert distances[0][2] == 1
        assert distances[0][3] == math.sqrt(2)

    def test_score_method(self):
        distances = TSPProblem.calc_distance_matrix([(0,0), (0,1), (1,0), (1,1)])
        problem = TSPProblem(distance_matrix=distances)
        assert problem.eval_function([0,1,2,3]) == 1 + math.sqrt(2) + 1 + math.sqrt(2)

    def test_score_method_can_error(self):
        distances = TSPProblem.calc_distance_matrix([(0,0), (0,1), (1,0), (1,1)])
        problem = TSPProblem(distance_matrix=distances)

        with pytest.raises(RuntimeError) as execinfo1:
            problem.eval_function([0,1,2,3,4])
        assert "Solution is longer than number of towns" in str(execinfo1.value)

        with pytest.raises(RuntimeError) as execinfo2:
            problem.eval_function([0,1,2])
        assert "3" in str(execinfo2.value)
        assert "missing" in str(execinfo2.value)

        with pytest.raises(RuntimeError) as execinfo3:
            problem.eval_function([0,1,2,2])
        assert "3" in str(execinfo3.value)
        assert "missing" in str(execinfo3.value)
