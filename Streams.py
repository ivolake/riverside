import json

from Packages import BasePackage

# TODO: Поток составляется из сообщения, и сам разбивается на пакетики. Мы зададим либо количество пакетов в потоке,
#  либо размер единичного пакета

# TODO: реализовать хранение потока через генератор (???) (экономия памяти взамен на одноразовость сущности)

# TODO SOLVE_BUG: package_size и настоящий размер пакектов не совпадают


class BaseStream:
    def __init__(self, start: str, goal: str, message: str, package_size: int, package_tol: int = None):
        self.start = start
        self.goal = goal

        self.message = message
        self.package_size = package_size

        if package_tol is None:
            self.package_tol = float('inf')
        else:
            self.package_tol = package_tol

    @property
    def headings(self):
        return {
            'start': self.start,
            'goal': self.goal,
            'tol': self.package_tol,
        }

    @property
    def _headings(self):
        return json.dumps(self.headings)

    @property
    def headings_size(self):
        """
        Returns
        -------
        Размер заголовков пакета в байтах. Пакет рассматривается как строка в формате utf-8.
        """
        return len(self._headings) * 2 # потому что в utf-8 символ занимает 2 байта

    @property
    def _package_data_len(self):
        return int((self.package_size - self.headings_size) / 2)

    @property
    def packages(self):
        res = []
        for i in range(0, len(self.message), self._package_data_len):
            res.append(BasePackage(headings=self.headings, data=self.message[i:i + self._package_data_len]))
        return res

    def __len__(self):
        return len(self.packages)

    def size(self):
        return sum([pkg.size for pkg in self.packages])