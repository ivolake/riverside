import hashlib
import json
import math

from Packets import BasePacket
from additions import Representation

# TODO: реализовать хранение потока через генератор (???) (экономия памяти взамен на одноразовость сущности)


class BaseStream:
    def __init__(self,
                 message: str,
                 sender: str,
                 receiver: str,
                 packet_size: int = None,
                 packet_tol: int = None,
                 special: dict = None):
        self._id = str(id(self))

        self.message = message

        self._sender = sender
        self._receiver = receiver

        self._special = special



        if packet_tol is None:
            self._packet_tol = float('inf')
        else:
            self._packet_tol = packet_tol

        self.packets = [NotImplemented]

        self.__protocol = NotImplemented

        if packet_size is not None:
            self.packet_size = packet_size
        else:
            estimating_data_size = math.trunc(len(self.message)/ 50) + 1 # делим размер сообщения в байтах на 30

            self.packet_size = math.trunc((estimating_data_size + len(' "data": "",')) * 2 + self.pkt_headings_size) + 1

        self.pkt_data_len = self._pkt_data_len

    def __len__(self):
        return len(self.packets)

    def __repr__(self):
        return Representation(self, ['sender', 'receiver', 'packet_size', 'size', 'id'])()


    @property
    def id(self):
        return self._id

    @property
    def sender(self):
        return self._sender

    @property
    def receiver(self):
        return self._receiver

    @property
    def special(self):
        return self._special

    @property
    def packet_tol(self):
        return self._packet_tol

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
            raise ValueError(f'''Размер пакета слишком маленький ({r}). Он должен быть больше, чем {self.pkt_headings_size + 2 * len(' "data": "",') + 1}''')
        return r

    @property
    def size(self):
        return sum([pkt.size for pkt in self.packets])

    @property
    def message_hash(self):
        return hashlib.md5(self.message.encode('utf-8')).hexdigest()

    @property
    def protocol(self):
        return self.__protocol


    def pop(self, index):
        if len(self.packets) > 0:
            return self.packets.pop(index)
        else:
            return None

    def get_by_pid(self, pid: str):
        p = None
        i = 0
        while p is None and i < len(self):
            cp = self.packets[i]
            if cp.pid == pid:
                p = cp
            else:
                i += 1
        return p

    def get_by_id(self, id: str):
        p = None
        i = 0
        while p is None and i < len(self):
            cp = self.packets[i]
            if cp.id == id:
                p = cp
            else:
                i += 1
        return p



class TCPStream(BaseStream):
    def __init__(self, message: str, sender: str, receiver: str, packet_size: int = None, packet_tol: int = None, special: dict = None):
        super().__init__(message, sender, receiver, packet_size, packet_tol, special)

        self.packets = []

        self.__protocol = 'TCP'

        for n, i in enumerate(range(0, len(self.message), self.pkt_data_len)):
            headings = dict(self.pkt_headings, **{
                'pid': str(n),
                'received_answer': False,
                'sending_attempts': 0,
                'is_answer': False,
            })
            self.packets.append(
                BasePacket(headings=headings, data=self.message[i:i + self.pkt_data_len]))

    @property
    def protocol(self):
        return self.__protocol

    def __repr__(self):
        return Representation(self, ['sender', 'receiver', 'packet_size', 'size', 'id'])()

    @property
    def pkt_headings(self):
        return {
            'protocol': 'TCP',
            'sender': self.sender,
            'receiver': self.receiver,
            # 'travel_time': 0,
            'sid': self.id,
            'pid': 'None',
            # 'next_hop': 'None',
            # 'received_answer': False,
            'sending_attempts': 0,
            'is_answer': False,
            'is_copy': False,
            'tol': self.packet_tol,
        }

    def create_answer_to_packet(self, pkt):
        """

        Parameters
        ----------
        pid - pid пакета, для которого создается ответный пакет

        Returns
        -------

        """
        headings = {
            'protocol': 'TCP',
            'sender': self.receiver,
            'receiver': self.sender,
            'sid': self.id,
            'pid': pkt.pid,
            # 'next_hop': 'None',
            'is_answer': True,
        }
        pkt = BasePacket(headings=headings, data='')
        return pkt

class UDPStream(BaseStream):
    def __init__(self, message: str, sender: str, receiver: str, packet_size: int = None, packet_tol: int = None, special: dict = None):
        super().__init__(message, sender, receiver, packet_size, packet_tol, special)

        self.packets = []

        self.__protocol = 'UDP'

        for n, i in enumerate(range(0, len(self.message), self.pkt_data_len)):
            headings = dict(self.pkt_headings, **{
                'pid': str(n),
            })
            self.packets.append(
                BasePacket(headings=headings, data=self.message[i:i + self.pkt_data_len]))


    @property
    def protocol(self):
        return self.__protocol

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
            # 'next_hop': 'None',
            'tol': self.packet_tol,
        }
