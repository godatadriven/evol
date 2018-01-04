from pytest import mark

from evol.helpers.utils import select_arguments


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
