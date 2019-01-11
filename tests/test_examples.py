from pytest import mark

from examples.number_of_parents import run_evolutionary
from examples.rock_paper_scissors import run_rock_paper_scissors


@mark.parametrize('concurrent_workers', [1, 2])
def test_number_of_parents(concurrent_workers):
    run_evolutionary(verbose=False, workers=concurrent_workers)


@mark.parametrize('concurrent_workers', [1, 2])
def test_rock_paper_scissors(concurrent_workers):
    run_rock_paper_scissors(silent=True, n_iterations=15, concurrent_workers=concurrent_workers)
