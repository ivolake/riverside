import hashlib
from typing import List

from Packets import BasePacket


# TODO: реализовать хранение потока через генератор (???) (экономия памяти взамен на одноразовость сущности)


import json

from Packets import BasePacket


# TODO: реализовать хранение потока через генератор (???) (экономия памяти взамен на одноразовость сущности)
from additions import Representation


class BaseStream:
    def __init__(self, sender: str, receiver: str, message: str, packet_size: int, packet_tol: int = None):
        self.sender = sender
        self.receiver = receiver

        self.id = id(self)

        self.message = message
        self.packet_size = packet_size

        if packet_tol is None:
            self.packet_tol = float('inf')
        else:
            self.packet_tol = packet_tol

        self.pkt_data_len = self._pkt_data_len

        self.packets = [NotImplemented]


    def __repr__(self):
        return Representation(self, ['sender', 'receiver', 'packet_size', 'size', 'id'])()

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
    def size(self):
        return sum([pkt.size for pkt in self.packets])

    @property
    def message_hash(self):
        return hashlib.md5(self.message.encode('utf-8')).hexdigest()


    def pop(self, index):
        return self.packets.pop(index)


class TCPStream(BaseStream):
    def __init__(self, sender: str, receiver: str, message: str, packet_size: int, packet_tol: int = None):
        super().__init__(sender, receiver, message, packet_size, packet_tol)

        self.packets = []

        for n, i in enumerate(range(0, len(self.message), self.pkt_data_len)):
            headings = dict(self.pkt_headings, **{
                'pid': n,
                'received_answer': False,
                'sending_attempts': 0,
                'is_answer': False,
            })
            self.packets.append(
                BasePacket(headings=headings, data=self.message[i:i + self.pkt_data_len]))

    def __repr__(self):
        return Representation(self, ['sender', 'receiver', 'packet_size', 'size', 'id'])()

    @property
    def pkt_headings(self):
        return {
            'protocol': 'TCP',
            'sender': self.sender,
            'receiver': self.receiver,
            'travel_time': 0,
            'sid': self.id,
            'pid': 'None',
            'hash': 'None',
            'next_hop': 'None',
            'received_answer': False,
            'sending_attempts': 0,
            'is_answer': False,
            'tol': self.packet_tol,
        }

    def create_answer_to_packet(self, pid: int):
        """

        Parameters
        ----------
        pid - id пакета, для которого создается ответный пакет

        Returns
        -------

        """
        headings = {
            'protocol': 'TCP',
            'sender': self.receiver,
            'receiver': self.sender,
            'sid': self.id,
            'parent_pid': pid,
            'hash': 'None',
            'next_hop': 'None',
            'is_answer': True,
        }
        pkt = BasePacket(headings=headings, data='')
        self.packets.append(pkt)
        return pkt

class UDPStream(BaseStream):
    def __init__(self, sender: str, receiver: str, message: str, packet_size: int, packet_tol: int = None):
        super().__init__(sender, receiver, message, packet_size, packet_tol)

        self.packets = []

        for n, i in enumerate(range(0, len(self.message), self.pkt_data_len)):
            headings = dict(self.pkt_headings, **{
                'pid': n,
            })
            self.packets.append(
                BasePacket(headings=headings, data=self.message[i:i + self.pkt_data_len]))


    def __repr__(self):
        return Representation(self, ['sender', 'receiver', 'packet_size', 'size', 'id'])()

    @property
    def pkt_headings(self):
        return {
            'protocol': 'UDP',
            'sender': self.sender,
            'receiver': self.receiver,
            'travel_time': 0,
            'sid': self.id,
            'pid': 'None',
            'hash': 'None',
            'next_hop': 'None',
            'tol': self.packet_tol,
        }
