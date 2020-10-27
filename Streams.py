import hashlib

from Packets import BasePacket


# TODO: реализовать хранение потока через генератор (???) (экономия памяти взамен на одноразовость сущности)


import json

from Packets import BasePacket


# TODO: реализовать хранение потока через генератор (???) (экономия памяти взамен на одноразовость сущности)


class BaseStream:
    def __init__(self, start: str, goal: str, message: str, packet_size: int, packet_tol: int = None):
        self.start = start
        self.goal = goal

        self.id = id(self)

        self.message = message
        self.packet_size = packet_size

        if packet_tol is None:
            self.packet_tol = float('inf')
        else:
            self.packet_tol = packet_tol

        self.pkt_data_len = self._pkt_data_len

    def __repr__(self):
        raise NotImplementedError

    def __len__(self):
        return len(self.packets)

    @property
    def pkt_headings(self):
        return NotImplementedError

    @property
    def _pkt_headings(self):
        return json.dumps(self.pkt_headings, ensure_ascii=False)

    @property
    def pkt_headings_size(self):
        """
        Returns
        -------
        Размер заголовков пакета в байтах. Пакет рассматривается как строка в формате utf-8.
        """
        return len(self._pkt_headings) * 2 # потому что в utf-8 символ занимает 2 байта

    @property
    def _pkt_data_len(self):
        r = int((self.packet_size - self.pkt_headings_size) / 2) - len(' "data": "",')
        if r <= 0:
            raise ValueError(f'''Packet size is too small. It must be greater, then {self.pkt_headings_size + 2 * len(' "data": "",') + 1}''')
        return r

    @property
    def packets(self):
        raise NotImplementedError

    @property
    def size(self):
        return sum([pkt.size for pkt in self.packets])

    @property
    def message_hash(self):
        return hashlib.md5(self.message.encode('utf-8')).hexdigest()


class ConsistentStream(BaseStream):
    def __init__(self, start: str, goal: str, message: str, packet_size: int, packet_tol: int = None):
        super().__init__(start, goal, message, packet_size, packet_tol)

    def __repr__(self):
        return f'ConsistentStream(' \
               f'start: {self.start}, ' \
               f'goal: {self.goal}, ' \
               f'packets_size: {self.packet_size}, ' \
               f'size: {self.size}, ' \
               f'id: {self.id})'

    @property
    def pkt_headings(self):
        return {
            'start': self.start,
            'goal': self.goal,
            'sid': self.id,
            'hash': 'None',
            'tol': self.packet_tol,
        }

    @property
    def packets(self):
        res = []
        for i in range(0, len(self.message), self.pkt_data_len):
            res.append(BasePacket(headings=self.pkt_headings, data=self.message[i:i + self.pkt_data_len]))
        return res

class SimultaneousStream(BaseStream):
    def __init__(self, start: str, goal: str, message: str, packet_size: int, packet_tol: int = None):
        super().__init__(start, goal, message, packet_size, packet_tol)

    def __repr__(self):
        return f'SimultaneousStream(' \
               f'start: {self.start}, ' \
               f'goal: {self.goal}, ' \
               f'packets_size: {self.packet_size}, ' \
               f'size: {self.size}, ' \
               f'id: {self.id})'

    @property
    def pkt_headings(self):
        return {
            'start': self.start,
            'goal': self.goal,
            'sid': self.id,
            'pid': 'None',
            'hash': 'None',
            'tol': self.packet_tol,
        }

    @property
    def packets(self):
        res = []
        for i in range(0, len(self.message), self.pkt_data_len):
            res.append(BasePacket(headings=dict(self.pkt_headings, **{'pid': i}), data=self.message[i:i + self.pkt_data_len]))
        return res
