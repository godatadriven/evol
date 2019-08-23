from pytest import mark
import sys

sys.path.append('.')

from examples.number_of_parents import run_evolutionary  # noqa: E402
from examples.rock_paper_scissors import run_rock_paper_scissors  # noqa: E402
from examples.travelling_salesman import run_travelling_salesman  # noqa: E402


N_WORKERS = [1, 2, None]


@mark.parametrize('concurrent_workers', N_WORKERS)
def test_number_of_parents(concurrent_workers):
    run_evolutionary(verbose=False, workers=concurrent_workers)


@mark.parametrize('grouped', (False, True))
def test_rock_paper_scissors(grouped):
    history = run_rock_paper_scissors(silent=True, n_iterations=16, grouped=grouped)
    assert len(set(h['generation'] for h in history.history)) == 16


@mark.parametrize('n_groups', (1, 4))
def test_travelling_salesman(n_groups):
    run_travelling_salesman(concurrent_workers=2, n_groups=n_groups, n_iterations=4, silent=True)
