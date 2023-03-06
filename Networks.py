import os

import json
from collections import OrderedDict

from itertools import compress

import random
import operator as op
from typing import Tuple

from Channels import BaseChannel
from Graphs import BaseGraph
from NetworksSupport import Traffic, Operator, TCPStreamData, UDPStreamData
from NetworksReports import TrafficReport, MaintenanceReport
from Nodes import BaseNode, TBLoadBasedNode
from Packets import BasePacket
from Streams import BaseStream, TCPStream, UDPStream
from additions import node_processing_packet_time
from config import CAPACITY_LOWEST, CAPACITY_HIGHEST, PROCESSING_SPEED_LOWEST, PROCESSING_SPEED_HIGHEST, \
    DISTORTION_PROBABILITY_LOWEST, DISTORTION_PROBABILITY_HIGHEST, DISTORTION_LEVEL_LOWEST, DISTORTION_LEVEL_HIGHEST, \
    DROP_THRESHOLD, DEFAULT_CYCLE_TIME, DEFAULT_TCP_TIMEOUT, DEFAULT_TCP_ATTEMPTS_LIMIT
from general import read_message


class BaseNetwork:
    def __init__(self, graph: BaseGraph):
        self.graph = graph
        self._options = self.graph.config.get('options').get('TN_options')
        self._id = str(id(self))


        self.cycle_time = self._options.get('cycle_time', DEFAULT_CYCLE_TIME)

        self.TCP_timeout = self._options.get('TCP_timeout', DEFAULT_TCP_TIMEOUT)
        self.TCP_attempts_limit = self._options.get('TCP_attempts_limit', DEFAULT_TCP_ATTEMPTS_LIMIT)

        self._init_nodes()

        self._init_edges()

        self._traffic_to_send = Traffic()

        self._operator = Operator()

    def __getitem__(self, item):
        return self._nodes.get(item, None)

    def __len__(self):
        return len(self._nodes)

    def __repr__(self):
        return f'BaseNetwork(graph.type={self.graph.type}, graph.nodes={self.graph.nodes})'

    @property
    def id(self):
        return self._id

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    @property
    def capacity(self):
        return sum([n.capacity for n in self._nodes.values()])

    @property
    def nodes_filled_space(self):
        return {nid: node.filled_space for nid, node in self._nodes.items()}

    @property
    def nodes_filled_space_avg(self):
        return round(sum(self.nodes_filled_space.values()) / len(self.nodes_filled_space), 4)

    @property
    def nodes_filled_space_relative(self):
        return {nid: node.filled_space_relative for nid, node in self._nodes.items()}

    @property
    def edges_filled_space(self):
        return {eid: channel.filled_space for eid, channel in self._edges.items()}

    @property
    def nodes_filled_space_relative_avg(self):
        return round(sum(self.nodes_filled_space_relative.values()) / len(self.nodes_filled_space_relative), 4)

    def _init_nodes(self):
        self._nodes = {}
        nodes_params = self._options.get('nodes_params', None)
        if nodes_params is None:
            for n in self.graph.nodes:
                self._nodes.update({n: BaseNode(node_id=n,
                                                capacity=random.randrange(CAPACITY_LOWEST, CAPACITY_HIGHEST),
                                                processing_speed=random.randrange(PROCESSING_SPEED_LOWEST, PROCESSING_SPEED_HIGHEST),
                                                distortion_probability=random.randint(DISTORTION_PROBABILITY_LOWEST, DISTORTION_PROBABILITY_HIGHEST),
                                                distortion_level=random.randint(DISTORTION_LEVEL_LOWEST, DISTORTION_LEVEL_HIGHEST)
                                                )})
        else:
            nodes_params = {str(k): v for k, v in nodes_params.items()}
            for n in self.graph.nodes:
                self._nodes.update({n: BaseNode(node_id=n,
                                                capacity=nodes_params.get(n, {}).get('capacity',
                                                                                             random.randrange(CAPACITY_LOWEST,
                                                                                                              CAPACITY_HIGHEST)),
                                                processing_speed=nodes_params.get(n, {}).get('processing_speed',
                                                                                                     random.randrange(PROCESSING_SPEED_LOWEST,
                                                                                                                      PROCESSING_SPEED_HIGHEST)),
                                                distortion_probability=nodes_params.get(n, {}).get(
                                                            'distortion_probability', random.randint(DISTORTION_PROBABILITY_LOWEST,
                                                                                                     DISTORTION_PROBABILITY_HIGHEST)),
                                                distortion_level=nodes_params.get(n, {}).get('distortion_level',
                                                                                                     random.randint(DISTORTION_LEVEL_LOWEST,
                                                                                                                    DISTORTION_LEVEL_HIGHEST)),
                                                **nodes_params.get(n, {}).get('settings', {})
                                                )})


    def _init_edges(self):
        self._edges = {}
        for n in self.nodes:
            edge_id = f'_{n}'
            node_init_channel = BaseChannel(channel_id=edge_id,
                                            source=None,
                                            target=self.nodes[n],
                                            processing_speed=None,
                                            )
            self._edges.update({edge_id: node_init_channel})
            self.nodes[n].init_channel = node_init_channel

        graph_edges = self.graph.edges
        graph_edges = list(graph_edges.keys()) if isinstance(graph_edges, dict) else graph_edges
        for e in graph_edges:
            edge_id = f'{e[0]}_{e[1]}'
            channel = BaseChannel(channel_id=edge_id,
                                  source=self.nodes[e[0]],
                                  target=self.nodes[e[1]],
                                  processing_speed=self.graph.edges[e],
                                  )
            self._edges.update({edge_id: channel})
            self.nodes[e[1]]._incoming_channels.update({edge_id: channel})
            self.nodes[e[0]]._outgoing_channels.update({edge_id: channel})

    def cafap(self, s: BaseStream, reverse: bool = False):
        """
        Расшифровка - check and find all paths.
        Находит все возможные пути для этого потока.
        Parameters
        ----------
        reverse
        s

        Returns
        -------

        """
        if not reverse:
            paths = self.graph.calculate(start=s.sender, goal=s.receiver, mass=1, **s.special)  # поиск пути с помощью пакета Виртуального Вызова
        else:
            paths = self.graph.calculate(start=s.receiver, goal=s.sender, mass=1, **s.special)  # поиск пути с помощью пакета Виртуального Вызова

        if paths:
            paths.get_shortest()
        else:
            if not reverse:
                raise Exception(f'Между отправителем ({s.sender}) и получателем ({s.receiver}) не существует математически допустимых путей.')
            else:
                raise Exception(f'Между получателем ({s.receiver}) и отправителем ({s.sender}) (обратное направление) не существует математически допустимых путей.')

        return paths

    def cafapatcp(self, s: BaseStream, reverse: bool = False):
        """
        Расшифровка - check and find all paths according to capacity problems.
        Находит все возможные пути для этого потока, узлы на которых в состоянии пропустить хотя бы один пакет из потока.
        Parameters
        ----------
        reverse
        s

        Returns
        -------

        """
        if not reverse:
            paths = self.graph.calculate(start=s.sender, goal=s.receiver, mass=1, **s.special)  # поиск пути с помощью пакета Виртуального Вызова
        else:
            paths = self.graph.calculate(start=s.receiver, goal=s.sender, mass=1, **s.special)  # поиск пути с помощью пакета Виртуального Вызова

        if paths:
            paths.get_shortest()
        else:
            if not reverse:
                raise Exception(f'Между отправителем ({s.sender}) и получателем ({s.receiver}) не существует математически допустимых путей.')
            else:
                raise Exception(f'Между получателем ({s.receiver}) и отправителем ({s.sender}) (обратное направление) не существует математически допустимых путей.')


        paths_found = type(paths)([])  # создать инстанс такой же коллекции путей, что и была передана в paths
        for path in paths:
            path_bandwidth = min([self.nodes[v].capacity for v in path])

            capacity_problem = path_bandwidth < max(s.packets, key=op.attrgetter('size')).size

            if not capacity_problem:
                paths_found.append(path)

        if not paths_found:
            if not reverse:
                raise Exception('Между отправителем и получателем не существует путей с узлами, обладающими достаточной пропускной способнотью, чтобы пропустить хотя бы один пакет.')
            else:
                raise Exception('Между получателем и отправителем (обратный порядок) не существует путей с узлами, обладающими достаточной пропускной способнотью, чтобы пропустить хотя бы один пакет.')

        return paths_found

    def flush(self):
        self._traffic_to_send.flush()
        self._operator.flush()
        for node in self.nodes.values():
            node.flush()

    def find_packet_by_id(self,
                          pkt_id: str):
        target_pkt = None
        target_node = None
        storage_name = None

        i = 0
        nodes_names = list(self.nodes.keys())
        while target_pkt is None and i < len(nodes_names):
            node = self.nodes[nodes_names[i]]
            i += 1
            for pkt in (record['packet'] for record in node.queue.values()):
                if pkt.id == pkt_id:
                    target_pkt = pkt
                    target_node = node
                    storage_name = 'queue'
            if target_pkt is None:
                for pkt in (record['packet'] for record in node.awaiting.values()):
                    if pkt.id == pkt_id:
                        target_pkt = pkt
                        target_node = node
                        storage_name = 'awaiting'
            if target_pkt is None:
                for pkt in (record['packet'] for record in node.successful.values()):
                    if pkt.id == pkt_id:
                        target_pkt = pkt
                        target_node = node
                        storage_name = 'successful'

        return target_pkt, target_node, storage_name

    def add_message_to_send(self,
                            message: str,
                            sender: str,
                            receiver: str,
                            delay: float,
                            protocol: str = 'UDP',
                            packet_size: int = None,
                            packet_tol: int = None,
                            special: dict = None):
        if protocol == 'TCP':
            self._traffic_to_send.add_stream(TCPStream(message=message,
                                                       sender=sender,
                                                       receiver=receiver,
                                                       delay=delay,
                                                       packet_size=packet_size,
                                                       packet_tol=packet_tol,
                                                       special=special
                                                       ))
        elif protocol == 'UDP':
            self._traffic_to_send.add_stream(UDPStream(message=message,
                                                       sender=sender,
                                                       receiver=receiver,
                                                       delay=delay,
                                                       packet_size=packet_size,
                                                       packet_tol=packet_tol,
                                                       special=special
                                                       ))
        else:
            raise Exception(f'Протокол {protocol} не является допустимым.')

    def add_traffic_to_send(self,
                            traffic_params):
        for stream in traffic_params['streams'].values():
            self.add_message_to_send(message=read_message(path=stream['message_path']),
                                     sender=stream['sender'],
                                     receiver=stream['receiver'],
                                     delay=stream['delay'],
                                     packet_size=None if stream['packet_size'] == 'default' else int(stream['packet_size']),
                                     protocol=stream['protocol'],
                                     special=stream.get('special', {}))

    def send_messages(self,
                      mode: str = 'default',
                      verbose: bool = False):
        if len(self._traffic_to_send) == 0:
            raise Exception('Нет сообщений для отправки. Воспользуйтесь методом add_message_to_send()')
        if mode == 'no_time_sim': # старый режим, нет тактов работы сети
            reports = self.start_traffic_no_time_sim(self._traffic_to_send, verbose)
        elif mode == 'default':
            reports = self.start_traffic(self._traffic_to_send, verbose)
        else:
            raise Exception(f'Неизвестный mode: {mode}')
        self.flush()
        return reports

    def send_message(self,
                     message: str,
                     sender: str,
                     receiver: str,
                     delay: float,
                     protocol: str = 'UDP',
                     packet_size: int = None,
                     packet_tol: int = None,
                     special: dict = None,
                     mode: str = 'default',
                     verbose: bool = False):
        self.flush()

        self.add_message_to_send(message=message,
                                 sender=sender,
                                 receiver=receiver,
                                 protocol=protocol,
                                 packet_size=packet_size,
                                 packet_tol=packet_tol,
                                 delay=delay,
                                 special=special)

        return self.send_messages(mode=mode, verbose=verbose)

    def start_traffic(self, traffic: Traffic, verbose: bool = False) -> Tuple[TrafficReport, MaintenanceReport]:
        """
        Моделирование с временем такта сети.
        Parameters
        ----------
        traffic
        verbose

        Returns
        -------

        """
        try:
            if traffic.empty():
                raise Exception('Переданный объект трафика пуст (ни в одном из потоков нет пакетов)')

            traffic_report = TrafficReport(traffic)
            maintenance_report = MaintenanceReport(self)

            for i, s in enumerate(traffic):
                paths = self.cafapatcp(s=s)
                paths.sort_by_time()

                if s.protocol == 'TCP':
                    reverse_paths = self.cafapatcp(s=s, reverse=True)
                    self._operator[s.id] = TCPStreamData(stream=s,
                                                         path=paths.get_shortest(),
                                                         reverse_path=reverse_paths.get_shortest())
                elif s.protocol == 'UDP':
                    self._operator[s.id] = UDPStreamData(stream=s,
                                                         paths=paths)
                else:
                    raise Exception(f'Протокол {s.protocol} потока с id={s.id} не является допустимым.')

            all_messages_delivered = False
            current_time = -self.cycle_time

            while not all_messages_delivered:
                if verbose:
                    print(f'{current_time}', end='\r')  # , end='\r'
                    # print(f'{current_time} nodes: {self.nodes_filled_space_relative}', end='\r')  # , end='\r'
                    # print(f'{current_time} edges: {self.edges_filled_space}')

                all_messages_delivered = True
                # дальше при итерировании по вершинам этот флаг обернется в False, если хоть
                #  на какой-то вершине у какого-либо пакета ((receiver != название вершины) или (next_hop не пустой))

                if not traffic.empty():
                    popped_packets = traffic.pop_packets()
                    for packet in popped_packets:
                        packet_sender_id = packet.sender
                        packet_sender = self.nodes[packet_sender_id]
                        packet_sender.add_to_init_channel(packet)  # добавление пакета в инициализирующий канал своего узла
                        self._operator[packet.sid].packets_time_lastalive.update({packet.id: packet.delay})  # добавление пакета в оперативную память для отслеживания времени его путешествия


                current_time += self.cycle_time
                current_time = round(current_time, 6)

                for node in self.nodes.values():
                    if maintenance_report[node.id]['data_recorded']['filled_space'] is None:
                        maintenance_report[node.id]['data_recorded']['filled_space'] = []

                    maintenance_report[node.id]['data_recorded']['filled_space'].append(node.filled_space)

                    if all_messages_delivered and (
                            len(node.queue) > 0 or
                            len(node.awaiting) > 0 or
                            len(node.init_channel.records) > 0):
                        all_messages_delivered = False

                    for channel in node.incoming_channels.values():
                        channel_records_tmp = OrderedDict(zip(channel.records.keys(), channel.records.values()))
                        for packet_id, record in channel_records_tmp.items():
                            departure_time = record['departure_time']
                            if current_time >= departure_time:
                                packet = record['packet']
                                channel.pop_from_records(packet)

                                destination_node = channel.target
                                processing_time = node_processing_packet_time(destination_node, packet, len(destination_node.queue))
                                destination_node.add_to_queue(packet, current_time + processing_time)
                                self._operator[packet.sid].packets_time_lastalive.update({packet.id: current_time})

                    node_queue_tmp = OrderedDict(zip(node.queue.keys(), node.queue.values()))
                    for packet_order, packet_record in enumerate(node_queue_tmp.values()):
                        packet = packet_record['packet']
                        packet_departure_time = packet_record['departure_time']
                        if current_time > self._operator[packet.sid].packets_time_lastalive[packet.id]:
                            self._operator.create_data_distortion(packet, node)  # моделирование случайных повреждений данных
                            if packet.protocol == 'TCP':
                                if packet.sender == node.id:
                                    if not packet.is_answer:  # информ-пакет
                                        # проверка, есть ли перед ним уже ждущий очереди пакет ИЗ ЕГО ПОТОКА
                                        same_stream_awaiting_packets = [((packet.sid == answer_record['packet'].sid) and not answer_record['packet'].is_answer) for answer_record in node.awaiting.values()]  # получение списка информ-пакетов того же потока в очереди ожидания
                                        same_stream_awaiting_packets = list(compress(list(node.awaiting.values()), same_stream_awaiting_packets))
                                        if len(same_stream_awaiting_packets) <= 0:  # если нет, то можно отправлять этот пакет (предыдущий был отправлен или это первый)
                                            # передача в next_hop копии пакета
                                            node.pop_from_queue(packet)  # забор пакета из текущего узла
                                            self._operator[packet.sid].packets_time_lastalive[packet.id] = current_time
                                            packet.sending_attempts += 1  # сохранение данных о количестве попыток отправки
                                            packet_copy = packet.copy()  # создание независимой копии

                                            self._operator[packet.sid].packets_time_lastalive.update({packet_copy.id: current_time})  # добавление копии в оперативную память для отслеживания времени ее путешествия
                                            # self.operator[moving_packet_copy.sid].stream.packets.append(moving_packet_copy) # добавление копии в поток изначального пакета

                                            processing_time = node_processing_packet_time(node, packet_copy, len(node.awaiting))

                                            node.add_to_awaiting(packet_copy, current_time + processing_time)  # добавление пакета в список ожидания

                                            next_hop_node = self.nodes[self._operator.get_next_hop(packet_copy, node)]  # получение следующего узла
                                            channel_to_next_hop_node = node.get_outgoing_channel(next_hop_node)  # получение канала связи со следующим узлом
                                            travel_time_in_channel_to_next_hop_node = channel_to_next_hop_node.get_packet_travel_time(packet_copy)
                                            channel_to_next_hop_node.add_to_records(packet, current_time + processing_time + travel_time_in_channel_to_next_hop_node)  # добавление пакета в канал связи
                                        else:  # есть предыдущий, и он еще ждет свой пакет-ответ
                                            self._operator[packet.sid].packets_time_lastalive[packet.id] = current_time  # тогда и этот пакет ждет. Но фактически он еще не начал двигаться, поэтому его отсчет времени еще не начался.
                                    else:  # пакет-ответ
                                        # передача в next_hop
                                        node.pop_from_queue(packet)  # забор пакета из текущего узл
                                        next_hop_node = self.nodes[self._operator.get_next_hop(packet, node)]  # получение следующего узла
                                        channel_to_next_hop_node = node.get_outgoing_channel(next_hop_node)  # получение канала связи со следующим узлом
                                        processing_time = node_processing_packet_time(node, packet, len(node.queue))
                                        travel_time_in_channel_to_next_hop_node = channel_to_next_hop_node.get_packet_travel_time(packet)  # просчет времени перемещения пакета по каналу связи между узлами
                                        channel_to_next_hop_node.add_to_records(packet, current_time + processing_time + travel_time_in_channel_to_next_hop_node)  # добавление пакета в канал связи
                                        self._operator[packet.sid].packets_time_lastalive[packet.id] = current_time
                                elif packet.receiver == node.id:
                                    if packet.is_answer:
                                        # # тут было ветвление на на ситуацию с пустым некстхоп и непустым
                                        node.pop_from_queue(packet)
                                        node.add_to_awaiting(packet, packet_departure_time)  # перемещение пакета-ответа в список ожидания (departure time не меняется, так как пакет уже начал обрабатываться в главной очереди)
                                    else:
                                        node.pop_from_queue(packet)  # забор пакета из текущего узла
                                        node.add_to_successful(packet)  # перемещение в список успешно дошедших пакетов
                                        answer_packet = self._operator[packet.sid].stream.create_answer_to_packet(packet)  # создание пакета-ответа для packet
                                        # self.operator[moving_packet.sid].stream.packets.append(answer_packet) # добавление пакета-ответа в поток изначального пакета
                                        processing_time = node_processing_packet_time(node, answer_packet, len(node.queue))
                                        node.add_to_queue(answer_packet, current_time + processing_time)  # добавление пакета-ответа в очередь
                                        self._operator[answer_packet.sid].packets_time_lastalive.update({answer_packet.id: current_time})  # добавление пакета-ответа в оперативную память для отслеживания времени его путешествия
                                else:
                                    # передача в next_hop
                                    node.pop_from_queue(packet)  # забор пакета из текущего узла

                                    processing_time = node_processing_packet_time(node, packet, len(node.queue))
                                    next_hop_node = self.nodes[self._operator.get_next_hop(packet, node)]  # получение следующего узла
                                    channel_to_next_hop_node = node.get_outgoing_channel(next_hop_node)  # получение канала связи со следующим узлом
                                    travel_time_in_channel_to_next_hop_node = channel_to_next_hop_node.get_packet_travel_time(packet)  # просчет времени перемещения пакета по каналу связи между узлами
                                    channel_to_next_hop_node.add_to_records(packet, current_time + processing_time + travel_time_in_channel_to_next_hop_node)  # добавление пакета в канал связи
                                    self._operator[packet.sid].packets_time_lastalive[packet.id] = current_time
                            elif packet.protocol == 'UDP':
                                if packet.receiver == node.id:
                                    node.pop_from_queue(packet)  # забор пакета из текущего узла
                                    node.add_to_successful(packet)
                                else:
                                    # передача в next_hop
                                    node.pop_from_queue(packet)  # забор пакета из текущего узла

                                    processing_time = node_processing_packet_time(node, packet, len(node.queue))
                                    next_hop_node = self.nodes[self._operator.get_next_hop(packet, node)]  # получение следующего узла
                                    channel_to_next_hop_node = node.get_outgoing_channel(next_hop_node)  # получение канала связи со следующим узлом
                                    travel_time_in_channel_to_next_hop_node = channel_to_next_hop_node.get_packet_travel_time(packet)  # просчет времени перемещения пакета по каналу связи между узлами
                                    channel_to_next_hop_node.add_to_records(packet, current_time + processing_time + travel_time_in_channel_to_next_hop_node)  # добавление пакета в канал связи
                                    self._operator[packet.sid].packets_time_lastalive[packet.id] = current_time
                            else:
                                raise Exception(
                                    f'Протокол пакета (sid: {packet.sid}, id: {packet.id}) не распознан ({packet.protocol})')
                            # print(e)

                    node_awaiting_tmp = OrderedDict(zip(node.awaiting.keys(), node.awaiting.values()))
                    for packet_order, packet_record in enumerate(node_awaiting_tmp.values()):
                        packet = packet_record['packet']
                        if current_time > packet.delay or current_time > self._operator[packet.sid].packets_time_lastalive[packet.id]:
                            self._operator.create_data_distortion(packet, node)  # моделирование случайных повреждений данных

                            if not packet.is_answer:
                                answer = None
                                for search_packet in {record['packet'] for record in node.awaiting.values()} - {packet}:
                                    cond = search_packet.is_answer and search_packet.sid == packet.sid and search_packet.pid == packet.pid
                                    if answer is None and cond:
                                        answer = search_packet
                                if answer is not None:
                                    if self._operator.get_travel_time(packet) < self.TCP_timeout:
                                        node.pop_from_awaiting(packet)  # удаление информ-пакета из очереди ожидания
                                        node.pop_from_awaiting(answer)  # удаление пакета-ответа
                                    else:
                                        node.pop_from_awaiting(answer)  # удаление пакета-ответа из очереди ожидания
                                        existing_copy_id = packet.copy_id
                                        if packet.sending_attempts < self.TCP_attempts_limit:
                                            packet.sending_attempts += 1
                                            packet_copy = packet.copy()  # создание независимой копии
                                            processing_time = node_processing_packet_time(node, packet_copy, len(node.awaiting))
                                            next_hop_node = self.nodes[self._operator.get_next_hop(packet_copy, node)]  # получение следующего узла
                                            channel_to_next_hop_node = node.get_outgoing_channel(next_hop_node)  # получение канала связи со следующим узлом
                                            travel_time_in_channel_to_next_hop_node = channel_to_next_hop_node.get_packet_travel_time(packet_copy)  # просчет времени перемещения пакета по каналу связи между узлами
                                            channel_to_next_hop_node.add_to_records(packet_copy, current_time + processing_time + travel_time_in_channel_to_next_hop_node)  # добавление пакета в канал связи
                                            self._operator[packet_copy.sid].packets_time_lastalive.update({packet_copy.id: current_time})  # добавление копии в оперативную память для отслеживания времени ее путешествия. Так как было затрачено время на ожидание предыдущего раза, оно прибавляется ко времени нового.
                                        else:
                                            node.pop_from_awaiting(packet)  # удаление информ-пакета из очереди ожидания
                                            # таким образом, этот пакет остается не доставленным.

                                        packet_copy, packet_copy_node, packet_copy_node_storage = self.find_packet_by_id(existing_copy_id)
                                        if packet_copy is not None:
                                            packet_copy_node.pop_from_successful(packet_copy)  # симуляция "недоставленности" - удаление копии с конечной вершины (передается пакет, а удаляется по факту его копия)
                                        else:
                                            pass  # raise Exception('Копия пакета не была найдена. Обеспечивать недоставленность не удалось.')
                                else:
                                    ...  # информ-пакет продолжает ждать свой ответ

                for node in self.nodes.values():
                    maintenance_report[node.id]['data_recorded']['filled_space'].append(node.filled_space)

            # Все пакеты доставлены, начинается обработка доставленных пакетов и восстановление сообщений

            for node in self.nodes.values():
                for record in node.successful.values():
                    packet = record['packet']
                    if traffic_report[packet.sid]['received_packets'] is None:
                        traffic_report[packet.sid]['received_packets'] = {}

                    traffic_report[packet.sid]['received_packets'].update({
                        packet.pid: packet
                    })

                    if traffic_report[packet.sid]['received_data']['packets_time'] is None:
                        traffic_report[packet.sid]['received_data']['packets_time'] = {}

                    traffic_report[packet.sid]['received_data']['packets_time'].update({
                        packet.pid: self._operator[packet.sid].packets_time_lastalive[packet.id]
                    })

            for r in traffic_report.values():
                if r['received_packets'] is None:
                    r['received_packets'] = {}

                if r['received_data']['packets_time'] is None:
                    r['received_data']['packets_time'] = {}

            return traffic_report, maintenance_report
        finally:
            self._traffic_to_send.flush()

    def start_traffic_from_file(self, traffic_file_path: str, verbose: bool = False) -> Tuple[TrafficReport, MaintenanceReport]:
        ...

    def start_traffic_no_time_sim(self, traffic: Traffic, verbose: bool = False) -> Tuple[TrafficReport, MaintenanceReport]:
        try:
            if traffic.empty():
                raise Exception('Переданный объект трафика пуст (ни в одном из потоков нет пакетов)')

            traffic_report = TrafficReport(traffic)
            maintenance_report = MaintenanceReport(self)


            for i, s in enumerate(traffic):
                paths = self.cafapatcp(s=s)
                paths.sort_by_time()

                if s.protocol == 'TCP':
                    reverse_paths = self.cafapatcp(s=s, reverse=True)
                    self._operator[s.id] = TCPStreamData(stream=s,
                                                         path=paths.get_shortest(),
                                                         reverse_path=reverse_paths.get_shortest())
                elif s.protocol == 'UDP':
                    self._operator[s.id] = UDPStreamData(stream=s,
                                                         paths=paths)
                else:
                    raise Exception(f'Протокол {s.protocol} потока с id={s.id} не является допустимым.')



            all_messages_delivered = False
            __i = 0
            while not all_messages_delivered:
                if verbose:
                    print(f'{__i} {self.nodes_filled_space_relative}', end='\r')
                __i += 1

                all_messages_delivered = True
                # дальше при итерировании по вершинам этот флаг обернется в False, если хоть
                #  на какой-то вершине у какого-либо пакета ((receiver != название вершины) или (next_hop не пустой))

                if not traffic.empty():
                    popped_packets = traffic.pop_packets()
                    for packet in popped_packets:
                        packet_sender_id = packet.sender
                        packet_sender = self.nodes[packet_sender_id]
                        packet_sender.add_to_queue(packet)  # добавление пакета в свой стартовый узел
                        self._operator[packet.sid].packets_time_lastalive.update({packet.id: 0})  # добавление пакета в оперативную память для отслеживания времени его путешествия

                for node in self.nodes.values():
                    if maintenance_report[node.id]['data_recorded']['filled_space'] is None:
                        maintenance_report[node.id]['data_recorded']['filled_space'] = []

                    maintenance_report[node.id]['data_recorded']['filled_space'].append(node.filled_space)

                    if all_messages_delivered and (len(node.queue) > 0 or len(node.awaiting) > 0):
                        all_messages_delivered = False

                    node_queue_tmp = OrderedDict(zip(node.queue.keys(), node.queue.values()))
                    for packet_order, packet in enumerate(node_queue_tmp.values()):
                        self._operator.increment_travel_time(packet,
                                                             packet_order,
                                                             node)  # добавление времени обработки ко времени путешествия объекта (время обработки зависит от положения в очереди)
                        self._operator.create_data_distortion(packet,
                                                              node)  # моделирование случайных повреждений данных

                        if packet.protocol == 'TCP':
                            if packet.sender == node.id:
                                if not packet.is_answer:
                                    # проверка, есть ли перед ним уже ждущий очереди пакет ИЗ ЕГО ПОТОКА
                                    same_stream_awaiting_packets = [((packet.sid == a_packet.sid) and not a_packet.is_answer) for a_packet in node.awaiting.values()] # получение списка информ-пакетов того же потока в очереди ожидания
                                    same_stream_awaiting_packets = list(compress(list(node.awaiting.values()), same_stream_awaiting_packets))
                                    if len(same_stream_awaiting_packets) <= 0: # если нет, то можно отправлять этот пакет (предыдущий был отправлен или это первый)
                                        # передача в next_hop копии пакета
                                        moving_packet = node.pop_from_queue(packet) # забор пакета из текущего узла
                                        moving_packet.sending_attempts += 1 # сохранение данных о количестве попыток отправки
                                        moving_packet_copy = moving_packet.copy() # создание независимой копии
                                        self._operator[packet.sid].packets_time_lastalive.update({moving_packet_copy.id: 0}) # добавление копии в оперативную память для отслеживания времени ее путешествия
                                        # self.operator[moving_packet_copy.sid].stream.packets.append(moving_packet_copy) # добавление копии в поток изначального пакета
                                        node.add_to_awaiting(moving_packet) # добавление пакета в список ожидания
                                        next_hop_node = self.nodes[self._operator.get_next_hop(moving_packet_copy, node)] # получение следующего узла
                                        next_hop_node.add_to_queue(moving_packet_copy) # перемещение копии пакета вперед по маршруту
                                        self._operator[moving_packet_copy.sid].packets_time_lastalive[moving_packet_copy.id] += moving_packet_copy.size / self.graph.edges[(node.id, next_hop_node.id)] # просчет времени перемещения пакета-копии по каналу связи между узлами

                                    else: # есть предыдущий, и он еще ждет свой пакет-ответ
                                        self._operator[packet.sid].packets_time_lastalive.update({packet.id: 0}) # тогда и этот пакет ждет. Но фактически он еще не начал двигаться, поэтому его отсчет времени еще не начался.
                                else:
                                    # передача в next_hop
                                    moving_packet = node.pop_from_queue(packet)  # забор пакета из текущего узла
                                    next_hop_node = self.nodes[self._operator.get_next_hop(moving_packet, node)]  # получение следующего узла
                                    next_hop_node.add_to_queue(moving_packet)  # перемещение пакета вперед по маршруту
                                    self._operator[moving_packet.sid].packets_time_lastalive[moving_packet.id] += moving_packet.size / self.graph.edges[(node.id, next_hop_node.id)]  # просчет времени перемещения пакета по каналу связи между узлами

                            elif packet.receiver == node.id:
                                if packet.is_answer:
                                     # # тут было ветвление на на ситуацию с пустым некстхоп и непустым
                                    moving_packet = node.pop_from_queue(packet)  # забор пакета из текущего узла
                                    node.add_to_awaiting(moving_packet)  # перемещение пакета-ответа в список ожидания
                                else:
                                    moving_packet = node.pop_from_queue(packet)  # забор пакета из текущего узла
                                    node.add_to_successful(moving_packet) # перемещение в список успешно дошедших пакетов
                                    answer_packet = self._operator[moving_packet.sid].stream.create_answer_to_packet(moving_packet) # создание пакета-ответа для packet
                                    # self.operator[moving_packet.sid].stream.packets.append(answer_packet) # добавление пакета-ответа в поток изначального пакета
                                    node.add_to_queue(answer_packet) # добавление пакета-ответа в очередь
                                    self._operator[answer_packet.sid].packets_time_lastalive.update({answer_packet.id: 0}) # добавление пакета-ответа в оперативную память для отслеживания времени ее путешествия
                            else:
                                # передача в next_hop
                                moving_packet = node.pop_from_queue(packet) # забор пакета из текущего узла
                                next_hop_node = self.nodes[self._operator.get_next_hop(moving_packet, node)] # получение следующего узла
                                next_hop_node.add_to_queue(moving_packet) # перемещение пакета вперед по маршруту
                                self._operator[moving_packet.sid].packets_time_lastalive[moving_packet.id] += moving_packet.size / self.graph.edges[(node.id, next_hop_node.id)]  # просчет времени перемещения пакета по каналу связи между узлами
                        elif packet.protocol == 'UDP':
                            if packet.receiver == node.id:
                                moving_packet = node.pop_from_queue(packet)  # забор пакета из текущего узла
                                node.add_to_successful(moving_packet)
                            else:
                                # передача в next_hop
                                moving_packet = node.pop_from_queue(packet)  # забор пакета из текущего узла
                                next_hop_node = self.nodes[self._operator.get_next_hop(moving_packet, node)]  # получение следующего узла
                                next_hop_node.add_to_queue(moving_packet)  # перемещение пакета вперед по маршруту
                                self._operator[moving_packet.sid].packets_time_lastalive[moving_packet.id] += moving_packet.size / self.graph.edges[(node.id, next_hop_node.id)]
                        else:
                            raise Exception(f'Протокол пакета (sid: {packet.sid}, id: {packet.id}) не распознан ({packet.protocol})')
                            # print(e)

                    node_awaiting_tmp = OrderedDict(zip(node.awaiting.keys(), node.awaiting.values()))
                    for packet_order, packet in enumerate(node_awaiting_tmp.values()):
                        self._operator.increment_travel_time(packet,
                                                             packet_order,
                                                             node)  # добавление времени обработки ко времени путешествия объекта (время обработки зависит от положения в очереди)
                        self._operator.create_data_distortion(packet,
                                                              node) # моделирование случайных повреждений данных

                        if not packet.is_answer:
                            answer = None
                            for search_packet in set(node.awaiting.values()) - {packet}:
                                cond = search_packet.is_answer and search_packet.sid == packet.sid and search_packet.pid == packet.pid
                                if answer is None and cond:
                                    answer = search_packet
                            if answer is not None:
                                if self._operator.get_travel_time(packet) < self.TCP_timeout:
                                    node.pop_from_awaiting(packet) # удаление информ-пакета из очереди ожидания
                                    node.pop_from_awaiting(answer) # удаление пакета-ответа
                                else:
                                    node.pop_from_awaiting(answer)  # удаление пакета-ответа из очереди ожидания
                                    existing_copy_id = packet.copy_id
                                    existing_copy_time = self._operator[packet.sid].packets_time_lastalive[existing_copy_id]
                                    if packet.sending_attempts < self.TCP_attempts_limit:
                                        packet.sending_attempts += 1
                                        packet_copy = packet.copy()  # создание независимой копии
                                        self._operator[packet_copy.sid].packets_time_lastalive.update({packet_copy.id: existing_copy_time}) # добавление копии в оперативную память для отслеживания времени ее путешествия. Так как было затрачено время на ожидание предыдущего раза, оно прибавляется ко времени нового.
                                        next_hop_node = self.nodes[self._operator.get_next_hop(packet_copy, node)]  # получение следующего узла
                                        next_hop_node.add_to_queue(packet_copy)  # перемещение копии пакета вперед по маршруту
                                        self._operator[packet_copy.sid].packets_time_lastalive[packet_copy.id] += packet_copy.size / self.graph.edges[(node.id, next_hop_node.id)]
                                    else:
                                        node.pop_from_awaiting(packet)  # удаление информ-пакета из очереди ожидания
                                        # таким образом, этот пакет остается не доставленным.

                                    packet_copy, packet_copy_node, packet_copy_node_storage = self.find_packet_by_id(existing_copy_id)
                                    if packet_copy is not None:
                                        packet_copy_node.pop_from_successful(packet_copy) # симуляция "недоставленности" - удаление копии с конечной вершины (передается пакет, а удаляется по факту его копия)
                                    else:
                                        pass # raise Exception('Копия пакета не была найдена. Обеспечивать недоставленность не удалось.')
                            else:
                                ... # информ-пакет продолжает ждать свой ответ

            # Все пакеты доставлены, начинается обработка доставленных пакетов и восстановление сообщений

            for node in self.nodes.values():
                for packet in node.successful.values():
                    if traffic_report[packet.sid]['received_packets'] is None:
                        traffic_report[packet.sid]['received_packets'] = {}

                    traffic_report[packet.sid]['received_packets'].update({
                        packet.pid: packet
                    })

                    if traffic_report[packet.sid]['received_data']['packets_time'] is None:
                        traffic_report[packet.sid]['received_data']['packets_time'] = {}

                    traffic_report[packet.sid]['received_data']['packets_time'].update({
                        packet.pid: self._operator[packet.sid].packets_time_lastalive[packet.id]
                    })


            for r in traffic_report.values():
                if r['received_packets'] is None:
                    r['received_packets'] = {}

                if r['received_data']['packets_time'] is None:
                    r['received_data']['packets_time'] = {}

            return traffic_report, maintenance_report
        finally:
            self._traffic_to_send.flush()




