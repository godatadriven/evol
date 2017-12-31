import datetime as dt
import os
import json
import logging
import sys


class BaseLogger():
    """
    The `evol.BaseLogger` is the most basic logger in evol. You can add it to a population
    so that the population knows how to handle the `.log()` verb. 
    """
    def __init__(self, file='/tmp/evol-logs.log', stdout=False):
        self.file = file
        if not os.path.exists(os.path.split(file)[0]):
            raise RuntimeError(f"path to file {os.path.split(file)[0]} does not exist!")
        handlers = [logging.FileHandler(filename=file)]
        if stdout:
            handlers.append(logging.StreamHandler(sys.stdout))
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s,%(message)s',
            handlers=handlers
        )
        self.logger = logging.getLogger(name='evol-base-logger')

    def log(self, population, **kwargs):
        """
        The logger method of the Logger object determines what will be logged. 
        :param population: `evol.Population` object
        :return: nothing, it merely logs to a file and perhaps stdout 
        """
        values = ','.join(kwargs.values())
        if values != '':
            values = ',{values}'
        for i in population:
            string = f'{population.id},{i.id},{i.fitness}' + values
            self.logger.debug(string)


class PopulationSummaryLogger(BaseLogger):
    """
    The `evol.PopulationSummaryLogger` merely logs statistics per population and nothing else. 
    You are still able to log to stdout as well. 
    """
    def log(self, population, **kwargs):
        fitnesses = [i.fitness for i in population]
        data = {
            'ts': str(dt.datetime.now()),
            'mean_ind': sum(fitnesses)/len(fitnesses),
            'min_ind': min(fitnesses),
            'max_ind': max(fitnesses)
        }
        dict_to_log = {**kwargs, **data}
        self.logger.debug(json.dumps(dict_to_log))


class MultiLogger():
    """
    The `evol.Multilogger` is a logger object that can handle writing to two files. 
    It is here for demonstration purposes to show how you could customize the logging. 
    The only thing that matters is that all logging is handled by the `.log()`
    call. So we are free to record to multiple files if we want as well. This is 
    not per se best practice but it would work. 
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

