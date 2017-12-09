from abc import ABCMeta, abstractmethod


class PopulationBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def _add(self):
        pass

    @abstractmethod
    def evaluate(self, lazy: bool):
        pass

    @abstractmethod
    def apply(self, func, **kwargs):
        pass

    @abstractmethod
    def filter(self, func, **kwargs):
        pass

    @abstractmethod
    def map(self, func, **kwargs):
        pass

    @abstractmethod
    def survive(self, fraction, n, luck):
        pass

    @abstractmethod
    def breed(self, parent_picker, combiner, population_size=None, **kwargs):
        pass

    @abstractmethod
    def mutate(self, func, probability=1.0, **kwargs):
        pass

    @abstractmethod
    def duplicate(self, n_islands):
        pass

    @abstractmethod
    def split(self, n_islands):
        pass

    @abstractmethod
    def join(self):
        pass
