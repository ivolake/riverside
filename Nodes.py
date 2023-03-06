import math
from collections import OrderedDict
import additions as adds
from Channels import BaseChannel

from NetworksSupport import RandomJitter
from Packets import BasePacket
from config import JITTER_LOWEST_lOW, JITTER_HIGHEST_LOW, JITTER_LOWEST_HIGH, JITTER_HIGHEST_HIGH, \
    DEFAULT_FILLED_SPACE_FACTOR_LOW, DEFAULT_FILLED_SPACE_FACTOR_HIGH, DEFAULT_FILLED_SPACE_FACTOR_PLATEAU, \
    DEFAULT_JITTER_ACCURACY


class BaseNode:
    def __init__(self,
                 node_id: str,
                 capacity: float,
                 processing_speed: float,
                 distortion_probability: float,
                 distortion_level: int,
                 **kwargs):
        self._id = node_id
        self._capacity = capacity
        self._processing_speed = processing_speed
        self._distortion_probability = distortion_probability
        self._distortion_level = distortion_level

        jitter_lowest_low = kwargs.get('jitter', {}).get('lowest_low', JITTER_LOWEST_lOW)
        jitter_highest_low = kwargs.get('jitter', {}).get('highest_low', JITTER_HIGHEST_LOW)
        jitter_lowest_high = kwargs.get('jitter', {}).get('lowest_high', JITTER_LOWEST_HIGH)
        jitter_highest_high = kwargs.get('jitter', {}).get('highest_high', JITTER_HIGHEST_HIGH)

        self._jitter_f = RandomJitter(jitter_lowest_low,
                                      jitter_highest_low,
                                      jitter_lowest_high,
                                      jitter_highest_high, accuracy=DEFAULT_JITTER_ACCURACY)

        self._filled_space_factor_low = kwargs.get('filled_space_factor', {}).get('low',
                                                                                  DEFAULT_FILLED_SPACE_FACTOR_LOW)
        self._filled_space_factor_high = kwargs.get('filled_space_factor', {}).get('high',
                                                                                   DEFAULT_FILLED_SPACE_FACTOR_HIGH)
        self._filled_space_factor_plateau = kwargs.get('filled_space_factor', {}).get('plateau',
                                                                                      DEFAULT_FILLED_SPACE_FACTOR_PLATEAU)

        self._queue = OrderedDict({})  # еще не отправленные содержащиеся на узле пакеты (хранение в виде {pkt.id: pkt})
        self._awaiting = OrderedDict(
            {})  # хранилище тех пакетов, которые были отправлены, но чье прибытие на оконечный узел
        # еще не было подтверждено (используется только в TCP и только на стартовых узлах)
        self._successful = OrderedDict(
            {})  # хранилище новых пакетов для этого узла (используется только в TCP и только на
        # оконечных узлах)

        self.init_channel: BaseChannel = ...

        self._incoming_channels: dict[str: BaseChannel] = {}
        self._outgoing_channels: dict[str: BaseChannel] = {}

    def __repr__(self):
        return f'BaseNode(id={self.id}, capacity={self.capacity} ({self.filled_space_relative * 100}% filled), processing_speed={self.processing_speed}, ' \
               f'distortion_probability={self.distortion_probability}, distortion_level={self.distortion_level}, ' \
               f'jitter_f={self.jitter_f}), filled_space_factor=({self._filled_space_factor_low}, {self._filled_space_factor_high})'

    @property
    def id(self):
        return self._id

    @property
    def capacity(self):
        return self._capacity

    @property
    def filled_space(self):
        queue = self.queue.values()
        if len(queue) == 0:
            queue_sum = 0
        else:
            queue_sum = sum([record['packet'].size for record in queue])
        awaiting = self.awaiting.values()
        if len(awaiting) == 0:
            awaiting_sum = 0
        else:
            awaiting_sum = sum([record['packet'].size for record in awaiting])
        # successful = self.successful.values()
        # if len(successful) == 0:
        #     successful_sum = 0
        # else:
        #     successful_sum = sum([p.size for p in successful])
        # return queue_sum + awaiting_sum + successful_sum
        return queue_sum + awaiting_sum

    @property
    def filled_space_relative(self):
        return round(self.filled_space / self.capacity, 4)

    @property
    def processing_speed(self):
        return self._processing_speed

    @property
    def filled_space_factor(self):
        return adds.filled_space_factor_formulae(n=self.filled_space_relative,
                                                 params={
                                                     'filled_space_factor_low': self._filled_space_factor_low,
                                                     'filled_space_factor_high': self._filled_space_factor_high,
                                                     'filled_space_factor_plateau': self._filled_space_factor_plateau,
                                                 })

    @property
    def distortion_probability(self):
        return self._distortion_probability

    @property
    def distortion_level(self):
        return self._distortion_level

    @property
    def jitter_f(self):
        return self._jitter_f

    @property
    def queue(self):  # -> OrderedDict[str, BasePacket]:
        return self._queue

    @property
    def awaiting(self):  # -> OrderedDict[str, BasePacket]:
        return self._awaiting

    @property
    def successful(self):  # -> OrderedDict[str, BasePacket]:
        return self._successful

    @property
    def incoming_channels(self):
        return dict({self.init_channel.id: self.init_channel}, **self._incoming_channels)

    @property
    def outgoing_channels(self):
        return self._outgoing_channels

    @property
    def outgoing_channels_is_empty(self):
        return sum([len(channel) for channel in self._outgoing_channels]) <= 0

    def add_to_queue(self,
                     pkt: BasePacket,
                     departure_time: float = None):
        if pkt is not None and departure_time is not None:
            self._queue.update({f'{pkt.sid}.{pkt.pid}.{pkt.id}': {
                    'packet': pkt,
                    'departure_time': departure_time,
                }})
        else:
            return -1

    def pop_from_queue(self, pkt: BasePacket):
        if pkt is not None:
            return self._queue.pop(f'{pkt.sid}.{pkt.pid}.{pkt.id}')
        else:
            return -1

    def add_to_awaiting(self,
                        pkt: BasePacket,
                        departure_time: float = None):
        if pkt is not None and departure_time is not None:
            self._awaiting.update({f'{pkt.sid}.{pkt.pid}.{pkt.id}': {
                    'packet': pkt,
                    'departure_time': departure_time,
                }})
        else:
            return -1

    def pop_from_awaiting(self, pkt: BasePacket):
        if pkt is not None:
            return self._awaiting.pop(f'{pkt.sid}.{pkt.pid}.{pkt.id}')
        else:
            return -1

    def add_to_successful(self,
                          pkt: BasePacket):
        if pkt is not None:
            self._successful.update({f'{pkt.sid}.{pkt.pid}.{pkt.id}': {
                    'packet': pkt,
                    'departure_time': float('inf'),
                }})
        else:
            return -1

    def pop_from_successful(self, pkt: BasePacket or None):
        if pkt is not None:
            return self._successful.pop(f'{pkt.sid}.{pkt.pid}.{pkt.id}')
        else:
            return -1

    def add_to_init_channel(self, pkt: BasePacket):
        if pkt is not None:
            self.init_channel.add_to_records(pkt, departure_time=pkt.delay)
        else:
            return -1

    def get_outgoing_channel(self, destination_node):
        outgoing_channel = self.outgoing_channels.get(f'{self.id}_{destination_node.id}', None)
        if outgoing_channel is None:
            raise Exception(f'Вершина {self.id} не имеет связи с {destination_node.id}')
        return outgoing_channel

    def flush(self):
        """
        Очистить очереди
        Returns
        -------

        """
        self._queue = OrderedDict({})
        self._awaiting = OrderedDict({})
        self._successful = OrderedDict({})


