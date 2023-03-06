import random
from collections import OrderedDict
from itertools import chain, compress
from typing import List
import operator as op

# from Nodes import BaseNode
# from NetworksReports import MaintenanceReport
from Packets import BasePacket
from Paths import PathCollection, Path
from Streams import BaseStream
import additions as adds
from config import BASIC_DROP_THRESHOLD


class Jitter:
    def __init__(self, low: float, high: float,
                 accuracy: int = 0):

        self.low = low
        self.high = high

        self._additional_power = accuracy

    def __repr__(self):
        return f'Jitter(low={self.low}, high={self.high}, accuracy={self._additional_power})'

    def __call__(self) -> float:
        return random.randrange(self._low, self._high)/self._order_multiplier

    @property
    def _order_multiplier(self):
        i = len(str(self.high).replace('.', ''))
        return 10**(i - 1 + self._additional_power)

    @property
    def _low(self):
        return int(self.low * self._order_multiplier)

    @property
    def _high(self):
        return int(self.high * self._order_multiplier)


class RandomJitter(Jitter):
    def __init__(self, lowest_low: float, highest_low: float,
                 lowest_high: float, highest_high: float,
                 accuracy: int = 2):

        if lowest_low > lowest_high:
            raise ValueError('Нижняя граница для генерации нижней границы джиттера не может быть больше, чем '
                             'нижняя граница для генерации верхней границы джиттера')

        if highest_low > highest_high:
            raise ValueError('Верхняя граница для генерации нижней границы джиттера не может быть больше, чем '
                             'верхняя граница для генерации верхней границы джиттера')

        self.lowest_low = lowest_low
        self.highest_low = highest_low
        self.lowest_high = lowest_high
        self.highest_high = highest_high

        self._additional_power = accuracy

        self._random_low = random.randrange(int(self.lowest_low * self._highest_low_order_multiplier),
                                int(self.highest_low * self._highest_low_order_multiplier)) \
               / self._highest_low_order_multiplier
        self._random_high = random.randrange(int(self.lowest_high * self._highest_high_order_multiplier),
                                int(self.highest_high * self._highest_high_order_multiplier)) \
               / self._highest_high_order_multiplier

        super().__init__(self._random_low, self._random_high)

    @property
    def _highest_low_order_multiplier(self):
        i = len(str(self.highest_low).replace('.', ''))
        return 10 ** (i - 1 + self._additional_power)

    @property
    def _highest_high_order_multiplier(self):
        i = len(str(self.highest_high).replace('.', ''))
        return 10 ** (i - 1 + self._additional_power)


class Traffic:
    def __init__(self, streams: List[BaseStream] = None):
        if streams is not None:
            self.__streams = streams
        else:
            self.__streams = []

        self.__id = str(id(self))

    @property
    def sender_nodes(self):
        return [s.sender for s in self.__streams]

    @property
    def receiver_nodes(self):
        return [s.receiver for s in self.__streams]

    @property
    def id(self):
        return self.__id

    def __len__(self):
        return len(self.__streams)

    def __getitem__(self, item):
        return self.__streams[item]

    def __repr__(self):
        return f'Traffic(streams={self.__streams})'

    def pop_packets(self):
        packets = [s.pop(0) for s in self.__streams]
        return list(compress(packets, packets))

    def empty(self):
        empty_streams_num = 0
        for s in self.__streams:
            empty_streams_num += 1 if len(s) == 0 else 0
        return empty_streams_num == len(self)

    def add_stream(self, stream: BaseStream):
        self.__streams.append(stream)

    def flush(self):
        self.__streams = []


class TrafficGenerator:
    def __init__(self,
                 params):
        self._message_paths_pool = params['message_paths_pool']
        self._messages_count = params['messages_count']
        self._senders_pool = params['senders_pool']
        self._receivers_pool = params['receivers_pool']
        self._packets_size = params['packets_size']
        self._protocols_pool = params['protocols_pool']
        self._start_timeouts_pool = params['start_timeouts_pool']
        self._k_pool = params['special'][' k_pool']




class TCPStreamData:
    def __init__(self,
                 stream: BaseStream,
                 path: Path,
                 reverse_path: Path):
        self.stream = stream
        self.id = stream.id
        self.path = path
        self.reverse_path = reverse_path
        self.packets_time_lastalive = {packet.id: 0 for packet in stream.packets} # id - уникальный идентификатор пакета как Python-объекта
                                                                        # здесь используется id, а не pid потому, что в
                                                                        # этом списке должны находится и копии некоторых
                                                                        # пакетов. Пакет и его копия различаются только параметром _copy_num и id
    def __repr__(self):
        return adds.Representation(self, ['id', 'packets_time'])()

class UDPStreamData:
    def __init__(self,
                 stream: BaseStream,
                 paths: PathCollection):
        self.stream = stream
        self.id = stream.id
        self.packets_paths = {packet.id: paths[i % len(paths)] for i, packet in enumerate(stream.packets)}
        self.packets_time_lastalive = {packet.id: 0 for packet in stream.packets}  # id - уникальный идентификатор пакета как Python-объекта
                                                                         # здесь используется id, а не pid потому, что в
                                                                         # этом списке должны находится и копии некоторых
                                                                         # пакетов. Пакет и его копия различаются только параметром _copy_num и id

    def __repr__(self):
        return adds.Representation(self, ['id', 'packets_time'])()


