import json
import pickle
from datetime import datetime
from typing import List

from os import listdir
from os.path import isdir, exists, join

from evol import Individual


class SimpleSerializer:

    def __init__(self, target):
        """
        :param target: Location to store the checkpoints. A new file is created for every checkpoint.

        """
        self.target = target

    def checkpoint(self, individuals: List[Individual], target: str=None, method: str='pickle') -> None:
        """Checkpoint a list of individuals.

        :param individuals: List of individuals to checkpoint.
        :param target: Directory to write checkpoint to. If None, take Serializer default target, if any.
        :param method: One of "pickle" or "json". For json, the chromosomes need to be json-serializable.
        """
        target = self.target if target is None else target
        if target is None:
            raise ValueError('Serializer requires a target')
        if not isdir(target):
            raise FileNotFoundError('Cannot write to "{}": is not a directory.'.format(target))
        filename = join(target,
                        datetime.now().strftime("%Y%m%d-%H%M%S.%f") + ('.pkl' if method == 'pickle' else '.json'))
        if exists(filename):
            raise FileExistsError('Cannot write to "{}": file exists!'.format(filename))
        if method == 'pickle':
            with open(filename, 'wb') as pickle_file:
                pickle.dump(individuals, pickle_file)
        elif method == 'json':
            with open(filename, 'w') as json_file:
                json.dump([individual.__dict__ for individual in individuals], json_file)
        else:
            raise ValueError('Invalid checkpointing method "{}". Choose "pickle" or "json".'.format(method))

    def load(self, target: str=None) -> List[Individual]:
        """Load a checkpoint.

        If path is a file, load that file. If it is a directory, load the most recent checkpoint.
        The checkpoint file must end with a ".json" or "pkl" extension.

        :param target: Path to checkpoint directory or file.
        :return: List of individuals from checkpoint.
        """
        target = self.target if target is None else target
        if not exists(target):
            raise FileNotFoundError('Cannot load "{}": does not exist.'.format(target))
        if isdir(target):
            try:
                target = join(target,
                              sorted(filter(lambda x: x.endswith('.pkl') or x.endswith('.json'),
                                            listdir(path=target)))[-1])
            except KeyError:
                raise FileNotFoundError('Cannot load from "{}": directory is empty.'.format(target))
        if target.endswith('.json'):
            with open(target, 'r') as json_file:
                return [Individual.from_dict(d) for d in json.load(json_file)]
        elif target.endswith('.pkl'):
            with open(target, 'rb') as pickle_file:
                return pickle.load(pickle_file)
        else:
            raise ValueError('Invalid extension "{}". Was expecting ".pkl" or ".json".'.format(target))