class TBLoadBasedNode(BaseNode):

    def __init__(self,
                 node_id: str,
                 capacity: float,
                 processing_speed: float,
                 distortion_probability: float,
                 distortion_level: int,
                 drop_threshold: float = 0.8,
                 **kwargs):

        super().__init__(node_id, capacity, processing_speed, distortion_probability, distortion_level, **kwargs)

        self.__drop_threshold = drop_threshold

    def __repr__(self):
        return f'BaseNode(id={self.id}, capacity={self.capacity} ({self.filled_space_relative * 100}% filled), processing_speed={self.processing_speed}, ' \
               f'drop_threshold={self.__drop_threshold}, distortion_probability={self.distortion_probability}, distortion_level={self.distortion_level}, ' \
               f'jitter_f={self.jitter_f}), filled_space_factor=({self._filled_space_factor_low}, {self._filled_space_factor_high})'

    @property
    def drop_threshold(self):
        return self.__drop_threshold

    def fit_to_capacity(self):
        if self.filled_space > self.capacity * self.drop_threshold and len(self.queue) > 1:
            # biggy = max(self.queue.items(), key=op.itemgetter(1))
            biggy = max(list(self.queue.items()), key=lambda x: x[1].size if not x[1].is_answer else -1)[1]
            if not biggy.is_answer:
                self.pop_from_queue(biggy)
                self.fit_to_capacity()
            else:
                return -1
        elif self.filled_space < self.capacity * self.drop_threshold:
            return None
        elif self.filled_space > self.capacity * self.drop_threshold and len(self.queue) == 0:
            return -1

    def add_to_queue(self, pkt: BasePacket):
        if pkt is not None:
            self._queue.update({f'{pkt.sid}.{pkt.pid}.{pkt.id}': pkt})
            self.fit_to_capacity()
        else:
            return -1

# class TBMessageBasedNode(BaseNode):
