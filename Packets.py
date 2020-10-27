import hashlib
import json


# TODO: решить вопрос с кодировкой пакета (, encoding: str = 'utf-8')
# TODO: инициализровать пакет заголовком и данными

class BasePacket:
    def __init__(self, headings: dict, data: str):
        self.data = data.replace('\n', ' ').replace('\t', '    ').replace('\r', '')

        self.headings = headings
        self.headings.update({'hash': self.hash})

        self.struct = dict(self.headings, **{'data': self.data})

    def __repr__(self):
        return f'BasePacket(headings: {self._headings})'

    @property
    def _headings(self):
        return json.dumps(self.headings, ensure_ascii=False)

    @property
    def _struct(self):
        return json.dumps(self.struct, ensure_ascii=False)

    @property
    def hash(self):
        return hashlib.md5(self.data.encode('utf-8')).hexdigest()

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

