from collections import Iterable
from operator import attrgetter
from typing import List


class Path(List):
    def __init__(self, path: List):
        if path is None:
            self.path = []
            self.start = None
            self.goal = None
        else:
            self.path = path
            self.start = path[0]
            self.goal = path[-1]

    def __len__(self):
        return len(self.path)

    def __setitem__(self, key, value):
        self.path[key] = value

    def __getitem__(self, item):
        return self.path[item]

    def __delitem__(self, key):
        del self.path[key]

    def __repr__(self):
        return f'{self.path}'

    def __contains__(self, item):
        return item in self.path

    def __add__(self, other: List):
        return self.path + other

    def __iadd__(self, other):
        return self.path + other

    def __mul__(self, other):
        return self.path * other

    def __imul__(self, other):
        return self.path * other

    def __iter__(self):
        return iter(self.path)

    def append(self, value):
        self.path.append(value)



class TNPath(Path):
    def __init__(self, path: List, time: float):
        super().__init__(path)
        if time is None:
            self.time = 0
        else:
            self.time = time

class PathCollection:
    def __init__(self, paths: Iterable[Path]):
        self.paths = paths

    def get_shortest(self):
        return min(self.paths, key=len)

class TNPathCollection:
    def __init__(self, paths: Iterable[TNPath]):
        self.paths = paths

    def get_fastest(self):
        return min(self.paths, key=attrgetter('time'))

    def get_shortest(self):
        return min(self.paths, key=len)