class TBNetwork(BaseNetwork):

    def __init__(self, graph: BaseGraph, tb_params: dict):
        self._tb_params = tb_params
        super().__init__(graph)

    def __repr__(self):
        return f'TBNetwork(graph.type={self.graph.type}, graph.nodes={self.graph.nodes}, tb_nodes=[{list(self._tb_params.keys())}])'


    def _init_nodes(self):
        self._nodes = {}
        nodes_params = self._options.get('nodes_params', None)
        if nodes_params is None:
            for n in self.graph.nodes:
                if n in self._tb_params:
                    self._nodes.update({n: TBLoadBasedNode(node_id=n,
                                                           capacity=random.randrange(CAPACITY_LOWEST, CAPACITY_HIGHEST),
                                                           processing_speed=random.randrange(PROCESSING_SPEED_LOWEST, PROCESSING_SPEED_HIGHEST),
                                                           distortion_probability=random.randint(DISTORTION_PROBABILITY_LOWEST, DISTORTION_PROBABILITY_HIGHEST),
                                                           distortion_level=random.randint(DISTORTION_LEVEL_LOWEST, DISTORTION_LEVEL_HIGHEST),
                                                           drop_threshold=DROP_THRESHOLD
                                                           )})
                else:
                    self._nodes.update({n: BaseNode(node_id=n,
                                                    capacity=random.randrange(CAPACITY_LOWEST, CAPACITY_HIGHEST),
                                                    processing_speed=random.randrange(PROCESSING_SPEED_LOWEST, PROCESSING_SPEED_HIGHEST),
                                                    distortion_probability=random.randint(DISTORTION_PROBABILITY_LOWEST, DISTORTION_PROBABILITY_HIGHEST),
                                                    distortion_level=random.randint(DISTORTION_LEVEL_LOWEST, DISTORTION_LEVEL_HIGHEST)
                                                    )})
        else:
            nodes_params = {str(k): v for k, v in nodes_params.items()}
            for n in self.graph.nodes:
                if n in self._tb_params:
                    self._nodes.update({n: TBLoadBasedNode(node_id=n,
                                                           capacity=nodes_params.get(n, {}).get('capacity',
                                                                                                 random.randrange(CAPACITY_LOWEST,
                                                                                                                  CAPACITY_HIGHEST)),
                                                           processing_speed=nodes_params.get(n, {}).get('processing_speed',
                                                                                                         random.randrange(PROCESSING_SPEED_LOWEST,
                                                                                                                          PROCESSING_SPEED_HIGHEST)),
                                                           distortion_probability=nodes_params.get(n, {}).get(
                                                                'distortion_probability', random.randint(DISTORTION_PROBABILITY_LOWEST,
                                                                                                         DISTORTION_PROBABILITY_HIGHEST)),
                                                           distortion_level=nodes_params.get(n, {}).get('distortion_level',
                                                                                                         random.randint(DISTORTION_LEVEL_LOWEST,
                                                                                                                        DISTORTION_LEVEL_HIGHEST)),
                                                           drop_threshold=self._tb_params.get(n, {}).get('drop_threshold', DROP_THRESHOLD),
                                                           **nodes_params.get(n, {}).get('settings', {})
                                                           )})
                else:
                    self._nodes.update({n: BaseNode(node_id=n,
                                                    capacity=nodes_params.get(n, {}).get('capacity',
                                                                                          random.randrange(CAPACITY_LOWEST,
                                                                                                           CAPACITY_HIGHEST)),
                                                    processing_speed=nodes_params.get(n, {}).get('processing_speed',
                                                                                                  random.randrange(PROCESSING_SPEED_LOWEST,
                                                                                                                   PROCESSING_SPEED_HIGHEST)),
                                                    distortion_probability=nodes_params.get(n, {}).get(
                                                         'distortion_probability', random.randint(DISTORTION_PROBABILITY_LOWEST,
                                                                                                  DISTORTION_PROBABILITY_HIGHEST)),
                                                    distortion_level=nodes_params.get(n, {}).get('distortion_level',
                                                                                                  random.randint(DISTORTION_LEVEL_LOWEST,
                                                                                                                 DISTORTION_LEVEL_HIGHEST)),
                                                    **nodes_params.get(n, {}).get('settings', {})
                                                    )})
