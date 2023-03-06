import hashlib
import json
import copy


# TODO: решить вопрос с кодировкой пакета (, encoding: str = 'utf-8')

class BasePacket:
    def __init__(self, headings: dict, data: str):

        self.data = data.replace('\n', ' ').replace('\t', '    ').replace('\r', '')

        self.headings = headings

        self.struct = dict(self.headings, **{'data': self.data})

        self.__id = str(id(self))

        self.copy_id = None

    # def __eq__(self, other) -> bool:
    #     return self.struct == other.struct
    #
    # def __ne__(self, other) -> bool:
    #     return self.struct != other.struct
    #
    # def __gt__(self, other) -> bool:
    #     return self.size > other.size
    #
    # def __lt__(self, other) -> bool:
    #     return self.size < other.size
    #
    # def __ge__(self, other) -> bool:
    #     return self.size > other.size or self.struct == other.struct
    #
    # def __le__(self, other) -> bool:
    #     return self.size < other.size or self.struct == other.struct

    def __getattr__(self, item):
        return self.struct[item]


    def __repr__(self):
        return f'BasePacket(id: {self.id}, headings: {self.__headings})'


    @property
    def __headings(self):
        return json.dumps(self.headings, ensure_ascii=False)

    @property
    def __struct(self):
        return json.dumps(self.struct, ensure_ascii=False)

    @property
    def sid_pid(self):
        return f'{self.sid}.{self.pid}'

    @property
    def id(self):
        return self.__id

    @property
    def size(self):
        """
        Returns
        -------
        Размер пакета в байтах. Пакет рассматривается как строка в формате utf-8.
        """
        # return sys.getsizeof(self._struct)
        return len(self.__struct) * 2  # потому что в utf-8 символ занимает 2 байта.

    @property
    def headings_size(self):
        """
        Returns
        -------
        Размер заголовков пакета в байтах. Пакет рассматривается как строка в формате utf-8.
        """
        return len(self.__headings) * 2  # потому что в utf-8 символ занимает 2 байта

    @property
    def data_size(self):
        return self.size - self.headings_size

    @property
    def sending_attempts(self):
        return self.headings['sending_attempts']

    @sending_attempts.setter
    def sending_attempts(self, value):
        self.headings['sending_attempts'] = value

    @property
    def is_copy(self):
        return self.headings.get('is_copy', False)

    @is_copy.setter
    def is_copy(self, value):
        self.headings['is_copy'] = value

    def copy(self):
        # c = copy.deepcopy(self)
        h = dict(self.headings, **self.headings)
        d = str(self.data)
        c = BasePacket(headings=h, data=d)
        c.is_copy = True
        self.copy_id = c.id
        return c

