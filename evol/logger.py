import datetime as dt
import os

class BaseLogger():
    def __init__(self, file=None):
        self.file = file
        if self.file is not None:
            if not os.path.exists(os.path.split(file)[0]):
                raise RuntimeError(f"path to file {os.path.split(file)[0]} does not exist!")

    def log(self, population, **kwargs):
        """
        The logger method of the Logger object determines what will be logged. 
        :param population: 
        :return: generator of strings to be handled
        """
        return (f'{dt.datetime.now()},{population.id},{i.id},{i.fitness},{i.chromosome}' for i in population)

    def handle(self, item, **kwargs):
        """
        The handler method of the Logger object determines how it will be logged.
        :return: 
        """
        if not self.file:
            print(item)
        else:
            with open(self.file, 'a') as f:
                f.write(item + '\n')
