import json
import pickle
from datetime import datetime
from typing import List, Union

from os import listdir
from os.path import isdir, exists, join

from evol import Individual


class SimpleSerializer:

    def __init__(self, target):
        """
        :param target: Location to store the checkpoints. A new file is created for every checkpoint.

        """
        self.target = target

    def checkpoint(self, individuals: List[Individual], target: Union[str, None]=None, method: str='pickle') -> None:
        """Checkpoint a list of individuals.

        :param individuals: List of individuals to checkpoint.
        :param target: Directory to write checkpoint to. If None, take Serializer default target, if any.
        :param method: One of "pickle" or "json". For json, the chromosomes need to be json-serializable.
        """
        filename = self._new_checkpoint_file(target=self.target if target is None else target, method=method)
        if method == 'pickle':
            with open(filename, 'wb') as pickle_file:
                pickle.dump(individuals, pickle_file)
        elif method == 'json':
            with open(filename, 'w') as json_file:
                json.dump([individual.__dict__ for individual in individuals], json_file)
        else:
            raise ValueError('Invalid checkpointing method "{}". Choose "pickle" or "json".'.format(method))

    def load(self, target: Union[str, None]=None) -> List[Individual]:
        """Load a checkpoint.

        If path is a file, load that file. If it is a directory, load the most recent checkpoint.
        The checkpoint file must end with a ".json" or "pkl" extension.

        :param target: Path to checkpoint directory or file.
        :return: List of individuals from checkpoint.
        """
        filename = self._find_checkpoint(self.target if target is None else target)
        if filename.endswith('.json'):
            with open(filename, 'r') as json_file:
                return [Individual.from_dict(d) for d in json.load(json_file)]
        elif filename.endswith('.pkl'):
            with open(filename, 'rb') as pickle_file:
                return pickle.load(pickle_file)

    @staticmethod
    def _new_checkpoint_file(target: str, method: str):
        """Generate a filename for a new checkpoint."""
        if target is None:
            raise ValueError('Serializer requires a target to checkpoint to.')
        if not isdir(target):
            raise FileNotFoundError('Cannot checkpoint to "{}": is not a directory.'.format(target))
        result = join(target, datetime.now().strftime("%Y%m%d-%H%M%S.%f") + ('.pkl' if method == 'pickle' else '.json'))
        if exists(result):
            raise FileExistsError('Cannot checkpoint to "{}": file exists.'.format(result))
        return result

    @classmethod
    def _find_checkpoint(cls, target: str):
        """Find the most recent checkpoint file."""
        if not exists(target):
            raise FileNotFoundError('Cannot load from "{}": file or directory does not exists.'.format(target))
        elif isdir(target):
            try:
                return join(target, max(filter(cls._has_valid_extension, listdir(path=target))))
            except ValueError:
                raise FileNotFoundError('Cannot load from "{}": directory contains no checkpoints.'.format(target))
        else:
            if not cls._has_valid_extension(target):
                raise ValueError('Invalid extension "{}": Was expecting ".pkl" or ".json".'.format(target))
            return target

    @staticmethod
    def _has_valid_extension(filename: str):
        """Check if a filename has a valid extension."""
        return filename.endswith('.pkl') or filename.endswith('.json')
