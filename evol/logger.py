import datetime as dt
import os

class BaseLogger():
    def __init__(self, file=None):
        self.file = file

    def log(self, population):
        """
        The logger method of the Logger object determines what will be logged. 
        :param population: 
        :return: 
        """
        return (f'{dt.datetime.now()},{population.id},{i.id},{i.fitness},{i.chromosome}' for i in population)

    def handle(self, item):
        """
        The handler method of the Logger object determines how it will be logged.
        :return: 
        """
        print(item)