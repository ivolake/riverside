import json
from collections import OrderedDict

from itertools import compress

import random
import operator as op
from typing import Tuple

from Graphs import BaseGraph
from NetworksSupport import Traffic, Operator, TCPStreamData, UDPStreamData
from NetworksReports import TrafficReport, MaintenanceReport
from Nodes import BaseNode, TBLoadBasedNode
from Packets import BasePacket
from Streams import BaseStream, TCPStream, UDPStream
from config import CAPACITY_LOWEST, CAPACITY_HIGHEST, PROCESSING_SPEED_LOWEST, PROCESSING_SPEED_HIGHEST, \
    DISTORTION_PROBABILITY_LOWEST, DISTORTION_PROBABILITY_HIGHEST, DISTORTION_LEVEL_LOWEST, DISTORTION_LEVEL_HIGHEST, \
    DROP_THRESHOLD


class BaseNetwork:
    def __init__(self, graph: BaseGraph):
        self.graph = graph
        self._options = self.graph.config.get('options').get('TN_options')
        self._id = str(id(self))


        self.TCP_timeout = self._options.get('TCP_timeout', 20)
        self.TCP_attempts_limit = self._options.get('TCP_attempts_limit', 5)

        self._init_nodes()

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
    def capacity(self):
        return sum([n.capacity for n in self._nodes.values()])

    @property
    def filled_space(self):
        return {nid: node.filled_space for nid, node in self._nodes.items()}

    @property
    def filled_space_avg(self):
        return round(sum(self.filled_space.values()) / len(self.filled_space), 4)

    @property
    def filled_space_relative(self):
        return {nid: node.filled_space_relative for nid, node in self._nodes.items()}

    @property
    def filled_space_relative_avg(self):
        return round(sum(self.filled_space_relative.values()) / len(self.filled_space_relative), 4)

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
            for pkt in node.queue.values():
                if pkt.id == pkt_id:
                    target_pkt = pkt
                    target_node = node
                    storage_name = 'queue'
            if target_pkt is None:
                for pkt in node.awaiting.values():
                    if pkt.id == pkt_id:
                        target_pkt = pkt
                        target_node = node
                        storage_name = 'awaiting'
            if target_pkt is None:
                for pkt in node.successful.values():
                    if pkt.id == pkt_id:
                        target_pkt = pkt
                        target_node = node
                        storage_name = 'successful'

        return target_pkt, target_node, storage_name

    def add_message_to_send(self,
                            message: str,
                            sender: str,
                            receiver: str,
                            protocol: str = 'UDP',
                            packet_size: int = None,
                            packet_tol: int = None,
                            special: dict = None):
        if protocol == 'TCP':
            self._traffic_to_send.add_stream(TCPStream(message=message,
                                                       sender=sender,
                                                       receiver=receiver,
                                                       packet_size=packet_size,
                                                       packet_tol=packet_tol,
                                                       special=special
                                                       ))
        elif protocol == 'UDP':
            self._traffic_to_send.add_stream(UDPStream(message=message,
                                                       sender=sender,
                                                       receiver=receiver,
                                                       packet_size=packet_size,
                                                       packet_tol=packet_tol,
                                                       special=special
                                                       ))
        else:
            raise Exception(f'Протокол {protocol} не является допустимым.')

    def send_messages(self, verbose: bool = False):
        if len(self._traffic_to_send) == 0:
            raise Exception('Нет сообщений для отправки. Воспользуйтесь методом add_message_to_send()')
        reports = self.start_traffic(self._traffic_to_send, verbose)
        self.flush()
        return reports

    def send_message(self,
                     message: str,
                     sender: str,
                     receiver: str,
                     protocol: str = 'UDP',
                     packet_size: int = None,
                     packet_tol: int = None,
                     special: dict = None,
                     verbose: bool = False):
        self.flush()

        self.add_message_to_send(message=message,
                                 sender=sender,
                                 receiver=receiver,
                                 protocol=protocol,
                                 packet_size=packet_size,
                                 packet_tol=packet_tol,
                                 special=special)

        return self.send_messages(verbose)

    def start_traffic(self, traffic: Traffic, verbose: bool = False) -> Tuple[TrafficReport, MaintenanceReport]:
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
                    print(f'{__i} {self.filled_space_relative}', end='\r')
                __i += 1

                all_messages_delivered = True
                # дальше при итерировании по вершинам этот флаг обернется в False, если хоть
                #  на какой-то вершине у какого-либо пакета ((receiver != название вершины) или (next_hop не пустой))

                if not traffic.empty():
                    popped_packets = traffic.pop_packets()
                    for packet in popped_packets:
                        packet_sender_id = packet.sender
                        packet_sender = self.nodes[packet_sender_id]
                        packet_sender.add_to_queue(packet) # добавление пакета в свой стартовый узел
                        self._operator[packet.sid].packets_time.update({packet.id: 0}) # добавление пакета в оперативную память для отслеживания времени его путешествия


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
                                                              node) # моделирование случайных повреждений данных

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
                                        self._operator[packet.sid].packets_time.update({moving_packet_copy.id: 0}) # добавление копии в оперативную память для отслеживания времени ее путешествия
                                        # self.operator[moving_packet_copy.sid].stream.packets.append(moving_packet_copy) # добавление копии в поток изначального пакета
                                        node.add_to_awaiting(moving_packet) # добавление пакета в список ожидания
                                        next_hop_node = self.nodes[self._operator.get_next_hop(moving_packet_copy, node)] # получение следующего узла
                                        next_hop_node.add_to_queue(moving_packet_copy) # перемещение копии пакета вперед по маршруту
                                        self._operator[moving_packet_copy.sid].packets_time[moving_packet_copy.id] += moving_packet_copy.size / self.graph.edges[(node.id, next_hop_node.id)] # просчет времени перемещения пакета-копии по каналу связи между узлами

                                    else: # есть предыдущий, и он еще ждет свой пакет-ответ
                                        self._operator[packet.sid].packets_time.update({packet.id: 0}) # тогда и этот пакет ждет. Но фактически он еще не начал двигаться, поэтому его отсчет времени еще не начался.
                                else:
                                    # передача в next_hop
                                    moving_packet = node.pop_from_queue(packet)  # забор пакета из текущего узла
                                    next_hop_node = self.nodes[self._operator.get_next_hop(moving_packet, node)]  # получение следующего узла
                                    next_hop_node.add_to_queue(moving_packet)  # перемещение пакета вперед по маршруту
                                    self._operator[moving_packet.sid].packets_time[moving_packet.id] += moving_packet.size / self.graph.edges[(node.id, next_hop_node.id)]  # просчет времени перемещения пакета по каналу связи между узлами

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
                                    self._operator[answer_packet.sid].packets_time.update({answer_packet.id: 0}) # добавление пакета-ответа в оперативную память для отслеживания времени ее путешествия
                            else:
                                # передача в next_hop
                                moving_packet = node.pop_from_queue(packet) # забор пакета из текущего узла
                                next_hop_node = self.nodes[self._operator.get_next_hop(moving_packet, node)] # получение следующего узла
                                next_hop_node.add_to_queue(moving_packet) # перемещение пакета вперед по маршруту
                                self._operator[moving_packet.sid].packets_time[moving_packet.id] += moving_packet.size / self.graph.edges[(node.id, next_hop_node.id)]  # просчет времени перемещения пакета по каналу связи между узлами
                        elif packet.protocol == 'UDP':
                            if packet.receiver == node.id:
                                moving_packet = node.pop_from_queue(packet)  # забор пакета из текущего узла
                                node.add_to_successful(moving_packet)
                            else:
                                # передача в next_hop
                                moving_packet = node.pop_from_queue(packet)  # забор пакета из текущего узла
                                next_hop_node = self.nodes[self._operator.get_next_hop(moving_packet, node)]  # получение следующего узла
                                next_hop_node.add_to_queue(moving_packet)  # перемещение пакета вперед по маршруту
                                self._operator[moving_packet.sid].packets_time[moving_packet.id] += moving_packet.size / self.graph.edges[(node.id, next_hop_node.id)]
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
                                    existing_copy_time = self._operator[packet.sid].packets_time[existing_copy_id]
                                    if packet.sending_attempts < self.TCP_attempts_limit:
                                        packet.sending_attempts += 1
                                        packet_copy = packet.copy()  # создание независимой копии
                                        self._operator[packet_copy.sid].packets_time.update({packet_copy.id: existing_copy_time}) # добавление копии в оперативную память для отслеживания времени ее путешествия. Так как было затрачено время на ожидание предыдущего раза, оно прибавляется ко времени нового.
                                        next_hop_node = self.nodes[self._operator.get_next_hop(packet_copy, node)]  # получение следующего узла
                                        next_hop_node.add_to_queue(packet_copy)  # перемещение копии пакета вперед по маршруту
                                        self._operator[packet_copy.sid].packets_time[packet_copy.id] += packet_copy.size / self.graph.edges[(node.id, next_hop_node.id)]
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
                        packet.pid: self._operator[packet.sid].packets_time[packet.id]
                    })


            for r in traffic_report.values():
                if r['received_packets'] is None:
                    r['received_packets'] = {}

                if r['received_data']['packets_time'] is None:
                    r['received_data']['packets_time'] = {}

            return traffic_report, maintenance_report
        finally:
            self._traffic_to_send.flush()





                    # Алгоритм работы TCP:
                    # 1) 1-й пакет (далее - информ-пакет) помещается в awaiting_list.
                    #    Копия 1-го пакета отправляется со стартовой вершины (из queue этой вершины).
                    # 2) Спустя какое-то время 1-й пакет доходит до конечной вершины и попадает в successful_list.
                    #    В конечной вершине формируется пакет-ответ, попадающий в queue этой вершины
                    # 4) Пакет-ответ начинает движение к стартовой вершине самого 1-го пакета.
                    # 5) Когда пакет-ответ доходит до стартовой вершины 1-го пакета, он помещается в awaiting_list
                    # 6) Если в awaiting_list присутствуют копия 1-го пакета и ответ на него, а также соблюдаются
                    #    условия по прибытию ответа (время и количество попыток) %возможно, проверять только время%,
                    #    то они оба удаляются и начинается процесс пердачи следующего пакета.
                    # 7) Если не выполняются, то пакет ответ удаляется. Количетсво попыток увеличивается, и если
                    #    количество попыток превышает допустимое количетсво - удаляется и сам пакет из awaiting_list.
                    #    **далее должна происходить симуляция недошедшего пакета - он должен удаляться с конечной вершины**
                    # 8) 2-й пакет начинает процесс отправки, когда из awaiting_list пропадает пакет, бывший перед ним.
                    #
                    #
                    #
                    #
                    #
                    #

                    # Info: перемещение пакетов происходит следующим образом:
                    #  1) Проверка выполнения условий для перемещения конкретно этого пакета
                    #  2) Если они выполнены, то его текущий next_hop запоминается в отдельную переменную.
                    #  3) Из self.operator подтягивается название (id) следующего (следующего после запомненного
                    #     next_hop) узла, которому становится равным next_hop пакета.
                    #  4) У пакета меняется travel_time на величину, равную сумме времени на обработку в текущем узле и
                    #     времени, которое будет затрачено на путь до следующего узла.
                    #  5) Пакет удаляется из очереди текущего узла и добавляется в очередь следующего.
                    #
                    # Проверка неотправленных пакетов в каждой вершине:
                    #
                    #  Если next_hop у какого-либо пакета не пустой, то all_messages_delivered = False
                    #  (У всех пакетов будет пустой next_hop, когда они все дойдут до своих оконечных узлов, где их next_hop будет очищен)
                    # <<<---------------------------
                    #
                    #  Сначала на Протокол: tcp или udp
                    #  Если tcp, то:
                    #   Для стартового узла (при переборе пакетов в узле идет сравнение со start_node):
                    #    Info: при отсылании пакетов со стартовой ноды они перемещаются в список ожидающих подтверждения прибытия (node.awaiting_dict)
                    #
                    #    Проверка пакетов флаг received_answer на пакете, который означает, что ответ на предыдущий пакет был получен.
                    #     Условие установки флага received_answer - наличие на одной и той же ноде пакета с определенным id и
                    #     флагом is_answer=False и пакета с is_answer=True и parent_id=id этого пакета
                    #    Если флаг received_answer=True, то:
                    #     Проверить, пришел ли вовремя ответ, сравнив travel_time пакета-ответа с self.TCP_timeout
                    #     Если ответ пришел вовремя (travel_time пакета-ответа < self.TCP_timeout) и (sending_attempts < self.TCP_attempts_limit), то
                    #      Переместить пакет на следующий узел (указан в заголовке этого пакета в параметре 'next_hop'). Пакет-ответ удалить.
                    #     Если ответ опоздал:
                    #      Увеличить sending_attempts на 1 и отослать предыдущий пакет заново на узел-receiver. Предыдущий
                    #      пакет лежит в node.awaiting_dict и остается там, пока не придет положительный ответ, либо не
                    #      истечет количество попыток. После истечения количества повторных попыток предыдущий пакет просто
                    #      удаляется и происходит отправка текущего пакета (путем установления received_answer в True).
                    #   Для промежуточного узла:
                    #    Просто передача в next_hop
                    #
                    #   Для оконечного узла (при переборе пакетов в узле идет сравнение со goal_node):
                    #    Проверка флага is_answer:
                    #     Если False:
                    #      Проверка на то, новый ли этот пакет на данном узле (непустой next_hop):
                    #       Если True:
                    #        Создать пакет-ответ о получении прибывшего пакета. Путь - такой же, как у прибывшего. Переместить пакет-ответ сразу в next_hop.
                    #        Сделать пустым next_hop у прибывшего пакета.
                    #       Если False:
                    #        Ничего не делать.
                    #     Если True:
                    #      Пакет перемещается next_hop (можно частично объединить с False-сценарием).
                    #      (Этот случай возможен, только если пакет-ответ был сгенерирован не здесь).
                    #
                    #  Если udp, то:
                    #
                    #   Для стартового узла (при переборе пакетов в узле идет сравнение со start_node):
                    #    Просто передача в next_hop
                    #
                    #
                    #
                    #
                    #   Для промежуточного узла:
                    #    Просто передача в next_hop
                    #
                    #
                    #
                    #
                    #   Для оконечного узла (при переборе пакетов в узле идет сравнение со goal_node):
                    #    Всем пакетам установить next_hop='', если у каких-то он еще не пустой
                    #
                    #
                    #
                    #
                    #
                    #
                    #
                    #
                    #
                    #
                    #
                    #
                    #

                    # TODO: ПРИ РЕАЛИЗАЦИИ АЛГОРИТМА ДЫРЯВОГО ВЕДРА НУЖНО УЧЕСТЬ, ЧТО ПАКЕТЫ-ОТВЕТЫ НЕ ДОЛЖНЫ ТЕРЯТЬСЯ
                    # TODO: ВРЕМЯ ОБРАБОТКИ ПАКЕТА НА УЗЛЕ ЗАВИСИТ ОТ ЕГО ПОЛОЖЕНИЯ В ОЧЕРЕДИ
                    # TODO: ОТЧЕТ О РАБОТЕ ПОИСКА ТОЧЕК УСТАНОВКИ ДЫРЯВЫХ ВЕДЕР СОДЕРЖИТ И ПАРАМЕТРЫ ТРАФИКА, ПРИ КОТОРЫХ ЭТИ ТОЧКИ НАДО ИСПОЛЬЗОВАТЬ

                # если в какой-то вершине ((у всех пакетов с каким-то sid пустой next_hop) и (у всех пакетов с каким-то sid receiver совпадает с именем вершины)), то
                #  обращаясь по этому sid, собрать у пакетов received message



        # for s in traffic:
        #     # s = TCPStream(start=start, goal=goal, message=message, packet_size=256)
        #
        #     start = s.start
        #     goal = s.goal
        #     path = self.check_and_find_path(s=s)
        #
        #     time = 0  # Вычисление, сколько сообщение будет идти до адресата
        #     received_message = ''  # Вычисление, каким сообщение дойдет до адресата
        #
        #     for node_name in path:

        # return result


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
