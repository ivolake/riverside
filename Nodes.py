import random

from NetworksSupport import RandomJitter
from Packets import BasePacket


class BaseNode:
    def __init__(self,
                 nodeid: str,
                 capacity: float,
                 processing_speed: float,
                 distortion_probability: float,
                 distortion_level: int,
                 **kwargs):
        self.id = nodeid
        self.capacity = capacity
        self.processing_speed = processing_speed
        self.distortion_probability = distortion_probability
        self.distortion_level = distortion_level

        _jitter_lowest_low = kwargs.get('jitter_lowest_low', 0)
        _jitter_highest_low = kwargs.get('jitter_highest_low', 4)
        _jitter_lowest_high = kwargs.get('jitter_lowest_high', 5)
        _jitter_highest_high = kwargs.get('jitter_highest_high', 7)

        self.jitter_f = RandomJitter(_jitter_lowest_low,
                                     _jitter_highest_low,
                                     _jitter_lowest_high,
                                     _jitter_highest_high, accuracy=5)

        self._queue = []  # еще не отправленные содержащиеся на узле пакеты
        self._awaiting_dict = {}  # место для тех пакетов, которые были отправлены, но чье прибытие на оконечный узел
                                  # еще не было подтверждено (используется только в TCP и только на стартовых узлах)
        self._successful_list = [] # список новых пакетов для этого узла (используется только в TCP и только на
                                   # оконечных узлах)

    @property
    def queue(self):
        return self._queue

    @property
    def awaiting_dict(self):
        return self._awaiting_dict

    def __repr__(self):
        return f'BaseNode(id={self.id}, capacity={self.capacity}, processing_speed={self.processing_speed}, ' \
               f'distortion_probability={self.distortion_probability}, distortion_level={self.distortion_level}, ' \
               f'jitter_f={self.jitter_f})'

    def add_to_queue(self, pkt: BasePacket):
        self._queue.append(pkt)

    def pop_from_queue(self):
        return self._queue.pop(0)

    def add_to_awaiting_dict(self, pkt: BasePacket):
        self._awaiting_dict.update({f'{pkt.headings["sid"]}.{pkt.headings["sid"]}': pkt})

    def pop_from_awaiting_dict(self, sid_pid: str):
        """

        Parameters
        ----------
        sid_pid - строка формата "sid.pid", чтобы найти пакет

        Returns
        -------

        """
        return self._awaiting_dict.pop(sid_pid)
