"""
Loggers help keep track of the workings of your evolutionary algorithm. By
default, each Population is initialized with a BaseLogger, which you can use
by using the .log() method of the population. If you want more complex
behaviour, you can supply another logger to the Population on initialisation.
"""
import datetime as dt
import os
import json
import logging
import sys
import uuid


class BaseLogger:
    """
    The `evol.BaseLogger` is the most basic logger in evol.
    You can supply it to a population so that the population
    knows how to handle the `.log()` verb.
    """
    def __init__(self, target=None, stdout=False, fmt='%(asctime)s,%(message)s'):
        self.file = target
        if target is not None:
            if not os.path.exists(os.path.split(target)[0]):
                raise RuntimeError(f"path to target {os.path.split(target)[0]} does not exist!")
        formatter = logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger(name=f"{uuid.uuid4()}")
        if not self.logger.handlers:
            # we do this extra step because loggers can behave in strange ways otherwise
            # https://navaspot.wordpress.com/2015/09/22/same-log-messages-multiple-times-in-python-issue/
            if target:
                file_handler = logging.FileHandler(filename=target)
                file_handler.setFormatter(fmt=formatter)
                self.logger.addHandler(file_handler)
            if stdout:
                stream_handler = logging.StreamHandler(stream=sys.stdout)
                stream_handler.setFormatter(fmt=formatter)
                self.logger.addHandler(stream_handler)
        self.logger.setLevel(level=logging.INFO)

    def log(self, population, **kwargs):
        """
        The logger method of the Logger object determines what will be logged.
        :param population: `evol.Population` object
        :return: nothing, it merely logs to a file and perhaps stdout
        """
        values = ','.join([str(item) for item in kwargs.values()])
        if values != '':
            values = f',{values}'
        for i in population:
            self.logger.info(f'{population.id},{i.id},{i.fitness}' + values)


class SummaryLogger(BaseLogger):
    """
    The `evol.SummaryLogger` merely logs statistics per population and nothing else.
    You are still able to log to stdout as well.
    """
    def log(self, population, **kwargs):
        values = ','.join([str(item) for item in kwargs.values()])
        if values != '':
            values = f',{values}'
        fitnesses = [i.fitness for i in population]
        self.logger.info(f'{min(fitnesses)},{sum(fitnesses)/len(fitnesses)},{max(fitnesses)}' + values)


class MultiLogger:
    """
    The `evol.Multilogger` is a logger object that can handle writing to two files.
    It is here for demonstration purposes to show how you could customize the logging.
    The only thing that matters is that all logging is handled by the `.log()`
    call. So we are free to record to multiple files if we want as well. This is
    not per se best practice but it would work.
    """
    def __init__(self, file_individuals, file_population):
        self.file_individuals = file_individuals
        self.file_population = file_population

    def log(self, population, **kwargs):
        """
        The logger method of the Logger object determines what will be logged.
        :param population: population to log
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
        """
        with open(self.file_population, 'a') as f:
            f.write(json.dumps(dict_to_log))
        with open(self.file_population, 'a') as f:
            f.writelines(ind_generator)