class Operator:
    def __init__(self):
        self.__streams_data = {}
        self._current_time = 0

    def __getitem__(self, key):
        return self.__streams_data.get(key, None)

    def __setitem__(self, key, value):
        self.__streams_data.update({key: value})

    def __repr__(self):
        packets = list(chain([[None if sd.stream.get_by_id(p_id) is None else sd.stream.get_by_id(p_id).id for p_id in sd.packets_time_lastalive] for sd in self.__streams_data.values()]))
        return f'Operator(streams_ids={list(self.__streams_data.keys())}, packets={packets})'

    def keys(self):
        return self.__streams_data.keys()

    def values(self):
        return self.__streams_data.values()

    # def __valid_packet(self, pkt: BasePacket):
    #     pkt_s_data = self[pkt.sid]
    #     if pkt_s_data is not None:
    #         pkt = pkt_s_data.stream.get_by_id(pkt.id)
    #     else:
    #         pkt = None
    #     return pkt is not None

    # TODO: На данный момент путь пакетов не изменяется на протяжении путешествия. 
    #  Реализовать новую функцию получения следующего узла адаптивным способом, 
    #  при котором расчет до точки назначения будет происходить каждый раз при поиске
    #  следующего узла и основываться на загруженности сети.
    def get_next_hop(self,
                     pkt: BasePacket,
                     current_node):
        # if not self.__valid_packet(pkt):
        #     raise Exception(f'Пакет {pkt.sid}.{pkt.pid} не принадлежит ни одному потоку, содержащемуся в оперативной памяти')

        if pkt.protocol == 'TCP' and pkt.is_answer:
            packet_path = self[pkt.sid].reverse_path
        elif pkt.protocol == 'TCP' and not pkt.is_answer:
            packet_path = self[pkt.sid].path
        else:
            packet_path = self[pkt.sid].packets_paths[pkt.id]

        if current_node.id not in packet_path:
            raise Exception(f'Вершины {current_node.id} нет в пути пакета {pkt.sid_pid}')
        else:

            current_node_i = None
            __i = 0
            while current_node_i == None and __i < len(packet_path):
                if packet_path[__i] == current_node.id:
                    current_node_i = __i
                else:
                    __i += 1

            next_node_i = current_node_i + 1
            if next_node_i < len(packet_path):
                return packet_path[next_node_i]
            else:
                return None

    def get_receiver(self,
                     pkt: BasePacket):
        # if not self.__valid_packet(pkt):
        #     raise Exception(f'Пакет {pkt.sid}.{pkt.pid} не принадлежит ни одному потоку, содержащемуся в оперативной памяти')
        # else:
        if pkt.protocol == 'TCP' and pkt.is_answer:
            packet_path = self[pkt.sid].reverse_path
        elif pkt.protocol == 'TCP' and not pkt.is_answer:
            packet_path = self[pkt.sid].path
        else:
            packet_path = self[pkt.sid].packets_paths[pkt.id]
        return packet_path[-1]

    def get_travel_time(self,
                        pkt: BasePacket):
        # if not self.__valid_packet(pkt):
        #     raise Exception(f'Пакет {pkt.sid}.{pkt.pid} не принадлежит ни одному потоку, содержащемуся в оперативной памяти')
        # else:
        return self[pkt.sid].packets_time_lastalive.get(pkt.id, None)

    def increment_travel_time(self,
                              pkt: BasePacket,
                              pkt_order: int,
                              current_node):
        # if not self.__valid_packet(pkt):
        #     print(f'Пакет {pkt.sid}.{pkt.pid} не принадлежит ни одному потоку, содержащемуся в оперативной памяти')
        # else:
        self[pkt.sid].packets_time[pkt.id] += adds.node_processing_packet_time(current_node, pkt, pkt_order)

    @staticmethod
    # TODO: Костыль, этот метод все таки должен быть в объекте вершины.
    def create_data_distortion(pkt: BasePacket,
                               current_node):

        if random.randint(0, 100) < current_node.distortion_probability:
            pkt.data = adds.information_distortion(pkt.data, dist_level=current_node.distortion_level)

    def flush(self):
        self.__streams_data = {}


class BaseReportAnalyzer:
    def __init__(self, report):
        self.report = report

    def _get_overfilled_nodes_ids(self):
        overfilled_nodes_stats = self.report.general_info['overfilled_nodes_stats']
        r = []
        for node_id, node_stat in overfilled_nodes_stats.items():
            if node_stat > 0:
                r.append(node_id)
        return r

    def _get_sorted_filled_nodes_ids(self):
        filled_nodes_stats = []
        for n in self.report.keys():
            filled_nodes_stats.append((n, self.report[n]['metrics']['filled_space_relative']['max']))
        r = OrderedDict()
        for node_id, node_stat in sorted(filled_nodes_stats, key=op.itemgetter(1), reverse=True):
                r.update({node_id: node_stat})
        return r

    def simple_analysis_single_node(self):
        opt_nodes = self._get_overfilled_nodes_ids()
        opt_nodes_stats = {}
        for node in opt_nodes:
            node_stats = {
                'drop_threshold': BASIC_DROP_THRESHOLD
            }
            opt_nodes_stats.update({node: node_stats})

        return opt_nodes_stats

    def simple_analysis_few_nodes(self, n: int):
        """
        Parameters
        ----------
        n - количество узлов для введения ведра

        Returns
        -------

        """
        opt_nodes = list(self._get_sorted_filled_nodes_ids().keys())[:n]
        opt_nodes_stats = {}
        for node in opt_nodes:
            node_stats = {
                'drop_threshold': BASIC_DROP_THRESHOLD
            }
            opt_nodes_stats.update({node: node_stats})

        return opt_nodes_stats

    def get_efforts_quality(self, base_report, report):
        ...





