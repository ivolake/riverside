from collections import Iterable
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
        return Path(self.path + other)

    def __iadd__(self, other):
        return Path(self.path + other)

    def __mul__(self, other):
        return Path(self.path * other)

    def __imul__(self, other):
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

    def append(self, value) -> None:
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
    def __init__(self, paths: List) -> None:
        self.paths = paths

    def __repr__(self) -> str:
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


class TNPathCollection(PathCollection):
    def __init__(self, paths: List):
        super().__init__(paths)

    def get_fastest(self) -> Path:
        return min(self.paths, key=attrgetter('time'))
