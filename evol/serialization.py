import json
import pickle
from datetime import datetime
from typing import List

from os import listdir
from os.path import isdir, exists, join

from evol import Individual


def checkpoint(individuals: List[Individual], directory: str, method: str='pickle') -> None:
    """Checkpoint a list of individuals.

    :param individuals: List of individuals to checkpoint.
    :param directory: Location to store the checkpoint. A new file is created for every checkpoint.
    :param method: One of "pickle" or "json". For json, the chromosomes need to be json-serializable.
    """
    if not isdir(directory):
        raise FileNotFoundError('Cannot write to "{}": is not a directory.'.format(directory))
    filename = join(directory,
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


def load(path: str) -> List[Individual]:
    """Load a checkpoint.

    If path is a file, load that file. If it is a directory, load the most recent checkpoint.
    The checkpoint file must end with a ".json" or "pkl" extension.

    :param path: Path to checkpoint directory or file.
    :return: List of individuals from checkpoint.
    """
    if not exists(path):
        raise FileNotFoundError('Cannot load "{}": does not exist.'.format(path))
    if isdir(path):
        try:
            path = join(path,
                        sorted(filter(lambda x: x.endswith('.pkl') or x.endswith('.json'), listdir(path=path)))[-1])
        except KeyError:
            raise FileNotFoundError('Cannot load from "{}": directory is empty.'.format(path))
    if path.endswith('.json'):
        with open(path, 'r') as json_file:
            return [Individual.from_dict(d) for d in json.load(json_file)]
    elif path.endswith('.pkl'):
        with open(path, 'rb') as pickle_file:
            return pickle.load(pickle_file)
    else:
        raise ValueError('Invalid extension "{}". Was expecting ".pkl" or ".json".'.format(path))
