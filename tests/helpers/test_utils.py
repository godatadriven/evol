from pytest import mark

from evol.helpers.utils import select_arguments, rotating_window, sliding_window
from evol import Individual, Population
from evol.helpers.pickers import pick_random
from evol.helpers.utils import select_arguments, offspring_generator


class TestOffspringGenerator:

    def test_simple_combiner(self, simple_population: Population):
        def combiner(x, y):
            return 1

        result = offspring_generator(parents=simple_population.individuals,
                                     parent_picker=pick_random, combiner=combiner)
        assert isinstance(next(result), Individual)
        assert next(result).chromosome == 1

    @mark.parametrize('n_parents', [1, 2, 3, 4])
    def test_args(self, n_parents: int, simple_population: Population):
        def combiner(*parents, n_parents):
            assert len(parents) == n_parents
            return 1

        result = offspring_generator(parents=simple_population.individuals, n_parents=n_parents,
                                     parent_picker=pick_random, combiner=combiner)
        assert isinstance(next(result), Individual)
        assert next(result).chromosome == 1

    def test_simple_picker(self, simple_population: Population):
        def combiner(x):
            return 1

        def picker(parents):
            return parents[0]

        result = offspring_generator(parents=simple_population.individuals, parent_picker=picker, combiner=combiner)
        assert isinstance(next(result), Individual)
        assert next(result).chromosome == 1

    def test_multiple_offspring(self, simple_population: Population):
        def combiner(x, y):
            yield 1
            yield 2

        result = offspring_generator(parents=simple_population.individuals,
                                     parent_picker=pick_random, combiner=combiner)
        for _ in range(10):
            assert next(result).chromosome == 1
            assert next(result).chromosome == 2


class TestSelectArguments:

    @mark.parametrize('args,kwargs,result', [((1, ), {}, 1), ((1, 2), {'x': 1}, 3), ((4, 5), {'z': 8}, 9)])
    def test_no_kwargs(self, args, kwargs, result):
        @select_arguments
        def fct(*args):
            return sum(args)
        assert fct(*args, **kwargs) == result

    @mark.parametrize('args,kwargs,result', [((1, ), {}, 1), ((1, 2), {'x': 1}, 3), ((4, 5), {'z': 8}, 17)])
    def test_with_kwargs(self, args, kwargs, result):
        @select_arguments
        def fct(*args, z=0):
            return sum(args)+z
        assert fct(*args, **kwargs) == result

    @mark.parametrize('args,kwargs,result', [((1,), {'b': 3}, 4), ((1, 2), {'x': 1}, 4), ((4, 5), {'z': 8}, 17)])
    def test_all_kwargs(self, args, kwargs, result):
        @select_arguments
        def fct(a, b=0, **kwargs):
            return a + b + sum(kwargs.values())
        assert fct(*args, **kwargs) == result


class TestSimpleUtilFunc:

    def test_sliding_window(self):
        assert list(sliding_window([1, 2, 3, 4])) == [(1, 2), (2, 3), (3, 4)]

    def test_rotating_window(self):
        assert list(rotating_window([1, 2, 3, 4])) == [(4, 1), (1, 2), (2, 3), (3, 4)]
