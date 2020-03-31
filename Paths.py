from collections import Iterable
from operator import attrgetter
from typing import List


class Path(List):
    """
    Type for paths
    """

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
        return Path(self.path + other)

    def __iadd__(self, other):
        return Path(self.path + other)

    def __mul__(self, other):
        return Path(self.path * other)

    def __imul__(self, other):
        return Path(self.path * other)

    def __eq__(self, other):
        return len(self.path) == len(other)

    def __ne__(self, other):
        return len(self.path) != len(other)

    def __gt__(self, other):
        return len(self.path) > len(other)

    def __lt__(self, other):
        return len(self.path) < len(other)

    def __ge__(self, other):
        return len(self.path) >= len(other)

    def __le__(self, other):
        return len(self.path) <= len(other)

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

    def __repr__(self):
        return f'{self.path},\n\ttime: {self.time:.3f}'


class PathCollection(List):
    def __init__(self, paths: List):
        self.paths = paths

    def __repr__(self):
        return '\n'.join([f'{i}: {path}' for i, path in enumerate(self.paths)])

    def __len__(self):
        return len(self.paths)

    def __setitem__(self, key, value):
        self.paths[key] = value

    def __getitem__(self, item):
        return self.paths[item]

    def __delitem__(self, key):
        del self.paths[key]

    def __contains__(self, item):
        return item in self.paths

    def __add__(self, other: List):
        return Path(self.paths + other)

    def __iadd__(self, other):
        return Path(self.paths + other)

    def __mul__(self, other):
        return Path(self.paths * other)

    def __imul__(self, other):
        return Path(self.paths * other)

    def __eq__(self, other):
        return len(self.paths) == len(other)

    def __ne__(self, other):
        return len(self.paths) != len(other)

    def __gt__(self, other):
        return len(self.paths) > len(other)

    def __lt__(self, other):
        return len(self.paths) < len(other)

    def __ge__(self, other):
        return len(self.paths) >= len(other)

    def __le__(self, other):
        return len(self.paths) <= len(other)

    def __iter__(self):
        return iter(self.paths)

    def append(self, value):
        self.paths.append(value)

    def index(self, item, start: int = ..., stop: int = ...) -> int:
        r = None
        for i, p in enumerate(self.paths):
            if item == p:
                r = i
        if r is None:
            raise ValueError(f'{item} is not in list')
        else:
            return r

    def get_shortest(self):
        return min(self.paths, key=len)


class TNPathCollection(PathCollection):
    def __init__(self, paths: List):
        super().__init__(paths)

    def get_fastest(self):
        return min(self.paths, key=attrgetter('time'))
