from unittest import TestCase

from evol.helpers.utils import select_arguments


class TestSelectArguments(TestCase):

    def test_no_kwargs(self):
        @select_arguments
        def fct(*args):
            return sum(args)
        self.assertEqual(fct(4, 5), 9)
        self.assertEqual(fct(4, 5, z=1), 9)

    def test_with_kwargs(self):
        @select_arguments
        def fct(*args, z=0):
            return sum(args)+z
        self.assertEqual(fct(4, 5), 9)  # no kwargs
        self.assertEqual(fct(4, 5, z=1), 10)  # accepted kwargs
        self.assertEqual(fct(4, 5, z=1, y=2), 10)  # include non-accepted kwarg

    def test_all_kwargs(self):
        @select_arguments
        def fct(a, **kwargs):
            return sorted(list(kwargs.keys()))
        self.assertEqual(fct(a=1, b=2, c=3), ['b', 'c'])
