from evol.problems.functions import Rosenbrock, Sphere, Rastrigin


def test_rosenbrock_optimality():
    problem = Rosenbrock(size=2)
    assert problem.eval_function((1, 1)) == 0.0
    problem = Rosenbrock(size=5)
    assert problem.eval_function((1, 1, 1, 1, 1)) == 0.0


def test_sphere_optimality():
    problem = Sphere(size=2)
    assert problem.eval_function((0, 0)) == 0.0
    problem = Sphere(size=5)
    assert problem.eval_function((0, 0, 0, 0, 0)) == 0.0


def test_rastrigin_optimality():
    problem = Rastrigin(size=2)
    assert problem.eval_function((0, 0)) == 0.0
    problem = Rastrigin(size=5)
    assert problem.eval_function((0, 0, 0, 0, 0)) == 0.0
