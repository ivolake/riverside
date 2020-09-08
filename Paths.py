from operator import attrgetter
from typing import List, Iterator


class Path(List):
    """
    Type for paths
    """

    def __init__(self, path: List) -> None:

        if path is None:
            self.path = []
            self.start = None
            self.goal = None
        else:
            self.path = path
            self.start = path[0]
            self.goal = path[-1]

    def __repr__(self) -> str:
        return f'{self.path}'

    def __len__(self) -> int:
        return len(self.path)

    def __setitem__(self, key: int, value: str) -> None:
        self.path[key] = value

    def __getitem__(self, key: int) -> str:
        return self.path[key]

    def __delitem__(self, key: int) -> None:
        del self.path[key]

    def __contains__(self, item: str) -> bool:
        return item in self.path

    def __add__(self, other):
        # return self.__class__(self.path + other)
        return Path(self.path + other)

    def __iadd__(self, other):
        # return self.__class__(self.path + other)
        return Path(self.path + other)

    def __mul__(self, other):
        # return self.__class__(self.path * other)
        return Path(self.path * other)

    def __imul__(self, other):
        # return self.__class__(self.path * other)
        return Path(self.path * other)

    def __eq__(self, other) -> bool:
        return len(self.path) == len(other)

    def __ne__(self, other) -> bool:
        return len(self.path) != len(other)

    def __gt__(self, other) -> bool:
        return len(self.path) > len(other)

    def __lt__(self, other) -> bool:
        return len(self.path) < len(other)

    def __ge__(self, other) -> bool:
        return len(self.path) >= len(other)

    def __le__(self, other) -> bool:
        return len(self.path) <= len(other)

    def __iter__(self) -> Iterator:
        return iter(self.path)

    def append(self, value: str) -> None:
        self.path.append(value)


class TNPath(Path):
    def __init__(self, path: List, time: float):
        Path.__init__(self, path)
        if time is None:
            self.time = 0
        else:
            self.time = time

    def __repr__(self):
        return f'{self.path},\n   time: {self.time:.3f}'

class MPath(Path):
    """
    Magnited Path - Path with magnitude
    """
    def __init__(self, path: List, i: int):
        Path.__init__(self, path)
        if i is None:
            self.i = 0
        else:
            self.i = i

    def __repr__(self):
        return f'{self.path},\n   i: {self.i}'

class TNMPath(MPath, TNPath):
    def __init__(self, path: List, i: int, time: float):
        MPath.__init__(self, path, i)
        TNPath.__init__(self, path, time)

    def __repr__(self):
        return f'{self.path},\n   i: {self.i},\n   time: {self.time:.3f}'


class PathCollection(List):
    def __init__(self, paths: List) -> None:
        self.paths = paths

    def __repr__(self) -> str:
        if len(self.paths) == 0:
            return 'Не обнаружено допустимых путей.'
        else:
            return '\n'.join([f'{i}: {path}' for i, path in enumerate(self.paths)])

    def __len__(self) -> int:
        return len(self.paths)

    def __setitem__(self, key: int, value: Path) -> None:
        self.paths[key] = value

    def __getitem__(self, key: int) -> Path:
        return self.paths[key]

    def __delitem__(self, key: int) -> None:
        del self.paths[key]

    def __contains__(self, item: Path) -> bool:
        return item in self.paths

    def __add__(self, other):
        return PathCollection(self.paths + other)

    def __iadd__(self, other):
        return PathCollection(self.paths + other)

    def __mul__(self, other):
        return PathCollection(self.paths * other)

    def __imul__(self, other):
        return PathCollection(self.paths * other)

    def __eq__(self, other) -> bool:
        return len(self.paths) == len(other)

    def __ne__(self, other) -> bool:
        return len(self.paths) != len(other)

    def __gt__(self, other) -> bool:
        return len(self.paths) > len(other)

    def __lt__(self, other) -> bool:
        return len(self.paths) < len(other)

    def __ge__(self, other) -> bool:
        return len(self.paths) >= len(other)

    def __le__(self, other) -> bool:
        return len(self.paths) <= len(other)

    def __iter__(self) -> Iterator:
        return iter(self.paths)

    def append(self, value: Path) -> None:
        self.paths.append(value)

    def index(self, item: Path, start: int = ..., stop: int = ...) -> int:
        r = None
        for i, p in enumerate(self.paths):
            if item == p:
                r = i
        if r is None:
            raise ValueError(f'{item} is not in list')
        else:
            return r

    def get_shortest(self) -> Path:
        return min(self.paths, key=len)

    def get_longest(self) -> Path:
        return max(self.paths, key=len)


class TNPathCollection(PathCollection):
    def __init__(self, paths: List):
        PathCollection.__init__(self, paths)

    def get_fastest(self) -> TNPath:
        return min(self.paths, key=attrgetter('time'))

    def get_slowest(self) -> TNPath:
        return max(self.paths, key=attrgetter('time'))

class MPathCollection(PathCollection):
    def __init__(self, paths: List):
        PathCollection.__init__(self, paths)

    def get_path_of_smallest_magnitude(self) -> TNMPath:
        return min(self.paths, key=attrgetter('i'))

    def get_path_of_biggest_magnitude(self) -> TNMPath:
        return max(self.paths, key=attrgetter('i'))

    def get_magnitudes_distribution(self):
        N = len(self.paths)
        magnitudes_distribution = dict()
        for path in self.paths:
            if path.i not in magnitudes_distribution.keys():
                magnitudes_distribution.update({path.i: 1})
            else:
                magnitudes_distribution[path.i] += 1

        for k in magnitudes_distribution:
            magnitudes_distribution[k] /= N

        return magnitudes_distribution

class TNMPathCollection(MPathCollection, TNPathCollection):
    def __init__(self, paths: List):
        MPathCollection.__init__(self, paths)
        TNPathCollection.__init__(self, paths)
