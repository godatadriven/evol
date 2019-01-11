from pytest import mark
import sys

sys.path.append('.')

from examples.number_of_parents import run_evolutionary
from examples.rock_paper_scissors import run_rock_paper_scissors


N_WORKERS = [1, 2, None]


@mark.parametrize('concurrent_workers', N_WORKERS)
def test_number_of_parents(concurrent_workers):
    run_evolutionary(verbose=False, workers=concurrent_workers)


@mark.parametrize('concurrent_workers', N_WORKERS)
def test_rock_paper_scissors(concurrent_workers):
    run_rock_paper_scissors(silent=True, n_iterations=15, concurrent_workers=concurrent_workers)
