import json


# TODO: решить вопрос с кодировкой пакета (, encoding: str = 'utf-8')
# TODO: инициализровать пакет заголовком и данными

class BasePackage:
    def __init__(self, headings: dict, data: str):
        self.headings = headings

        self.data = data

    @property
    def start(self):
        _start = self.headings.get('start', None)
        if _start is None:
            raise ValueError('Argument "start" is not passed')
        return _start

    @property
    def goal(self):
        _goal = self.headings.get('goal', None)
        if _goal is None:
            raise ValueError('Argument "goal" is not passed')
        return _goal

    @property
    def tol(self):
        _tol = self.headings.get('goal', float('inf'))
        return _tol

    @property
    def struct(self):
        return dict(self.headings, **{'data': self.data})

    @property
    def _headings(self):
        return json.dumps(self.headings)

    @property
    def _struct(self):
        return json.dumps(self.struct)

    @property
    def size(self):
        """
        Returns
        -------
        Размер пакета в байтах. Пакет рассматривается как строка в формате utf-8.
        """
        # return sys.getsizeof(self._struct)
        return len(self._struct) * 2 # потому что в utf-8 символ занимает 2 байта.

    @property
    def headings_size(self):
        """
        Returns
        -------
        Размер заголовков пакета в байтах. Пакет рассматривается как строка в формате utf-8.
        """
        return len(self._headings) * 2 # потому что в utf-8 символ занимает 2 байта

    @property
    def data_size(self):
        return self.size - self.headings_size

