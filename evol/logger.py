import datetime as dt
import os
import json


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
        values = ','.join(kwargs.values())
        for i in population:
            string = f'{dt.datetime.now()},{population.id},{i.id},{i.fitness}' + values
            self.handle(string)

    def handle(self, item):
        """
        The handler method of the Logger object determines how it will be logged.
        In this case we print if there is no file and we append to a file otherwise.
        :return: 
        """
        if not self.file:
            print(item)
        else:
            with open(self.file, 'a') as f:
                f.write(item + '\n')


class PopulationSummaryLogger(BaseLogger):
    def log(self, population, **kwargs):
        fitnesses = [i.fitness for i in population]
        data = {
            'ts': str(dt.datetime.now()),
            'mean_ind': sum(fitnesses)/len(fitnesses),
            'min_ind': min(fitnesses),
            'max_ind': max(fitnesses)
        }
        dict_to_log = {**kwargs, **data}
        return self.handle([json.dumps(dict_to_log)])


class MultiLogger():
    """
    The only thing that matters is that all logging is handled by the `.log()`
    call. So we are free to record to multiple files if we want as well. 
    """
    def __init__(self, file_indidivuals, file_population):
        self.file_individuals = file_indidivuals
        self.file_population = file_population

    def log(self, population, **kwargs):
        """
        The logger method of the Logger object determines what will be logged. 
        :param population: 
        :return: generator of strings to be handled
        """
        ind_generator = (f'{dt.datetime.now()},{population.id},{i.id},{i.fitness}' for i in population)
        fitnesses = [i.fitness for i in population]
        data = {
            'ts': str(dt.datetime.now()),
            'mean_ind': sum(fitnesses) / len(fitnesses),
            'min_ind': min(fitnesses),
            'max_ind': max(fitnesses)
        }
        dict_to_log = {**kwargs, **data}
        self.handle(ind_generator, dict_to_log)

    def handle(self, ind_generator, dict_to_log):
        """
        The handler method of the Logger object determines how it will be logged.
        In this case we print if there is no file and we append to a file otherwise.
        :return: 
        """
        with open(self.file_population, 'a') as f:
            f.write(json.dumps(dict_to_log))
        with open(self.file_population, 'a') as f:
            f.writelines(ind_generator)

