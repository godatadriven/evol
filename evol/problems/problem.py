from abc import ABCMeta, abstractmethod


class Problem(metaclass=ABCMeta):

    @abstractmethod
    def eval_function(self, solution):
        raise NotImplementedError
