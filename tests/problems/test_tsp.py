import math
import pytest
from evol.problems.routing.tsp import TSPProblem


def test_distance_func():
    problem = TSPProblem.from_coordinates([(0, 0), (0, 1), (1, 0), (1, 1)])
    assert problem.distance_matrix[0][0] == 0
    assert problem.distance_matrix[1][0] == 1
    assert problem.distance_matrix[0][1] == 1
    assert problem.distance_matrix[1][1] == 0
    assert problem.distance_matrix[0][2] == 1
    assert problem.distance_matrix[0][3] == pytest.approx(math.sqrt(2))


def test_score_method():
    problem = TSPProblem.from_coordinates([(0, 0), (0, 1), (1, 0), (1, 1)])
    expected = 1 + math.sqrt(2) + 1 + math.sqrt(2)
    assert problem.eval_function([0, 1, 2, 3]) == pytest.approx(expected)


def test_score_method_can_error():
    problem = TSPProblem.from_coordinates([(0, 0), (0, 1), (1, 0), (1, 1)])

    with pytest.raises(ValueError) as execinfo1:
        problem.eval_function([0, 1, 2, 3, 4])
    assert "Solution is longer than number of towns" in str(execinfo1.value)

    with pytest.raises(ValueError) as execinfo2:
        problem.eval_function([0, 1, 2])
    assert "3" in str(execinfo2.value)
    assert "missing" in str(execinfo2.value)

    with pytest.raises(ValueError) as execinfo3:
        problem.eval_function([0, 1, 2, 2])
    assert "3" in str(execinfo3.value)
    assert "missing" in str(execinfo3.value)
